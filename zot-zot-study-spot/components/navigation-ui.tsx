import geoJSON from "@types";
import {useState, useEffect} from "react";
import MapView, {Geojson} from "react-native-maps";
import * as Location from "expo-location";
import {StyleSheet, Pressable, View, Text} from "react-native";
import { BottomSheetPanel } from "@/components/bottom-sheet-panel";

export const ex_route = {
  "type": "FeatureCollection",
  "bbox": [-117.841848, 33.644486, -117.8412, 33.647261],
  "features": [
    {
      "bbox": [-117.841848, 33.644486, -117.8412, 33.647261],
      "type": "Feature",
      "properties": {
        "segments": [
          {
            "distance": 383.2,
            "duration": 275.9,
            "steps": [
              {
                "distance": 15.5,
                "duration": 11.2,
                "type": 11,
                "instruction": "Head northeast",
                "name": "-",
                "way_points": [0, 2]
              },
              {
                "distance": 20.6,
                "duration": 14.8,
                "type": 0,
                "instruction": "Turn left",
                "name": "-",
                "way_points": [2, 4]
              },
              {
                "distance": 8.1,
                "duration": 5.8,
                "type": 0,
                "instruction": "Turn left",
                "name": "-",
                "way_points": [4, 5]
              },
              {
                "distance": 48.1,
                "duration": 34.6,
                "type": 1,
                "instruction": "Turn right",
                "name": "-",
                "way_points": [5, 9]
              },
              {
                "distance": 193.5,
                "duration": 139.3,
                "type": 1,
                "instruction": "Turn right onto Inner Ring",
                "name": "Inner Ring",
                "way_points": [9, 17]
              },
              {
                "distance": 32.3,
                "duration": 23.3,
                "type": 1,
                "instruction": "Turn right",
                "name": "-",
                "way_points": [17, 21]
              },
              {
                "distance": 31.7,
                "duration": 22.8,
                "type": 1,
                "instruction": "Turn right",
                "name": "-",
                "way_points": [21, 23]
              },
              {
                "distance": 9.8,
                "duration": 7.1,
                "type": 1,
                "instruction": "Turn right",
                "name": "-",
                "way_points": [23, 24]
              },
              {
                "distance": 17.8,
                "duration": 12.8,
                "type": 1,
                "instruction": "Turn right",
                "name": "-",
                "way_points": [24, 26]
              },
              {
                "distance": 5.7,
                "duration": 4.1,
                "type": 1,
                "instruction": "Turn right",
                "name": "-",
                "way_points": [26, 27]
              },
              {
                "distance": 0,
                "duration": 0,
                "type": 10,
                "instruction": "Arrive at your destination, on the left",
                "name": "-",
                "way_points": [27, 27]
              }
            ]
          }
        ],
        "way_points": [0, 27],
        "summary": {
          "distance": 383.2,
          "duration": 275.9
        }
      },
      "geometry": {
        "coordinates": [
          [-117.841848, 33.644486],
          [-117.841793, 33.644521],
          [-117.841715, 33.644571],
          [-117.84173, 33.644588],
          [-117.841573, 33.644687],
          [-117.841626, 33.644745],
          [-117.841538, 33.644816],
          [-117.841459, 33.64494],
          [-117.841471, 33.645037],
          [-117.841528, 33.645117],
          [-117.841411, 33.64525],
          [-117.84132, 33.645406],
          [-117.841241, 33.645581],
          [-117.841201, 33.64573],
          [-117.8412, 33.645968],
          [-117.841254, 33.646196],
          [-117.841358, 33.646446],
          [-117.841562, 33.646726],
          [-117.841516, 33.646775],
          [-117.841514, 33.646872],
          [-117.841531, 33.646913],
          [-117.841604, 33.646977],
          [-117.84149, 33.647129],
          [-117.841594, 33.64719],
          [-117.84153, 33.647261],
          [-117.841428, 33.647202],
          [-117.841387, 33.647247],
          [-117.841339, 33.647214]
        ],
        "type": "LineString"
      }
    }
  ],
  "metadata": {
    "attribution": "openrouteservice.org | OpenStreetMap contributors",
    "service": "routing",
    "timestamp": 1773676072524,
    "query": {
      "coordinates": [
        [-117.841832908902, 33.6444700729087],
        [-117.841159, 33.647176]
      ],
      "profile": "foot-walking",
      "profileName": "foot-walking",
      "format": "json"
    },
    "engine": {
      "version": "9.5.0",
      "build_date": "2025-10-31T12:33:09Z",
      "graph_date": "2026-03-02T19:01:20Z",
      "osm_date": "2026-02-16T01:00:01Z"
    }
  }
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