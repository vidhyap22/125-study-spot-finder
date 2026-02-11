import React from "react";
import { View, Text, StyleSheet, Pressable } from "react-native";
import { Brand } from "@/constants/theme";
import { FontAwesome6 } from "@expo/vector-icons";
import { Image } from "expo-image";
import { LOCATION_IMAGES } from "@/components/location-images";

type Props = {
	locationTitle: string;
	locationId: string;
	onBack?: () => void;
	onSelectReservable: () => void;
	onSelectPublic: () => void;
};

export function SpaceTypePanel({ locationTitle, locationId, onBack, onSelectReservable, onSelectPublic }: Props) {
	const imageSource = LOCATION_IMAGES[locationId];
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

				<Text style={styles.title} numberOfLines={1}>
					{locationTitle}
				</Text>

				<View style={styles.backButtonPlaceholder} />
			</View>

			<View style={styles.divider} />
			{imageSource && (
				<Image source={imageSource} style={{ margin: 5, width: "95%", aspectRatio: 1.5, alignSelf: "center", borderRadius: 12 }} contentFit="cover" />
			)}
			{/* Options */}
			<Pressable
				onPress={onSelectReservable}
				android_ripple={{ color: "#E5E7EB" }}
				style={({ pressed }) => [styles.row, { backgroundColor: pressed ? "#f8eeff" : "#FFFFFF" }]}
			>
				<View style={styles.rowIcon}>
					<FontAwesome6 name="door-closed" size={30} color={Brand.purple} />
				</View>
				<View style={styles.rowInfo}>
					<Text style={styles.rowTitle} numberOfLines={1}>
						Reservable Spaces
					</Text>
					<Text style={styles.rowMeta} numberOfLines={1}>
						Rooms you can book
					</Text>
				</View>
			</Pressable>

			<Pressable
				onPress={onSelectPublic}
				android_ripple={{ color: "#E5E7EB" }}
				style={({ pressed }) => [styles.row, { backgroundColor: pressed ? "#f8eeff" : "#FFFFFF" }]}
			>
				<View style={styles.rowIcon}>
					<FontAwesome6 name="door-open" size={30} color={Brand.purple} />
				</View>
				<View style={styles.rowInfo}>
					<Text style={styles.rowTitle} numberOfLines={1}>
						Public Spaces
					</Text>
					<Text style={styles.rowMeta} numberOfLines={1}>
						Floors, open areas, outdoors
					</Text>
				</View>
			</Pressable>
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
		paddingHorizontal: 12,
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
	title: {
		flex: 1,
		textAlign: "center",
		fontSize: 20,
		fontWeight: "600",
		color: "#000",
		paddingHorizontal: 8,
	},
	divider: {
		height: StyleSheet.hairlineWidth,
		backgroundColor: "#E5E7EB",
		marginTop: 10,
	},
	row: {
		display: "flex",
		flexDirection: "row",
		alignContent: "center",
		paddingHorizontal: 16,
		paddingVertical: 14,
		borderBottomWidth: StyleSheet.hairlineWidth,
		borderBottomColor: "#E5E7EB",
		overflow: "hidden",
	},
	rowIcon: {
		padding: 12,
		margin: 15,
		marginRight: 30,
		borderRadius: 10,
		backgroundColor: "#9b4afe2e",
	},
	rowInfo: {
		flex: 1,
		verticalAlign: "middle",
		alignSelf: "center",
	},
	rowTitle: {
		fontSize: 18,
		lineHeight: 22,
		fontWeight: "400",
		color: Brand.purple,
	},
	rowMeta: {
		marginTop: 6,
		fontSize: 13,
		lineHeight: 16,
		color: "#6B7280",
	},
});
