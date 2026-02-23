import { Image } from "expo-image";
import { View, StyleSheet, Pressable } from "react-native";
import React, {  useEffect, useState } from "react";
import { FilterBar, Filters } from "@/components/filter-bar";
import { LocationResultsPage, LocationResultsPanel, Stage} from "@/components/location-results-panel";
import { FontAwesome6 } from "@expo/vector-icons";
import MapView, { LatLng, Geojson, Marker} from "react-native-maps";
import { Colors, Brand, Fonts } from "@/constants/theme";
import {RAW_LOCATIONS, MOCK_LOCATIONS, MOCK_MARKERS } from "@/components/mock-locations";
import BUILDING_DATA from "@/components/building-data.json";
import ALT_BUILDING_DATA from "@/components/alt_building-data.json";
import type { LocationResult } from "@/components/types";
//import {check, request, PERMISSIONS, RESULTS} from 'react-native-permissions';
import * as Location from "expo-location";

//put <Geojson geojson={route} /> inside mapview to show a route
export default function HomeScreen() {
	const [filters, setFilters] = useState<Filters>({
		capacity: null,
		environment: "any",
		techEnhanced: false,
	});
	
	const theme = Colors.light;
	const [showResults, setShowResults] = useState(false);
	const [markers, setMarkers] = useState(ALT_BUILDING_DATA);
	const [selectedLocation, setSelectedLocation] = useState<LocationResult | null>(null);
	const [stage, setStage] = useState<Stage>("results");

	//update_markers([1, 2, 3])
	
	useEffect(() => {
    async function getCurrentLocation() {
      let { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== "granted") {
        return;
      }

      let location = await Location.getCurrentPositionAsync({});
	  console.log(location)
    }
  	}, []);

	function update_markers(indices:string[])
	{	
		useEffect(()=>{
			let new_markers = Object.fromEntries(Object.entries(ALT_BUILDING_DATA).filter(([key]) => indices.includes(key)));
			setMarkers(new_markers)}, 
		[])
	}

	function select_marker(marker)
	{
		setSelectedLocation(MOCK_LOCATIONS[marker.id]);
		setStage("category");
		setShowResults(true);
	}

	function deselect_marker(marker)
	{
		setSelectedLocation(null);
		setStage("results");
		setShowResults(false);
	}

	update_markers(["LLIB", "SLIB"])
	return (
		<View style={[styles.container, { backgroundColor: theme.background }]}>

			{/* Map */}
			<MapView style={styles.image} 
				//events
				onUserLocationChange={update_route_as_user_moves}

				//non-events
				showsPointsOfInterest = {false} //removes default apple pins since ours overlap
				showsUserLocation
				initialRegion={{
					latitude: 33.64579,
          			longitude: -117.84279,
          			latitudeDelta: 0.008,
          			longitudeDelta: 0.008,}}
			>

			{Object.entries(markers).map((marker, index) => (
				<Marker
					//events
					onSelect = {(marker) => select_marker(marker.nativeEvent)}
					onDeselect = {(marker) => deselect_marker(marker.nativeEvent)}
					
					//characteristics>
					key  = {index}
					title = {marker[1].name}
					identifier = {marker[1].building_id}
					coordinate = {{latitude: marker[1].latitude, longitude: marker[1].longitude}}
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
						onPress={() => setShowResults(true)}
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
				locations={MOCK_LOCATIONS}
				curr_location={selectedLocation}
				current_stage={stage}
				/>
		</View>
	);
}


function update_route_as_user_moves()
{
	return
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
