// LocationDetailsPanel.tsx (updated: adds a back button callback)
import React from "react";
import { View, Text, StyleSheet, FlatList, Pressable } from "react-native";

import { Brand } from "@/constants/theme";
import { StudySpaceRow } from "@/components/space-results-row";
import type { StudySpace } from "./types";

type Props = {
	locationTitle: string;
	spaceType: string;
	spaces: StudySpace[];
	onBack?: () => void;
};

export function LocationDetailsPanel({ locationTitle, spaceType, spaces, onBack }: Props) {
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
						onPress={() => console.log("Tapped space:", item.id)}
					/>
				)}
				showsVerticalScrollIndicator={false}
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
		width: 70, // keeps title centered when back button exists
	},
	title: {
		// flex: 1,
		textAlign: "center",
		fontSize: 20,
		fontWeight: "600",
		color: "#000",
		paddingHorizontal: 8,
	},
	subtitle: {
		marginTop: 4,
		fontSize: 13,
		lineHeight: 16,
		color: "#6B7280",
		textAlign: "center",
	},
	titleContainer: {
		display: "flex",
		flexDirection: "column",
		textAlign: "center",
		alignSelf: "center",
		flex: 1,
	},
	divider: {
		height: StyleSheet.hairlineWidth,
		backgroundColor: "#E5E7EB",
		marginTop: 10,
	},
});
