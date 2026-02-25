import * as Location from "expo-location";

export async function getUserLocationOrNull() {
	// Need to request location permission (mandatory on mobile apps)
	const { status, canAskAgain } = await Location.requestForegroundPermissionsAsync();

	if (status !== "granted") { // TODO
		return {
			coords: null,
			error: canAskAgain
				? "Location permission denied. Please allow location to use nearby results."
				: "Location permission denied. Enable it in Settings to use nearby results.",
		};
	}

	// Check services are enabled 
	const servicesEnabled = await Location.hasServicesEnabledAsync();
	if (!servicesEnabled) {
		return { coords: null, error: "Location services are off. Turn on GPS/location services." };
	}

	// Now we have access to location
	const pos = await Location.getCurrentPositionAsync({
		accuracy: Location.Accuracy.Balanced,
	});

	return { coords: pos.coords, error: null };
}
