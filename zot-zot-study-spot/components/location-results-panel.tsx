import React, { useEffect, useMemo, useState } from "react";
import { FlatList, Modal, Pressable, StyleSheet, View, Text } from "react-native";

import { BottomSheetPanel } from "@/components/bottom-sheet-panel";
import { LocationResultsRow } from "@/components/location-results-row";
import { LocationDetailsPanel } from "@/components/location-details-panel";
import type { StudySpace, LocationResult } from "@/components/types";
import { SpaceTypePanel } from "./space-type-panel";

type ResultsPanelProps = {
	locations: LocationResult[];
	onSelectLocation: (loc: LocationResult) => void;
};

export function LocationResultsPanel({ locations, onSelectLocation }: ResultsPanelProps) {
	return (
		<View style={styles.resultsContainer}>
			<View style={styles.headerRow}>
				<Text style={styles.title} numberOfLines={1}>
					Location Results
				</Text>
			</View>
			<View style={styles.divider} />
			<FlatList
				data={locations}
				keyExtractor={(item) => item.id}
				renderItem={({ item }) => (
					<LocationResultsRow
						title={item.title}
						distanceText={item.distanceText}
						printerAvailable={item.printerAvailable}
						isIndoors={item.isIndoors}
						isOutdoors={item.isOutdoors}
						onPress={() => onSelectLocation(item)}
					/>
				)}
				showsVerticalScrollIndicator={false}
			/>
		</View>
	);
}
type PageProps = {
	visible: boolean;
	onRequestClose: () => void;
	locations: LocationResult[];
};

type Stage = "results" | "category" | "spaces";
type SpaceFilter = "reservable" | "public";

const TAB_BAR_HEIGHT = 80;
const SHEET_HEIGHT = 420;

export function LocationResultsPage({ visible, onRequestClose, locations }: PageProps) {
	const [stage, setStage] = useState<Stage>("results");
	const [selectedLocation, setSelectedLocation] = useState<LocationResult | null>(null);
	const [spaceFilter, setSpaceFilter] = useState<SpaceFilter>("reservable");

	useEffect(() => {
		if (visible) {
			setStage("results");
			setSelectedLocation(null);
			setSpaceFilter("reservable");
		}
	}, [visible]);

	const list = useMemo(() => locations, [locations]);

	const filteredSpaces: StudySpace[] = useMemo(() => {
		if (!selectedLocation) return [];
		return selectedLocation.spaces.filter((s) => (spaceFilter === "reservable" ? s.reservable : !s.reservable));
	}, [selectedLocation, spaceFilter]);

	if (!visible) return null;

	return (
		<Modal transparent animationType="fade" onRequestClose={onRequestClose}>
			<Pressable style={styles.backdrop} onPress={onRequestClose} />

			<BottomSheetPanel height={SHEET_HEIGHT} bottomOffset={TAB_BAR_HEIGHT}>
				{stage === "results" && (
					<LocationResultsPanel
						locations={list}
						onSelectLocation={(loc) => {
							setSelectedLocation(loc);
							setStage("category"); // 👈 NEW: go to category page
						}}
					/>
				)}

				{stage === "category" && selectedLocation && (
					<SpaceTypePanel
						locationTitle={selectedLocation.title}
						onBack={() => {
							setSelectedLocation(null);
							setStage("results");
						}}
						onSelectReservable={() => {
							setSpaceFilter("reservable");
							setStage("spaces");
						}}
						onSelectPublic={() => {
							setSpaceFilter("public");
							setStage("spaces");
						}}
					/>
				)}

				{stage === "spaces" && selectedLocation && (
					<LocationDetailsPanel
						locationTitle={selectedLocation.title}
						locationId={selectedLocation.id}
						spaceType={spaceFilter === "reservable" ? "Reservable Spaces" : "Public Spaces"}
						spaces={filteredSpaces}
						onBack={() => setStage("category")}
					/>
				)}
			</BottomSheetPanel>
		</Modal>
	);
}

const styles = StyleSheet.create({
	// ResultsPanel container
	resultsContainer: {
		flex: 1,
		backgroundColor: "#FFFFFF",
	},

	// Modal backdrop
	backdrop: {
		...StyleSheet.absoluteFillObject,
		backgroundColor: "rgba(0,0,0,0.25)",
	},
	title: {
		flex: 1,
		textAlign: "center",
		fontSize: 20,
		fontWeight: "600",
		color: "#000",
		paddingTop: 15,
		paddingBottom: 7,
		verticalAlign: "middle",
		alignSelf: "center",
	},
	divider: {
		height: StyleSheet.hairlineWidth,
		backgroundColor: "#E5E7EB",
		marginTop: 10,
	},
	headerRow: {
		flexDirection: "row",
		alignItems: "center",
		paddingHorizontal: 12,
	},
});
