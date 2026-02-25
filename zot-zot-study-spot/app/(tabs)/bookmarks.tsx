import BookmarksListScreen, { SelectedSpotPayload } from "@/components/bookmarks-list-screen";
import { useSession } from "@/context/session-context";
import type { StudySpace } from "@/utils/types";
import { useState } from "react";
import { StyleSheet, View } from "react-native";

export default function BookmarksTab() {
	const { setSelectedSpot } = useSession();

	const [bookmarks] = useState<StudySpace[]>([
		{
			id: "44696",
			title: "Langson 380",
			capacity: 6,
			reservable: true,
			techEnhanced: false,
			locationId: "LLIB",
			environment: "indoors",
			talkingAllowed: true,
			locationName: "Langson Library",
		},
		{
			id: "LLIB-4th",
			title: "Langson 4th floor",
			capacity: 6,
			reservable: false,
			techEnhanced: false,
			locationId: "LLIB",
			environment: "indoors",
			talkingAllowed: true,
			locationName: "Langson Library",
		},
	]);

	const handleChooseSpace = (spot: SelectedSpotPayload) => {
		setSelectedSpot(spot);
		console.log("Selected spot for session:", spot);
	};

	return (
		<View style={styles.screen}>
			<BookmarksListScreen bookmarks={bookmarks} onChooseSpace={handleChooseSpace} />
		</View>
	);
}

const styles = StyleSheet.create({
	screen: { flex: 1, backgroundColor: "#FFFFFF" },
});
