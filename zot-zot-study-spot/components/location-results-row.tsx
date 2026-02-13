import { useMemo } from "react";
import { Pressable, StyleSheet, Text } from "react-native";

import { Brand, Colors } from "@/constants/theme";

const theme = Colors.light;
type Props = {
	backgroundColor?: string;

	title: string;
	distanceText: string; // e.g. "0.4 mi" or "700 ft"
	printerAvailable?: boolean;

	isIndoors?: boolean;
	isOutdoors?: boolean;

	onPress?: () => void;
};

export function LocationResultsRow({ backgroundColor = "#FFFFFF", title, distanceText, printerAvailable, isIndoors, isOutdoors, onPress }: Props) {
	// Build the "meta" pills/segments like: "0.4 mi • Printer available • Indoors"
	const metaText = useMemo(() => {
		const parts: string[] = [];

		if (distanceText?.trim()) parts.push(distanceText.trim());
		if (printerAvailable) parts.push("Printer available");

		const envParts: string[] = [];
		if (isIndoors) envParts.push("Indoors");
		if (isOutdoors) envParts.push("Outdoors");
		if (envParts.length) parts.push(envParts.join(" / "));

		return parts.join(" • ");
	}, [distanceText, printerAvailable, isIndoors, isOutdoors]);

	if (onPress) {
		return (
			<Pressable
				onPress={onPress}
				android_ripple={{ color: "#E5E7EB" }}
				style={({ pressed }) => [
					styles.row,
					{
						backgroundColor: pressed ? "#f8eeff" : backgroundColor,
					},
				]}
			>
				<Text style={styles.title} numberOfLines={1}>
					{title}
				</Text>

				<Text style={styles.meta} numberOfLines={1}>
					{metaText}
				</Text>
			</Pressable>
		);
	}
}

const styles = StyleSheet.create({
	row: {
		paddingHorizontal: 16,
		paddingVertical: 14,

		// Google-maps-like separators
		borderBottomWidth: StyleSheet.hairlineWidth,
		borderBottomColor: "#E5E7EB", // light gray
		overflow: "hidden",
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
		color: "#6B7280", // gray
	},
});
