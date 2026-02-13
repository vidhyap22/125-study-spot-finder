import { Brand } from "@/constants/theme";
import { RESERVATION_LINKS } from "@/utils/reservation-links";
import { FontAwesome6 } from "@expo/vector-icons";
import { useMemo } from "react";
import { Linking, Pressable, StyleSheet, Text, View } from "react-native";

type Environment = "indoors" | "outdoors";

export type SpaceRef = { id: string; title: string };

type Props = {
	backgroundColor?: string;

	title: string;
	capacity: number;
	techEnhanced?: boolean;
	environment: Environment;
	reservable: boolean;
	talkingAllowed: boolean;
	roomId: string;
	locationId: string;

	onPress?: () => void;

	// reservable flow: leaving app
	onReserveOpened?: (space: SpaceRef) => void;

	// public flow: choose in-app
	onChoosePublic?: (space: SpaceRef) => void;
};

export function StudySpaceRow({
	backgroundColor = "#FFFFFF",
	title,
	capacity,
	techEnhanced,
	environment,
	reservable,
	talkingAllowed,
	locationId,
	roomId,
	onPress,
	onReserveOpened,
	onChoosePublic,
}: Props) {
	const handleActionPress = async () => {
		const spaceRef: SpaceRef = { id: roomId, title };

		if (!reservable) {
			onChoosePublic?.(spaceRef);
			return;
		}

		const base = RESERVATION_LINKS[locationId];
		if (!base) {
			console.warn("No reservation link for location:", locationId);
			return;
		}

		const url = `${base}${roomId}`;
		const supported = await Linking.canOpenURL(url);

		if (!supported) {
			console.warn("Can't open URL:", url);
			return;
		}

		onReserveOpened?.(spaceRef);

		try {
			await Linking.openURL(url);
		} catch (e) {
			console.warn("Failed to open URL:", url, e);
		}
	};

	const metaText = useMemo(() => {
		const parts: string[] = [];
		if (talkingAllowed) parts.push("Talking Allowed");
		if (Number.isFinite(capacity)) parts.push(`Capacity ${capacity}`);
		if (techEnhanced) parts.push("Tech enhanced");
		parts.push(environment === "indoors" ? "Indoors" : "Outdoors");
		return parts.join(" • ");
	}, [capacity, techEnhanced, environment, talkingAllowed]);

	return (
		<View style={[styles.row, { backgroundColor }]}>
			<View style={styles.rowInner}>
				<View style={styles.textContainer}>
					<Text style={styles.title}>{title}</Text>
					<Text style={styles.meta}>{metaText}</Text>
				</View>

				<Pressable onPress={handleActionPress} style={({ pressed }) => [styles.rowIcon, pressed && styles.rowIconPressed]}>
					<FontAwesome6 name="calendar-plus" size={15} color={Brand.purple} />
				</Pressable>
			</View>
		</View>
	);
}

const styles = StyleSheet.create({
	row: {
		paddingHorizontal: 16,
		paddingVertical: 14,
		borderBottomWidth: StyleSheet.hairlineWidth,
		borderBottomColor: "#E5E7EB",
		overflow: "hidden",
	},
	rowInner: {
		flexDirection: "row",
		alignItems: "center",
	},
	textContainer: {
		flex: 1,
		paddingRight: 12,
	},
	title: {
		fontSize: 18,
		lineHeight: 22,
		fontWeight: "400",
		color: Brand.purple,
	},
	meta: {
		marginTop: 6,
		fontSize: 13,
		lineHeight: 16,
		color: "#6B7280",
	},
	rowIcon: {
		height: 40,
		width: 40,
		borderRadius: 20,
		alignItems: "center",
		justifyContent: "center",
		backgroundColor: "#9b4afe2e",
	},
	rowIconPressed: {
		backgroundColor: "#7c3aed33",
	},
});
