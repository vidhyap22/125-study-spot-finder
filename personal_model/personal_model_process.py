from datetime import date
import math
import sqlite3
from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
USER_DB = BASE_DIR / "data" / "database" / "user_data.db"
APP_DB = BASE_DIR / "data" / "database" / "app.db"


class PersonalModel():
    def __init__(self, user_id, USER_DB=USER_DB, APP_DB=APP_DB):
        self.user_id = user_id
        self.USER_DB = USER_DB
        self.APP_DB = APP_DB

        #joint table with more information
        self.df_sessions, self.df_bookmarks, self.df_feedback, self.df_views, self.df_searchfilters = self.enrich_and_store()

        #basic statistic on event
        self.event_stats=self.collect_stats(self.df_sessions, self.df_bookmarks, self.df_feedback, self.df_views, self.df_searchfilters)

        #reserved_hour
        self.hours = self.reserve_hours()

    def reserve_hours(self):
        df = self.df_sessions
        today = date.today().isoformat()
        hours = (
            df[(df["start_date"] == today) & (df["must_reserve"] == 1)]
            ["duration_ms"]
            .sum() / 3_600_000
        )
        return hours

    def enrich_and_store(self):
        # load dimension tables from APP_DB (static info)
        with sqlite3.connect(self.APP_DB) as conn:
            df_spaces = pd.read_sql_query("SELECT * FROM study_spaces;", conn)
            df_buildings = pd.read_sql_query("SELECT * FROM buildings;", conn)

        df_spaces["study_space_id"] = df_spaces["study_space_id"].astype("int64")
        df_spaces["building_id"] = df_spaces["building_id"].astype("string")
        df_buildings["building_id"] = df_buildings["building_id"].astype("string")

        # helper to load per-user event table from USER_DB
        def load_user_table(table_name: str) -> pd.DataFrame:
            with sqlite3.connect(self.USER_DB) as conn:
                return pd.read_sql_query(
                    f"SELECT * FROM {table_name} WHERE user_id = ?;",
                    conn,
                    params=(self.user_id,)
                )

        # load the 4 event tables from USER_DB (filtered by user_id)
        df_sessions = load_user_table("study_sessions")
        df_bookmarks = load_user_table("bookmarks")
        df_feedback = load_user_table("spot_feedback")
        df_views = load_user_table("spot_detail_views")
        df_search = load_user_table("search_filters")

        # helper: enrich one event df
        def enrich(df_event: pd.DataFrame) -> pd.DataFrame:
            df = df_event.copy()

            # if study_space_id is missing entirely, cannot enrich
            if "study_space_id" not in df.columns:
                return df

            # normalize key type even if df is empty
            df["study_space_id"] = df["study_space_id"].astype("int64")
            df_spaces_local = df_spaces.copy()
            df_spaces_local["study_space_id"] = df_spaces_local["study_space_id"].astype("int64")

            # merge spot info
            df = df.merge(df_spaces_local, on="study_space_id", how="left", suffixes=("", "_space"))

            # resolve building_id if both exist
            if "building_id_space" in df.columns:
                if "building_id" in df.columns:
                    df["building_id"] = df["building_id"].astype("string")
                    df["building_id_space"] = df["building_id_space"].astype("string")
                    df["building_id"] = df["building_id"].fillna(df["building_id_space"])
                    df = df.drop(columns=["building_id_space"])
                else:
                    df = df.rename(columns={"building_id_space": "building_id"})

            # merge building info
            if "building_id" in df.columns:
                df["building_id"] = df["building_id"].astype("string")
                df_buildings_local = df_buildings.copy()
                df_buildings_local["building_id"] = df_buildings_local["building_id"].astype("string")
                df = df.merge(df_buildings_local, on="building_id", how="left", suffixes=("", "_bldg"))

            return df

        return (
            enrich(df_sessions),
            enrich(df_bookmarks),
            enrich(df_feedback),
            enrich(df_views),
            df_search,
        )

    def show_df(self, name, df, max_rows=10):
        print(f"\n===== {name} =====")
        print(f"shape: {df.shape}")
        print(df.head(max_rows).to_string(index=False))

    def visualization(self):
        self.show_df("study_sessions", self.df_sessions)
        self.show_df("bookmarks", self.df_bookmarks)
        self.show_df("spot_feedback", self.df_feedback)
        self.show_df("spot_detail_views", self.df_views)
        self.show_df("search_filters", self.df_searchfilters)

    def event_stats(self, df, event_name):
        if df.empty:
            return {
                "event": event_name,
                "count": 0,
                "avg_capacity": None,
                "has_printer_pct": None,
                "is_indoor_pct": None,
                "is_talking_allowed_pct": None,
                "tech_enhanced_pct": None,
                "building_counts": {},  
            }
        if event_name == "study_sessions":
            return {
                "event": event_name,
                "count": len(df),

                # how many times each building appears
                "building_counts": df["building_id"].value_counts().to_dict(),

                # capacity information
                "avg_capacity": df["capacity"].mean(),
                "min_capacity": df["capacity"].min(),
                "max_capacity": df["capacity"].max(),


                # percentages (mean of binary columns)
                "has_printer_pct": df["has_printer"].mean(),
                "is_indoor_pct": df["is_indoor"].mean(),
                "is_talking_allowed_pct": df["is_talking_allowed"].mean(),
                "tech_enhanced_pct": df["tech_enhanced"].mean(),
                #average session traffic
                "session_traffic": df["session_traffic"].mean(),
                "must_reserve_pct": df['must_reserve'].mean()
            }
        elif event_name == "search_filters":
            return {
                    "event": event_name,
                    "count": len(df),

                    # capacity information
                    "avg_capacity": df[["min_capacity", "max_capacity"]].mean(),
                    "min_capacity": df["min_capacity"].min(),
                    "max_capacity": df["max_capacity"].max(),


                    # percentages (mean of binary columns)
                    "has_printer_pct": df["has_printer"].mean(),
                    "is_indoor_pct": df["is_indoor"].mean(),
                    "is_talking_allowed_pct": df["is_talking_allowed"].mean(),
                    "tech_enhanced_pct": df["tech_enhanced"].mean(),
                }
        else:
            return {
                "event": event_name,
                "count": len(df),

                # how many times each building appears
                "building_counts": df["building_id"].value_counts().to_dict(),

                # averages
                "avg_capacity": df["capacity"].mean(),
                "min_capacity": df["capacity"].min(),
                "max_capacity": df["capacity"].max(),

                # percentages (mean of binary columns)
                "has_printer_pct": df["has_printer"].mean(),
                "is_indoor_pct": df["is_indoor"].mean(),
                "is_talking_allowed_pct": df["is_talking_allowed"].mean(),
                "tech_enhanced_pct": df["tech_enhanced"].mean(),
                "must_reserve_pct": df['must_reserve'].mean()
            }
    
    def collect_stats(self, df_sessions,df_bookmarks,df_feedback,df_views, df_search_filters):
        stats = {
        "study_session": self.event_stats(df_sessions, "study_sessions"),
        "bookmarks": self.event_stats(df_bookmarks, "bookmarks"),
        "spot_feedback": self.event_stats(df_feedback, "spot_feedback"),
        "spot_detail_views": self.event_stats(df_views, "spot_detail_views"),
        "search_filters": self.event_stats(df_search_filters, "search_filters")
        }
        return stats
    

    def analyze_stats(self, event_stats_list):
        EVENT_WEIGHTS = {
        "study_sessions": 1.0,
        "bookmarks": 1.5,
        "spot_detail_views": 0.5,
        "search_filters": 0.5,
        }

        ATTRS = [
            "avg_capacity",
            "min_capacity",
            "max_capacity",
            "has_printer_pct",
            "is_indoor_pct",
            "is_talking_allowed_pct",
            "tech_enhanced_pct",
            "must_reserve_pct"
        ]

        DEFAULTS = {
            "avg_capacity": 100.5,
            "min_capacity": 1,
            "max_capacity": 200,
            "has_printer_pct": 0.5,
            "is_indoor_pct": 0.5,
            "is_talking_allowed_pct": 0.5,
            "tech_enhanced_pct": 0.5,
            "must_reserve_pct": 0.5
        }

        weighted_sum = {a: 0.0 for a in ATTRS}
        total_weight = 0.0
        average_traffic = None

        for stats in event_stats_list:
            event = stats.get("event")
            w = EVENT_WEIGHTS.get(event)
            if w is None:
                continue

            if event == "study_sessions":
                average_traffic = stats.get("session_traffic")

            if stats.get("count", 0) == 0:
                continue

            for a in ATTRS:
                val = stats.get(a)
                if val is not None and not (isinstance(val, float) and math.isnan(val)):
                    weighted_sum[a] += w * val

            total_weight += w

        result = {}

        # cold start case
        if total_weight == 0:
            result = DEFAULTS.copy()
        else:
            for a in ATTRS:
                value = weighted_sum[a] / total_weight
                if isinstance(value, float) and math.isnan(value):
                    result[a] = DEFAULTS[a]
                else:
                    result[a] = value

        # handle traffic default
        result["library_traffic"] = 0.5 if average_traffic is None else average_traffic
        result["can_reserve_room"] = 1 if  total_weight == 0 or self.hours <= 2 and result.get("must_reserve_pct") > 0.5 else 0
        return result

    def user_preference(self, average_preference):
        preference = {}

        min_capacity = average_preference.get("min_capacity")
        max_capacity = average_preference.get("max_capacity")

        preference["min_capacity"] = math.floor(min_capacity) if min_capacity is not None else None
        preference["max_capacity"] = math.ceil(max_capacity) if max_capacity is not None else None

        indoor_pct = average_preference.get("is_indoor_pct")
        preference["is_indoor"] = (
            0 if indoor_pct is not None and indoor_pct < 0.5
            else 1 if indoor_pct is not None
            else None
        )

        talking_pct = average_preference.get("is_talking_allowed_pct")
        preference["is_talking_allowed"] = (
            0 if talking_pct is not None and talking_pct < 0.5
            else 1 if talking_pct is not None
            else None
        )

        library_traffic = average_preference.get("library_traffic")
        if library_traffic is not None:
            preference["library_traffic_range"] = (
                max(0, library_traffic - 0.2),
                min(1, library_traffic + 0.2),
            )
        else:
            preference["library_traffic_range"] = None

        printer_pct = average_preference.get("has_printer_pct")
        preference["has_printer"] = (
            0 if printer_pct is not None and printer_pct < 0.5
            else 1 if printer_pct is not None
            else None
        )
        preference['must_reserve'] = (
            0 if self.hours >= 2 or average_preference.get("must_reserve_pct") < 0.5
            else 1
        )
        return preference

    def room_history(self, df_sessions):
        history = {
            "building_counts": df_sessions["building_id"].value_counts().to_dict(),
            "study_spot_count": df_sessions["study_space_id"].value_counts().to_dict()
        }
        return history
    
    def low_rating_spot(self, df_feedback):
        below_3 = df_feedback[df_feedback["rating"] < 3]
        return below_3['study_space_id'].values.tolist() 
    
    def bookmarks_room(self, df_bookmarks):
        df_sorted = df_bookmarks.sort_values(by="created_at", ascending=False)
        return df_sorted['study_space_id'].values.tolist() 
    
    def user_context_for_ranking(self):
        #dictionary return for the ranking
        """
        filter preference include capacity range, indoor outdoor preference, is talking allowed, library traffic rang, and has printer or not
        """
        #self.visualization()

        #average_preference
        self.average_preference = self.analyze_stats([self.event_stats["study_session"], self.event_stats["bookmarks"], self.event_stats["spot_detail_views"], self.event_stats["search_filters"]])
        #print("="*50)
        #print("average preference statisic: ", self.average_preference)

        #preference used for filter
        self.filter_preference = self.user_preference(self.average_preference)
        #print("="*50)
        #print("preference used for recommendation: ", self.filter_preference)
        
        #history of room and building
        self.history=self.room_history(self.df_sessions)
        #print("="*50)
        #print("user history: ", self.history)

        #can be used to filter out low rating spot
        self.low_rating = self.low_rating_spot(self.df_feedback)
        #print("="*50)
        #print("low rating study spot: ", self.low_rating)

        #return the bookmarked spot
        self.bookmarks_spots = self.bookmarks_room(self.df_bookmarks)
        #print("="*50)
        #print("bookmarks: ", self.bookmarks_spots)
        
        self.user_context = {
            "event_stats": self.event_stats,
            "average_preference": self.average_preference,
            "preference": self.filter_preference,
            "history": self.history,
            "low_rating_rooms": self.low_rating,
            "bookmarks": self.bookmarks_spots,
        }
        return self.user_context

    def filter_out_low_rating_spot(self, spots):
        """
        can be useful for ranking -- when given a list of spots, it filters out the ones with rating < 3 in the feedback
        """
        for spot in spots:
            if spot in self.low_rating:
                spots.remove(spot)
        return spots
    
    def build_marginal_pref(self, df, attrs, alpha=1.0):
        """
        returns:
        {
            attr: {value: probability}
        }
        """
        pref = {}

        if df is None or df.empty:
            return {a: {} for a in attrs}

        n = len(df)

        for a in attrs:
            counts = df[a].value_counts(dropna=False).to_dict()

            # Laplace smoothing
            k = len(counts)
            dist = {}
            for val, c in counts.items():
                dist[val] = (c + alpha) / (n + alpha * k)

            pref[a] = dist
        return pref
    
    def score_spot_condition(self, pref, spot_condition, attr_weights=None):
        num, den = 0.0, 0.0

        for attr, val in spot_condition.items():
            if attr not in pref:
                continue

            dist = pref[attr]
            if not dist:
                continue

            p = dist.get(val, 0.0) 

            w = 1.0 if attr_weights is None else attr_weights.get(attr, 1.0)

            num += w * p
            den += w

        return num / den if den > 0 else 0.0
            
    def probability(self, spots):
        #given a list of spot_id, return the probability that the user will like the spot in descending order
        results = []
        spots = self.filter_out_low_rating_spot(spots)

        # cold-start check
        if self.df_sessions.empty and self.df_bookmarks.empty and self.df_views.empty:
            return [(spot, 0.5) for spot in spots]

        attrs = [
            "must_reserve", "tech_enhanced", "capacity",
            "is_indoor", "is_talking_allowed", "has_printer"
        ]

        pref_sessions  = self.build_marginal_pref(self.df_sessions, attrs)
        pref_bookmarks = self.build_marginal_pref(self.df_bookmarks, attrs)
        pref_views     = self.build_marginal_pref(self.df_views, attrs)

        for spot in spots:
            with sqlite3.connect(self.APP_DB) as conn:
                query = """
                    SELECT s.must_reserve, s.tech_enhanced, s.capacity,
                        s.is_indoor, s.is_talking_allowed, b.has_printer
                    FROM study_spaces s
                    JOIN buildings b
                    ON s.building_id = b.building_id
                    WHERE s.study_space_id = ?
                """
                df = pd.read_sql_query(query, conn, params=(spot,))
                spot_condition = df.iloc[0].to_dict()

            s_score = self.score_spot_condition(pref_sessions, spot_condition)
            b_score = self.score_spot_condition(pref_bookmarks, spot_condition)
            v_score = self.score_spot_condition(pref_views, spot_condition)

            final_score = (1.0*s_score + 1.5*b_score + 0.5*v_score) / (1.0 + 1.5 + 0.5)

            results.append((spot, final_score))

        results.sort(key=lambda x: x[1], reverse=True)
        return results
                

    



if __name__ == "__main__":
    user1 = PersonalModel("USER_001", USER_DB, APP_DB)
    user1.user_context_for_ranking()
    result = user1.probability([44672, 34681, 10, 11, 12, 34680, 44700])
    print(result)