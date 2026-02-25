import BookmarksListScreen, { SelectedSpotPayload } from "@/components/bookmarks-list-screen";
import { useSession } from "@/context/session-context";
import { apiGetBookmarkedSpaces } from "@/utils/api-client";
import type { StudySpace } from "@/utils/types";
import { useCallback, useMemo, useState } from "react";
import { StyleSheet, Text, View } from "react-native";
import { useFocusEffect } from "expo-router";

export default function BookmarksTab() {
	const { setSelectedSpot } = useSession();

	const [bookmarks, setBookmarks] = useState<StudySpace[]>([]);
	const [loading, setLoading] = useState(true);
	const [refreshing, setRefreshing] = useState(false);
	const [error, setError] = useState<string | null>(null);

	const normalize = useCallback((rows: any[]): StudySpace[] => {
		return (rows ?? []).map((x: any) => ({
			id: String(x.id ?? x.study_space_id ?? ""),
			title: String(x.title ?? x.name ?? ""),
			capacity: Number(x.capacity ?? 0),
			reservable: !!(x.reservable ?? x.must_reserve),
			techEnhanced: x.techEnhanced != null ? !!x.techEnhanced : x.tech_enhanced != null ? !!x.tech_enhanced : undefined,
			environment: (x.environment ?? ((x.indoor ?? x.is_indoor) ? "indoors" : "outdoors")) as "indoors" | "outdoors",
			talkingAllowed: x.talkingAllowed != null ? !!x.talkingAllowed : x.is_talking_allowed != null ? !!x.is_talking_allowed : !!x.talking_allowed,
			locationId: String(x.locationId ?? x.building_id ?? ""),
			locationName: String(x.locationName ?? x.building_name ?? ""),
		}));
	}, []);

	const loadBookmarks = useCallback(async () => {
		setError(null);

		const res = await apiGetBookmarkedSpaces({ user_id: "1", debug: false });

		if (!res.success) {
			setBookmarks([]);
			setError(res.error);
			return;
		}

		setBookmarks(normalize(res.data ?? []));
	}, [normalize]);

	useFocusEffect(
		useCallback(() => {
			let cancelled = false;

			(async () => {
				setLoading(true);
				await loadBookmarks();
				if (!cancelled) setLoading(false);
			})();

			return () => {
				cancelled = true;
			};
		}, [loadBookmarks]),
	);

	const onRefresh = useCallback(async () => {
		setRefreshing(true);
		await loadBookmarks();
		setRefreshing(false);
	}, [loadBookmarks]);

	const handleChooseSpace = (spot: SelectedSpotPayload) => {
		setSelectedSpot(spot);
		console.log("Selected spot for session:", spot);
	};

	const busy = useMemo(() => refreshing || loading, [refreshing, loading]);

	return (
		<View style={styles.screen}>
			{error ? <Text style={styles.error}>Failed to load bookmarks: {error}</Text> : null}

			<BookmarksListScreen bookmarks={bookmarks} onChooseSpace={handleChooseSpace} refreshing={busy} onRefresh={onRefresh} />
		</View>
	);
}

const styles = StyleSheet.create({
	screen: { flex: 1, backgroundColor: "#FFFFFF" },
	error: {
		paddingHorizontal: 16,
		paddingTop: 10,
		paddingBottom: 6,
		color: "#B91C1C",
		fontWeight: "700",
	},
});
