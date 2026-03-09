import { FilterBar, Filters } from "@/components/filter-bar";
import { LocationResultsPage } from "@/components/location-results-panel";
import { Brand, Colors } from "@/constants/theme";
import { MOCK_LOCATIONS } from "@/utils/mock-locations";
import { FontAwesome6 } from "@expo/vector-icons";
import { useEffect, useState } from "react";
import { Pressable, StyleSheet, View } from "react-native";
import MapView, { Marker } from "react-native-maps";
import { apiSearchSpaces, toApiFilters, apiGetBuildings } from "@/utils/api-client";
import type { LocationResult } from "@/utils/types";
import * as Location from "expo-location";

const USER_ID = "1"; // hardcoding current user ID
const myPlace = {
	type: "FeatureCollection",
	features: [
		{
			type: "Feature",
			properties: {},
			geometry: {
				type: "Point",
				coordinates: [-117.84279, 33.64579],
			},
		},
	],
};

export default function HomeScreen() {
	const [locations, setLocations] = useState<LocationResult[]>([]);
	const [markers, setMarkers] = useState<LocationResult[]>([]); //All currently available markers
	const [isSearching, setIsSearching] = useState(false);
	const [searchError, setSearchError] = useState<string | null>(null);
	const [filters, setFilters] = useState<Filters>({
		capacity: null,
		environment: "any",
		techEnhanced: false,
	});
	const [stage, setStage] = useState("results");
	const [selectedLocation, setSelectedLocation] = useState<LocationResult|null>(null);

	const theme = Colors.light;
	const [showResults, setShowResults] = useState(false);

	useEffect(() => {
		async function getCurrentLocation() {
			let { status } = await Location.requestForegroundPermissionsAsync();
			if (status !== "granted") {
				return;
			}

			let location = await Location.getCurrentPositionAsync({});
		}
		getCurrentLocation();
	}, []);

	useEffect(() => {
		async function retrieve_buildings()
		{
			const response = await apiGetBuildings();
			if (response.success)
				setMarkers(response.data);
		}
		retrieve_buildings();
	}, []);

	async function onSearchPress() {
		setIsSearching(true);
		setSearchError(null);

		const apiFilters = toApiFilters(filters);

		const res = await apiSearchSpaces({
			user_id: USER_ID,
			filters: apiFilters,
			debug: false,
		});

		setIsSearching(false);

		if (!res.success) {
			setSearchError(res.error);
			// TODO: error UI
			//setLocations([]);//
			setShowResults(true);
			return;
		}
		console.log(res.data[0]);

		//setLocations(res.data as LocationResult[]);
		setShowResults(true);
	}

	function select_marker(marker) 
	{
		console.log(marker)
		setStage("category");
		setSelectedLocation(markers[Number(marker.id)]);
		setShowResults(true);
	}

	function deselect_marker(marker) 
	{
		setStage("results");
		setSelectedLocation(null);
		setShowResults(false);
	}

	return (
		<View style={[styles.container, { backgroundColor: theme.background }]}>
			{/* Map */}
			<MapView
				style={styles.image}
				//events
				onUserLocationChange={update_route_as_user_moves}
				//non-events
				showsPointsOfInterest={false} //removes default apple pins since ours overlap
				showsUserLocation
				initialRegion={{
					latitude: 33.64579,
					longitude: -117.84279,
					latitudeDelta: 0.008,
					longitudeDelta: 0.008,
				}}
			>
				{markers.map((marker, index) => (
					<Marker
						//events
						onSelect={marker => select_marker(marker.nativeEvent)}
						onDeselect={marker => deselect_marker(marker.nativeEvent)}
						//characteristics
						coordinate= {{latitude: marker.latitude, longitude:marker.longitude}}
						description = {marker.title}
						identifier = {index + ""}
						title = {marker.id}
						key = {index}
					/>
				))}
			</MapView>

			{/* Floating filter bar */}
			<View style={styles.controlWrapper}>
				<View style={styles.filterBarWrapper}>
					<FilterBar value={filters} onChange={setFilters} />
				</View>

				{/* Search button */}

				<View style={[styles.findButtonShadow, { shadowColor: theme.shadow }]}>
					<Pressable
						onPress={onSearchPress}
						disabled={isSearching}
						android_ripple={{ color: "rgba(255,255,255,0.2)", borderless: false }}
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

			{/* Pin (example) */}
			{/* <FontAwesome6 name="map-marker" size={24} color={theme.brand} /> */}
			<LocationResultsPage 
				visible={showResults} 
				onRequestClose={() => setShowResults(false)} 
				locations={markers} 
				stageProp = {stage}
				selectedLocationProp = {selectedLocation}
				/>
		</View>
	);
}

function update_route_as_user_moves() {
	return;
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
