import React, { useMemo } from "react";
import { View, Text, StyleSheet, Pressable } from "react-native";

import { Brand } from "@/constants/theme";

type Environment = "indoors" | "outdoors";

type Props = {
	backgroundColor?: string;

	title: string;
	capacity: number;
	techEnhanced?: boolean;
	environment: Environment;
	reservable: boolean;

	onPress?: () => void;
};

export function StudySpaceRow({ backgroundColor = "#FFFFFF", title, capacity, techEnhanced, environment, reservable, onPress }: Props) {
	const metaText = useMemo(() => {
		const parts: string[] = [];
		// Reservable
		// if (reservable) parts.push("Reservable");
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
		<>
			<Text style={styles.title} numberOfLines={1}>
				{title}
			</Text>

			<Text style={styles.meta} numberOfLines={1}>
				{metaText}
			</Text>
		</>
	);

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
				{content}
			</Pressable>
		);
	}

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
});
