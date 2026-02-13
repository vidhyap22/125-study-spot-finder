import { ConfirmationModal } from "@/components/confirmation-modal";
import { SpaceRef, StudySpaceRow } from "@/components/space-results-row";
import { Brand } from "@/constants/theme";
import type { StudySpace } from "../utils/types";

import { useEffect, useRef, useState } from "react";
import { AppState, AppStateStatus, FlatList, Pressable, StyleSheet, Text, View } from "react-native";

export type SelectedSpotPayload = {
	locationId: string;
	locationTitle: string;
	spaceId: string;
	spaceTitle: string;
	kind: "reservable" | "public";
};

type Props = {
	locationTitle: string;
	locationId: string;
	spaceType: string;
	spaces: StudySpace[];
	onBack?: () => void;

	// parent receives a confirmed choice (public) or confirmed reservation (reservable)
	onChooseSpace?: (spot: SelectedSpotPayload) => void;
};

export function LocationSpacesList({ locationTitle, locationId, spaceType, spaces, onBack, onChooseSpace }: Props) {
	// 1) reservable flow: modal after returning from browser
	const [reservedModalVisible, setReservedModalVisible] = useState(false);
	const [reservedModalMessage, setReservedModalMessage] = useState("");

	const awaitingReturnRef = useRef(false);
	const pendingReserveSpaceRef = useRef<SpaceRef | null>(null);
	const lastReturnedReserveRef = useRef<SpaceRef | null>(null);

	// 2) public flow: modal immediately on press
	const [chooseModalVisible, setChooseModalVisible] = useState(false);
	const pendingChooseSpaceRef = useRef<SpaceRef | null>(null);

	useEffect(() => {
		const sub = AppState.addEventListener("change", (nextState: AppStateStatus) => {
			if (nextState === "active" && awaitingReturnRef.current) {
				awaitingReturnRef.current = false;

				const space = pendingReserveSpaceRef.current;
				pendingReserveSpaceRef.current = null;

				lastReturnedReserveRef.current = space;

				setReservedModalMessage(space ? `Did you reserve "${space.title}" at ${locationTitle}?` : `Did you reserve a space at ${locationTitle}?`);
				setReservedModalVisible(true);
			}
		});

		return () => sub.remove();
	}, [locationTitle]);

	const handleReserveOpened = (space: SpaceRef) => {
		awaitingReturnRef.current = true;
		pendingReserveSpaceRef.current = space;
	};

	const handleChoosePublic = (space: SpaceRef) => {
		pendingChooseSpaceRef.current = space;
		setChooseModalVisible(true);
	};

	return (
		<View style={styles.container}>
			{/* Header */}
			<View style={styles.headerRow}>
				{onBack ? (
					<Pressable
						onPress={onBack}
						android_ripple={{ color: "#E5E7EB" }}
						style={({ pressed }) => [styles.backButton, { opacity: pressed ? 0.7 : 1 }]}
					>
						<Text style={styles.backText}>‹ Back</Text>
					</Pressable>
				) : (
					<View style={styles.backButtonPlaceholder} />
				)}

				<View style={styles.titleContainer}>
					<Text style={styles.title} numberOfLines={1}>
						{locationTitle}
					</Text>
					<Text style={styles.subtitle} numberOfLines={1}>
						{spaceType}
					</Text>
				</View>

				<View style={styles.backButtonPlaceholder} />
			</View>

			<View style={styles.divider} />

			{/* Study Spaces */}
			<FlatList
				data={spaces}
				keyExtractor={(item) => item.id}
				renderItem={({ item }) => (
					<StudySpaceRow
						title={item.title}
						capacity={item.capacity}
						techEnhanced={item.techEnhanced}
						environment={item.environment}
						reservable={item.reservable}
						talkingAllowed={item.talkingAllowed}
						roomId={item.id}
						locationId={locationId}
						onReserveOpened={handleReserveOpened}
						onChoosePublic={handleChoosePublic}
					/>
				)}
				showsVerticalScrollIndicator={false}
			/>

			{/* Reservable flow: ask after returning from browser */}
			<ConfirmationModal
				visible={reservedModalVisible}
				message={reservedModalMessage}
				onClose={() => {
					setReservedModalVisible(false);
					lastReturnedReserveRef.current = null;
				}}
				onConfirmation={() => {
					const space = lastReturnedReserveRef.current;
					lastReturnedReserveRef.current = null;
					setReservedModalVisible(false);

					if (space) {
						onChooseSpace?.({
							locationId,
							locationTitle,
							spaceId: space.id,
							spaceTitle: space.title,
							kind: "reservable",
						});
					}
				}}
			/>

			{/* Public flow: ask immediately */}
			<ConfirmationModal
				visible={chooseModalVisible}
				message={
					pendingChooseSpaceRef.current
						? `Confirm studying at "${pendingChooseSpaceRef.current.title}"?`
						: `Confirm studying at this space at ${locationTitle}?`
				}
				onClose={() => {
					setChooseModalVisible(false);
					pendingChooseSpaceRef.current = null;
				}}
				onConfirmation={() => {
					const space = pendingChooseSpaceRef.current;
					pendingChooseSpaceRef.current = null;
					setChooseModalVisible(false);

					if (space) {
						onChooseSpace?.({
							locationId,
							locationTitle,
							spaceId: space.id,
							spaceTitle: space.title,
							kind: "public",
						});
					}
				}}
			/>
		</View>
	);
}

const styles = StyleSheet.create({
	container: {
		backgroundColor: "#FFFFFF",
		borderTopLeftRadius: 22,
		borderTopRightRadius: 22,
		paddingTop: 10,
		flex: 1,
	},
	headerRow: {
		flexDirection: "row",
		alignItems: "center",
		paddingHorizontal: 14,
	},
	backButton: {
		paddingHorizontal: 10,
		paddingVertical: 8,
		borderRadius: 10,
		overflow: "hidden",
	},
	backText: {
		fontSize: 16,
		color: Brand.purple,
	},
	backButtonPlaceholder: {
		width: 70,
	},
	titleContainer: {
		flexDirection: "column",
		alignSelf: "center",
		flex: 1,
		alignItems: "center",
	},
	title: {
		textAlign: "center",
		fontSize: 20,
		fontWeight: "600",
		color: "#232324",
		paddingHorizontal: 8,
	},
	subtitle: {
		marginTop: 4,
		fontSize: 13,
		lineHeight: 16,
		color: "#6B7280",
		textAlign: "center",
	},
	divider: {
		height: StyleSheet.hairlineWidth,
		backgroundColor: "#E5E7EB",
		marginTop: 10,
	},
});
