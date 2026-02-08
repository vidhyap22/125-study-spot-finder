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

    def enrich_and_store(self):
        # Load dimension tables from APP_DB (static info)
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

        # Load the 4 event tables from USER_DB (filtered by user_id)
        df_sessions = load_user_table("study_sessions")
        df_bookmarks = load_user_table("bookmarks")
        df_feedback = load_user_table("spot_feedback")
        df_views = load_user_table("spot_detail_views")

        # helper: enrich one event df
        def enrich(df_event: pd.DataFrame) -> pd.DataFrame:
            if df_event.empty:
                return df_event

            # normalize keys
            df_event = df_event.copy()
            df_event["study_space_id"] = df_event["study_space_id"].astype("int64")

            # merge spot info
            df = df_event.merge(df_spaces, on="study_space_id", how="left", suffixes=("", "_space"))

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
                df = df.merge(df_buildings, on="building_id", how="left", suffixes=("", "_bldg"))

            return df


        return (
            enrich(df_sessions),
            enrich(df_bookmarks),
            enrich(df_feedback),
            enrich(df_views),
        )

    def show_df(self, name, df, max_rows=10):
        print(f"\n===== {name} =====")
        print(f"shape: {df.shape}")
        print(df.head(max_rows).to_string(index=False))

    def visualization(self,df_sessions,df_bookmarks,df_feedback,df_views):
        self.show_df("study_sessions", df_sessions)
        self.show_df("bookmarks", df_bookmarks)
        self.show_df("spot_feedback", df_feedback)
        self.show_df("spot_detail_views", df_views)

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

        return {
            "event": event_name,
            "count": len(df),

            # NEW: how many times each building appears
            "building_counts": df["building_id"].value_counts().to_dict(),

            # averages
            "avg_capacity": df["capacity"].mean(),

            # percentages (mean of binary columns)
            "has_printer_pct": df["has_printer"].mean(),
            "is_indoor_pct": df["is_indoor"].mean(),
            "is_talking_allowed_pct": df["is_talking_allowed"].mean(),
            "tech_enhanced_pct": df["tech_enhanced"].mean(),
        }
    
    def collect_stats(self, df_sessions,df_bookmarks,df_feedback,df_views):
        stats = {
        "study_session": self.event_stats(df_sessions, "study_sessions"),
        "bookmarks": self.event_stats(df_bookmarks, "bookmarks"),
        "spot_feedback": self.event_stats(df_feedback, "spot_feedback"),
        "spot_detail_views": self.event_stats(df_views, "spot_detail_views"),
        }
        return stats
    
    def analyze_stats(self, event_stats_list):
        EVENT_WEIGHTS = {
        "study_sessions": 1.0,
        "bookmarks": 1.5,
        "spot_detail_views": 0.5,
        } 
        
        ATTRS = [
            "avg_capacity",
            "has_printer_pct",
            "is_indoor_pct",
            "is_talking_allowed_pct",
            "tech_enhanced_pct",
        ]

        weighted_sum = {a: 0.0 for a in ATTRS}
        total_weight = 0.0

        for stats in event_stats_list:
            event = stats["event"]
            w = EVENT_WEIGHTS.get(event)

            # skip events we don't care about
            if w is None:
                continue

            # skip empty / invalid stats
            if stats["count"] == 0:
                continue

            for a in ATTRS:
                val = stats.get(a)
                if val is not None:
                    weighted_sum[a] += w * val

            total_weight += w

        if total_weight == 0:
            return {a: None for a in ATTRS}

        return {a: weighted_sum[a] / total_weight for a in ATTRS}




if __name__ == "__main__":
    user1 = PersonalModel("USER_001", USER_DB, APP_DB)
    df_sessions, df_bookmarks, df_feedback, df_views = user1.enrich_and_store()
    #user1.visualization(df_sessions, df_bookmarks, df_feedback, df_views)
    event_stats=user1.collect_stats(df_sessions, df_bookmarks, df_feedback, df_views)
    average_preference = user1.analyze_stats([event_stats["study_session"], event_stats["bookmarks"], event_stats["spot_detail_views"]])
    print(average_preference)
