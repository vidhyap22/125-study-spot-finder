
import { Image } from "expo-image";
import { View, StyleSheet, Pressable } from "react-native";
import { useState } from "react";
import { FilterBar, Filters } from "@/components/filter-bar";
import { FontAwesome6 } from "@expo/vector-icons";

import { Colors, Brand, Fonts } from "@/constants/theme";

export default function HomeScreen() {
	const [filters, setFilters] = useState<Filters>({
		capacity: null,
		environment: "any",
		techEnhanced: false,
	});

	const theme = Colors.light;

	return (
		<View style={[styles.container, { backgroundColor: theme.background }]}>
			{/* Placeholder image of map */}
			<Image source={{ uri: "https://cdn.pacer.cc/route/screenshot/9mupq_20200225_18.png" }} style={styles.image} contentFit="cover" />

			{/* Floating filter bar */}
			<View style={styles.controlWrapper}>
				<View style={styles.filterBarWrapper}>
					<FilterBar value={filters} onChange={setFilters} />
				</View>

				{/* Search button */}
				<View style={[styles.findButtonShadow, { shadowColor: theme.shadow }]}>
					<Pressable
						android_ripple={{ color: "rgba(255,255,255,0.2)" }}
						style={({ pressed }) => [
							styles.findButton,
							{
								backgroundColor: pressed ? Brand.dark_purple : theme.brand,
								opacity: pressed ? 0.92 : 1, 
							},
						]}
					>
						<FontAwesome6 name="magnifying-glass" size={18} color={theme.textOnBrand} />
					</Pressable>
				</View>
			</View>

			{/* User Location bubble */}
			<View
				style={[
					styles.userBubble,
					{
						backgroundColor: theme.brand,
						borderColor: theme.surface,
						shadowColor: theme.brand,
					},
				]}
			/>

			{/* Pin (example) */}
			<FontAwesome6 name="map-marker" size={24} color={theme.brand} />
		</View>
	);
}

const styles = StyleSheet.create({
	container: { flex: 1 },

	image: { ...StyleSheet.absoluteFillObject },

	controlWrapper: {
		position: "absolute",
		top: 80,
		left: 16,
		right: 16,
		flexDirection: "row",
		gap: 12,
	},

	filterBarWrapper: { flex: 0.8 },

	findButtonShadow: {
		flex: 0.2,
		borderRadius: 22,
		shadowOpacity: 0.5,
		shadowRadius: 8,
		shadowOffset: { width: 0, height: 3 },
		elevation: 6,
		backgroundColor: "transparent",
	},

	findButton: {
		height: 44,
		borderRadius: 22,
		overflow: "hidden",
		alignItems: "center",
		justifyContent: "center",
	},

	userBubble: {
		borderRadius: 50,
		position: "absolute",
		top: 200,
		left: 100,
		height: 25,
		aspectRatio: 1,
		elevation: 10,
		borderWidth: 2,
		shadowOpacity: 0.9,
		shadowRadius: 10,
	},
});
