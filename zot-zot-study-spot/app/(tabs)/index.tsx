
import { Image } from "expo-image";
import { View, StyleSheet, Pressable } from "react-native";
import React, {  useEffect, useState } from "react";
import { FilterBar, Filters } from "@/components/filter-bar";
import { FontAwesome6 } from "@expo/vector-icons";
import MapView, { LatLng, Geojson, Marker} from "react-native-maps";
import { Colors, Brand, Fonts } from "@/constants/theme";
import FeatureCollection, {GeoJsonObject} from 'geojson';
//import {check, request, PERMISSIONS, RESULTS} from 'react-native-permissions';
import * as Location from "expo-location";

const route = {"type":"FeatureCollection","bbox":[-117.846031,33.644952,-117.842622,33.645906],"features":[{"bbox":[-117.846031,33.644952,-117.842622,33.645906],"type":"Feature","properties":{"segments":[{"distance":397.7,"duration":286.3,"steps":[{"distance":22.4,"duration":16.1,"type":11,"instruction":"Head northwest","name":"-","way_points":[0,1]},{"distance":30,"duration":21.6,"type":5,"instruction":"Turn slight right","name":"-","way_points":[1,2]},{"distance":22.8,"duration":16.4,"type":12,"instruction":"Keep left","name":"-","way_points":[2,3]},{"distance":82.1,"duration":59.1,"type":4,"instruction":"Turn slight left","name":"-","way_points":[3,7]},{"distance":112.2,"duration":80.8,"type":12,"instruction":"Keep left","name":"-","way_points":[7,14]},{"distance":128.2,"duration":92.3,"type":0,"instruction":"Turn left","name":"-","way_points":[14,24]},{"distance":0,"duration":0,"type":10,"instruction":"Arrive at your destination, straight ahead","name":"-","way_points":[24,24]}]}],"way_points":[0,24],"summary":{"distance":397.7,"duration":286.3}},"geometry":{"coordinates":[[-117.842622,33.644952],[-117.842742,33.645123],[-117.842699,33.645391],[-117.842776,33.645586],[-117.843101,33.645767],[-117.843289,33.645801],[-117.843312,33.645805],[-117.84358,33.645869],[-117.843659,33.645836],[-117.843954,33.645821],[-117.844256,33.645796],[-117.844492,33.645789],[-117.84459,33.645786],[-117.84464,33.645789],[-117.844647,33.645906],[-117.844734,33.645904],[-117.844888,33.645899],[-117.844976,33.645897],[-117.845281,33.645896],[-117.845353,33.645896],[-117.845499,33.645896],[-117.845686,33.645888],[-117.845928,33.645879],[-117.846024,33.645876],[-117.846031,33.645876]],"type":"LineString"}}],"metadata":{"attribution":"openrouteservice.org | OpenStreetMap contributors","service":"routing","timestamp":1770326786099,"query":{"coordinates":[[-117.842301,33.645109],[-117.846031,33.645871]],"profile":"foot-walking","profileName":"foot-walking","format":"json"},"engine":{"version":"9.5.0","build_date":"2025-10-31T12:33:09Z","graph_date":"2026-01-26T15:03:31Z","osm_date":"2026-01-19T01:00:01Z"}}}

//put <Geojson geojson={route} /> inside mapview to show a route
export default function HomeScreen() {
	const [filters, setFilters] = useState<Filters>({
		capacity: null,
		environment: "any",
		techEnhanced: false,
	});
	
	const theme = Colors.light;
	
	useEffect(() => {
    async function getCurrentLocation() {
      let { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== "granted") {
        return;
      }

      let location = await Location.getCurrentPositionAsync({});
    }
  	}, []);
	
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
          			longitudeDelta: 0.008,}}>

				<Marker
					//events
					onSelect = {select_marker}
					onDeselect = {deselect_marker}
					
					//characteristics
					coordinate = {get_marker_coordinates()}
				/>
				
			</MapView>

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

			{/* Pin (example) */}
			<FontAwesome6 name="map-marker" size={24} color={theme.brand} />
		</View>
	);
}

function select_marker()
{
	return
}

function deselect_marker()
{
	return
}

function update_route_as_user_moves()
{
	return
}

function get_marker_coordinates()
{
	return {latitude: 33.64579, longitude: -117.84279};
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
