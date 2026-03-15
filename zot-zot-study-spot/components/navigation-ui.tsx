import geoJSON from "@types";
import {useState, useEffect} from "react";
import MapView, {Geojson} from "react-native-maps";
import * as Location from "expo-location";
import {StyleSheet, Pressable, View, Text} from "react-native";
import { BottomSheetPanel } from "@/components/bottom-sheet-panel";

export const ex_route = {
	type: "FeatureCollection",
	bbox: [-117.846031, 33.644952, -117.842622, 33.645906],
	features: [
		{
			bbox: [-117.846031, 33.644952, -117.842622, 33.645906],
			type: "Feature",
			properties: {
				segments: [
					{
						distance: 397.7,
						duration: 286.3,
						steps: [
							{ distance: 22.4, duration: 16.1, type: 11, instruction: "Head northwest", name: "-", way_points: [0, 1] },
							{ distance: 30, duration: 21.6, type: 5, instruction: "Turn slight right", name: "-", way_points: [1, 2] },
							{ distance: 22.8, duration: 16.4, type: 12, instruction: "Keep left", name: "-", way_points: [2, 3] },
							{ distance: 82.1, duration: 59.1, type: 4, instruction: "Turn slight left", name: "-", way_points: [3, 7] },
							{ distance: 112.2, duration: 80.8, type: 12, instruction: "Keep left", name: "-", way_points: [7, 14] },
							{ distance: 128.2, duration: 92.3, type: 0, instruction: "Turn left", name: "-", way_points: [14, 24] },
							{ distance: 0, duration: 0, type: 10, instruction: "Arrive at your destination, straight ahead", name: "-", way_points: [24, 24] },
						],
					},
				],
				way_points: [0, 24],
				summary: { distance: 397.7, duration: 286.3 },
			},
			geometry: {
				coordinates: [
					[-117.842622, 33.644952],
					[-117.842742, 33.645123],
					[-117.842699, 33.645391],
					[-117.842776, 33.645586],
					[-117.843101, 33.645767],
					[-117.843289, 33.645801],
					[-117.843312, 33.645805],
					[-117.84358, 33.645869],
					[-117.843659, 33.645836],
					[-117.843954, 33.645821],
					[-117.844256, 33.645796],
					[-117.844492, 33.645789],
					[-117.84459, 33.645786],
					[-117.84464, 33.645789],
					[-117.844647, 33.645906],
					[-117.844734, 33.645904],
					[-117.844888, 33.645899],
					[-117.844976, 33.645897],
					[-117.845281, 33.645896],
					[-117.845353, 33.645896],
					[-117.845499, 33.645896],
					[-117.845686, 33.645888],
					[-117.845928, 33.645879],
					[-117.846024, 33.645876],
					[-117.846031, 33.645876],
				],
				type: "LineString",
			},
		},
	],
	metadata: {
		attribution: "openrouteservice.org | OpenStreetMap contributors",
		service: "routing",
		timestamp: 1770326786099,
		query: {
			coordinates: [
				[-117.842301, 33.645109],
				[-117.846031, 33.645871],
			],
			profile: "foot-walking",
			profileName: "foot-walking",
			format: "json",
		},
		engine: { version: "9.5.0", build_date: "2025-10-31T12:33:09Z", graph_date: "2026-01-26T15:03:31Z", osm_date: "2026-01-19T01:00:01Z" },
	},
};

type NavProps = 
{
	user_lon:number,
	user_lat:number,
	input_route:geoJSON,
	onExit:()=>void
};

