import { BookmarkRow, SpaceRef } from "@/components/bookmark-row";
import { ConfirmationModal } from "@/components/confirmation-modal";
import type { StudySpace } from "@/utils/types";
import { useEffect, useRef, useState } from "react";
import { AppState, AppStateStatus, FlatList, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

export type SelectedSpotPayload = {
	locationId: string;
	locationTitle: string;
	spaceId: string;
	spaceTitle: string;
	kind: "reservable" | "public";
};

type Props = {
	bookmarks: StudySpace[];
	onChooseSpace?: (spot: SelectedSpotPayload) => void;
};
export default function BookmarksListScreen({ bookmarks = [], onChooseSpace }: Props) {
	const count = bookmarks.length;
	// Reservable flow
	const [reservedModalVisible, setReservedModalVisible] = useState(false);
	const [reservedModalMessage, setReservedModalMessage] = useState("");

	const awaitingReturnRef = useRef(false);

	const pendingReserveRef = useRef<{
		space: SpaceRef;
		locationId: string;
		locationTitle: string;
	} | null>(null);

	const lastReturnedReserveRef = useRef<{
		space: SpaceRef;
		locationId: string;
		locationTitle: string;
	} | null>(null);

	// Public flow
	const [chooseModalVisible, setChooseModalVisible] = useState(false);

	const pendingChooseRef = useRef<{
		space: SpaceRef;
		locationId: string;
		locationTitle: string;
	} | null>(null);

	/**
	 * Detect when user returns from browser reservation page
	 */
	useEffect(() => {
		const sub = AppState.addEventListener("change", (nextState: AppStateStatus) => {
			if (nextState === "active" && awaitingReturnRef.current) {
				awaitingReturnRef.current = false;

				const payload = pendingReserveRef.current;
				pendingReserveRef.current = null;
				lastReturnedReserveRef.current = payload;

				setReservedModalMessage(payload ? `Did you reserve "${payload.space.title}" at ${payload.locationTitle}?` : "Did you reserve the space?");

				setReservedModalVisible(true);
			}
		});

		return () => sub.remove();
	}, []);

	const handleReserveOpened = (space: SpaceRef, locationId: string, locationTitle: string) => {
		awaitingReturnRef.current = true;
		pendingReserveRef.current = { space, locationId, locationTitle };
	};

	const handleChoosePublic = (space: SpaceRef, locationId: string, locationTitle: string) => {
		pendingChooseRef.current = { space, locationId, locationTitle };
		setChooseModalVisible(true);
	};

	return (
		<SafeAreaView style={styles.container} edges={["top"]}>
			<FlatList
				data={bookmarks}
				keyExtractor={(item) => item.id}
				showsVerticalScrollIndicator={false}
				contentContainerStyle={{ paddingBottom: 40 }}
				ListHeaderComponent={
					<View style={styles.header}>
						<Text style={styles.title}>Bookmarks</Text>
						<Text style={styles.subtitle}>{count} saved</Text>
						<View style={styles.divider} />
					</View>
				}
				renderItem={({ item }) => (
					<BookmarkRow
						title={item.title}
						capacity={item.capacity}
						techEnhanced={item.techEnhanced}
						environment={item.environment}
						reservable={item.reservable}
						talkingAllowed={item.talkingAllowed}
						roomId={item.id}
						locationId={item.locationId}
						locationTitle={item.locationName}
						onReserveOpened={(space) => handleReserveOpened(space, item.locationId, item.locationName)}
						onChoosePublic={(space) => handleChoosePublic(space, item.locationId, item.locationName)}
					/>
				)}
				ListEmptyComponent={
					<View style={styles.emptyWrap}>
						<Text style={styles.emptyTitle}>No bookmarks yet</Text>
						<Text style={styles.emptySub}>Save a study space and it’ll show up here.</Text>
					</View>
				}
			/>

			{/* Reservable confirmation */}
			<ConfirmationModal
				visible={reservedModalVisible}
				message={reservedModalMessage}
				onClose={() => {
					setReservedModalVisible(false);
					lastReturnedReserveRef.current = null;
				}}
				onConfirmation={() => {
					const payload = lastReturnedReserveRef.current;
					lastReturnedReserveRef.current = null;
					setReservedModalVisible(false);

					if (!payload) return;

					onChooseSpace?.({
						locationId: payload.locationId,
						locationTitle: payload.locationTitle,
						spaceId: payload.space.id,
						spaceTitle: payload.space.title,
						kind: "reservable",
					});
				}}
			/>

			{/* Public confirmation */}
			<ConfirmationModal
				visible={chooseModalVisible}
				message={pendingChooseRef.current ? `Confirm studying at "${pendingChooseRef.current.space.title}"?` : "Confirm studying at this space?"}
				onClose={() => {
					setChooseModalVisible(false);
					pendingChooseRef.current = null;
				}}
				onConfirmation={() => {
					const payload = pendingChooseRef.current;
					pendingChooseRef.current = null;
					setChooseModalVisible(false);

					if (!payload) return;

					onChooseSpace?.({
						locationId: payload.locationId,
						locationTitle: payload.locationTitle,
						spaceId: payload.space.id,
						spaceTitle: payload.space.title,
						kind: "public",
					});
				}}
			/>
		</SafeAreaView>
	);
}

const styles = StyleSheet.create({
	container: {
		flex: 1,
		backgroundColor: "#FFFFFF",
		paddingHorizontal: 16,
	},

	header: {
		paddingTop: 18,
		paddingBottom: 12,
		alignItems: "center",
	},

	title: {
		fontSize: 28,
		fontWeight: "600",
		color: "#232324",
	},

	subtitle: {
		marginTop: 4,
		fontSize: 13,
		color: "#6B7280",
	},

	divider: {
		marginTop: 16,
		height: StyleSheet.hairlineWidth,
		backgroundColor: "#E5E7EB",
		width: "100%",
	},

	emptyWrap: {
		marginTop: 60,
		alignItems: "center",
	},

	emptyTitle: {
		fontSize: 18,
		fontWeight: "700",
		color: "#111827",
	},

	emptySub: {
		marginTop: 8,
		fontSize: 13,
		color: "#6B7280",
		textAlign: "center",
	},
});
