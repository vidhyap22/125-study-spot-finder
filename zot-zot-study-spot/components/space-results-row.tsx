import React, { useMemo } from "react";
import { View, Text, StyleSheet, Pressable } from "react-native";
import { FontAwesome6 } from "@expo/vector-icons";
import { Brand } from "@/constants/theme";
import { Linking } from "react-native";
import { RESERVATION_LINKS } from "@/components/reservation-links";

type Environment = "indoors" | "outdoors";

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
}: Props) {
	const handleReservePress = async () => {
		const base = RESERVATION_LINKS[locationId];

		if (!base) {
			console.warn("No reservation link for location:", locationId);
			return;
		}

		const url = `${base}${roomId}`;

		const supported = await Linking.canOpenURL(url);

		if (supported) {
			await Linking.openURL(url);
		} else {
			console.warn("Can't open URL:", url);
		}
	};

	const metaText = useMemo(() => {
		const parts: string[] = [];
		// Talking Allowed
		if (talkingAllowed) parts.push("Talking Allowed");
		// Capacity
		if (Number.isFinite(capacity)) parts.push(`Capacity ${capacity}`);

		// Tech enhanced
		if (techEnhanced) parts.push("Tech enhanced");

		// Environment (only one allowed)
		if (environment === "indoors") parts.push("Indoors");
		else parts.push("Outdoors");

		return parts.join(" • ");
	}, [capacity, techEnhanced, environment]);

	const content = (
		<View style={styles.rowInner}>
			<View style={styles.textContainer}>
				<Text style={styles.title}>{title}</Text>

				<Text style={styles.meta}>{metaText}</Text>
			</View>

			{reservable && (
				<Pressable onPress={handleReservePress} style={({ pressed }) => [styles.rowIcon, pressed && styles.rowIconPressed]}>
					<FontAwesome6 name="calendar-plus" size={15} color={Brand.purple} />
				</Pressable>
			)}
		</View>
	);

	return <View style={[styles.row, { backgroundColor }]}>{content}</View>;
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