export function MapNav({user_lon, user_lat, input_route, onExit}:NavProps)
{
	//helper functions
	function findNearestPointOnLine(px: number, py: number, ax: number, ay: number, bx: number, by: number)
	{
		const atob = { x: bx - ax, y: by - ay };
		const atop = { x: px - ax, y: py - ay };
		const len = (atob.x * atob.x) + (atob.y * atob.y);
		let dot = (atop.x * atob.x) + (atop.y * atob.y);
		const t = Math.min(1, Math.max(0, dot / len));

		dot = ((bx - ax) * (py - ay)) - ((by - ay) * (px - ax));

		return { x: ax + (atob.x * t), y: ay + (atob.y * t) };
	}

	function setup_nav(route:geoJSON, user_lon:number, user_lat:number)
	{
		let covered_route = JSON.parse(JSON.stringify(route));
		covered_route.features.geometry.coordinates = [];//remove all but first point
		covered_route.features.geometry.coordinates.push(route.features.geometry.coordinates[0]);
		let start = route.features.geometry.coordinates[0];
		let end = route.features.geometry.coordinates[1];
		let user_point = findNearestPointOnLine(user_lon, user_lat, start[0], start[1], end[0], end[1]);
		covered_route.features.geometry.coordinates.push(user_point);
		setCurrentLine(1);
		return covered_route
	}

	function update_nav(user_lon:number, user_lat:number)
	{
		let covered_route = JSON.parse(JSON.stringify(covered));
		let prev_point = covered_route.features.geometry.coordinates.pop();
		//check if prev_point passes the current line segment?
		if(user_passed_line(user_lon, user_lat))
		{	
			setCurrentLine(currentLine+1);
			if (currentLine >= route.features.geometry.coordinates.length)
			{
				return covered_route
			}
		}
		//update line segment
		let start = route.features.geometry.coordinates[currentLine];
		let end = route.features.geometry.coordinates[currentLine+1];
		let user_point = findNearestPointOnLine(user_lon, user_lat, start[0], start[1], end[0], end[1]);
		covered_route.features.geometry.coordinates.push(user_point);
		return covered_route;
	}

	function user_passed_line(user_x:number, user_y:number)
	{
		//These are from the projection of user location onto line?
		let {start_x, start_y} = route.features.geometry.coordinates[currentLine];
		let {end_x, end_y} = route.features.geometry.coordinates[currentLine];
		if (start_y > end_y && end_y > user_y)
		{
			return true;
		}
		else if (start_y < end_y && end_y < user_y)
		{
			return true;
		}
		return false;
	}

	//set necessary states
	const [currentLine, setCurrentLine] = useState<number>(0);
	const [route, setRoute] = useState<geoJSON>(input_route);
	//const [covered, setCovered] = useState<geoJSON>(setup_nav(route, user_lon, user_lat));

	useEffect( ()=>{
		setRoute(input_route);
		console.log("route in MapNav: ");
		console.log(input_route);
		//setCovered(setup_nav(input_route, user_lon, user_lat));
	}, [input_route])
	
	//call update_nav + return html for route + coveredroute when placed inside MapView
	//setCovered(update_nav(user_lon, user_lat));
	/*if (currentLine > route.features.geometry.coordinates.length)
	{
		onExit();
	}*/
	return (
		<MapView
			style = {styles.image}
			showsUserLocation
			followsUserLocation
			initialRegion={{
					latitude: user_lat,
					longitude: user_lon,
					latitudeDelta: 0.005,
					longitudeDelta: 0.005,
				}}
			showsPointsOfInterest = {false}>
				<Geojson 
					geojson = {input_route}
					strokeColor = "blue"
					strokeWidth = {5}
				/>
				{/*
				//<Geojson
				//	geojson = {covered}
				//	strokeColor = "black"
				//	strokeWidth = {3}
				///>*/}
		</MapView>
		
	);
}


{/*
Every time the user location is updated, we need to update the appearance of the lines
Since we have given line segments, the easy way to make it look like a line changes color
midway through is probably to render the route from openrouteservice on the bottom, with the
appearance of the "route to go" that the user hasn't walked yet.
Render the part of the route the user has already walked on top of this in a different color
with >= thickness as the bottom route. 
The thing to calculate is what line segments make up the already walked route.
The components of this are 
    1) Figure out which line segment the user is currently on
        - We should keep track of this over time. We should be able to calculate whether the user has 
        passed the current line segment + is heading in the direction of the next line segment. When 
        this is true, append the full current line segment to past line segments and set the next
        line segment as the current line segment
        - If nearestPointOnLine() from user location to current_line is further in the same direction
        than the end point of the line, the user has passed to the next line
        - If the new line segment is associated with a new direction, update the direction
    2) Figure out which point on the current line segment the user is at (project exact location to
        a point on the line segment so we don't get funny angles)
    3) Format a separate geojson object with the past line segments that can be updated dynamically
    4) set the last line segment in the geojson to start at the start of the current line and
    end at the point on the current line segment the user is at
*/}
type exitButtonProps = {onExit:()=>void};

export function ExitNavButton({onExit}: exitButtonProps)
{
	return (
	//<View style = {styles.buttonContainer}>
		<Pressable
			style = {styles.buttonContainer}
			onPress={onExit}
		>
			<Text style = {styles.buttonText}>
				Exit
			</Text>
		</Pressable>
	//</View>
	);
}

const styles = StyleSheet.create({
	image: { ...StyleSheet.absoluteFillObject },
	buttonContainer: {
		position: 'absolute', // Key to absolute positioning
		bottom: '5%',
		right: '5%',
		width: 100,
		height: 30,
		alignItems: 'center',
		backgroundColor: '#4b49d7',
		justifyContent: 'center',
		borderRadius: 5,
		marginHorizontal: 10,
		//padding: 15,
	},
	buttonText: {
		color: 'white',
		fontSize: 12,
	},
})