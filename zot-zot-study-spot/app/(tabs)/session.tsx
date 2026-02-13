import { Brand, Colors } from "@/constants/theme";
import { useSession } from "@/context/session-context";
import { useEffect, useRef, useState } from "react";
import { Pressable, StyleSheet, Text, View, useColorScheme } from "react-native";

function pad2(n: number) {
	return n.toString().padStart(2, "0");
}

function formatMs(ms: number) {
	const totalSec = Math.floor(ms / 1000);
	const minutes = Math.floor(totalSec / 60);
	const seconds = totalSec % 60;
	const centis = Math.floor((ms % 1000) / 10);
	return `${pad2(minutes)}:${pad2(seconds)}.${pad2(centis)}`;
}

export default function Session() {
	const scheme = useColorScheme();
	const theme = scheme === "dark" ? Colors.dark : Colors.light;

	const { selectedSpot, clearSelectedSpot } = useSession();
	const canStart = !!selectedSpot;

	const [elapsedMs, setElapsedMs] = useState(0);
	const [running, setRunning] = useState(false);

	const startedAtRef = useRef<number | null>(null);
	const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

	const clear = () => {
		if (intervalRef.current) {
			clearInterval(intervalRef.current);
			intervalRef.current = null;
		}
	};

	const tick = () => {
		if (startedAtRef.current == null) return;
		const now = Date.now();
		const delta = now - startedAtRef.current;
		startedAtRef.current = now;
		setElapsedMs((prev) => prev + delta);
	};

	const start = () => {
		if (running) return;
		if (!selectedSpot) return; // guard
		setRunning(true);
		startedAtRef.current = Date.now();
		clear();
		intervalRef.current = setInterval(tick, 50);
	};

	const pause = () => {
		if (!running) return;
		setRunning(false);
		startedAtRef.current = null;
		clear();
	};

	const endSession = () => {
		setRunning(false);
		startedAtRef.current = null;
		clear();
		setElapsedMs(0);
		clearSelectedSpot();
	};

	useEffect(() => {
		return () => clear();
	}, []);

	return (
		<View style={[styles.root, { backgroundColor: theme.background }]}>
			<View style={[styles.card, { backgroundColor: theme.surface, borderColor: theme.outline, shadowColor: theme.shadow }]}>
				<Text style={[styles.title, { color: theme.text }]}>Session Timer</Text>

				<View style={styles.spotRow}>
					<Text style={[styles.spotLabel, { color: theme.text, opacity: 0.7 }]}>Study spot</Text>
					<Text style={[styles.spotValue, { color: theme.text }]} numberOfLines={2}>
						{selectedSpot ? `${selectedSpot.locationTitle} • ${selectedSpot.spaceTitle}` : "No study spot selected"}
					</Text>
				</View>

				<View style={[styles.timerBox, { backgroundColor: "rgba(84,56,220,0.08)", borderColor: theme.outlineSoft }]}>
					<Text style={[styles.timerText, { color: theme.brand }]}>{formatMs(elapsedMs)}</Text>
				</View>

				<View style={styles.row}>
					<Pressable
						onPress={running ? pause : start}
						disabled={!canStart && !running}
						style={({ pressed }) => [
							styles.primaryBtn,
							{
								backgroundColor: !canStart && !running ? theme.outlineSoft : pressed ? Brand.dark_purple : theme.brand,
								opacity: !canStart && !running ? 0.6 : 1,
							},
						]}
					>
						<Text style={[styles.primaryText, { color: theme.textOnBrand }]}>{running ? "Pause" : "Start"}</Text>
					</Pressable>

					<Pressable
						onPress={endSession}
						style={({ pressed }) => [
							styles.secondaryBtn,
							{
								backgroundColor: theme.surfaceVariant,
								borderColor: theme.outlineSoft,
								opacity: pressed ? 0.75 : 1,
							},
						]}
					>
						<Text style={[styles.secondaryText, { color: theme.text }]}>End Session</Text>
					</Pressable>
				</View>

				{!selectedSpot && !running && (
					<Text style={[styles.hint, { color: theme.text, opacity: 0.7 }]}>Select a study spot from the map results to start.</Text>
				)}
			</View>
		</View>
	);
}

const styles = StyleSheet.create({
	root: {
		flex: 1,
		justifyContent: "center",
		padding: 18,
	},
	card: {
		borderRadius: 18,
		padding: 18,
		borderWidth: 1,
		shadowOpacity: 0.08,
		shadowRadius: 18,
		shadowOffset: { width: 0, height: 10 },
		elevation: 6,
	},
	title: {
		fontSize: 22,
		fontWeight: "700",
		textAlign: "center",
		marginBottom: 12,
	},
	spotRow: {
		alignItems: "center",
		gap: 4,
		marginBottom: 16,
	},
	spotLabel: {
		fontSize: 13,
		fontWeight: "700",
	},
	spotValue: {
		fontSize: 15,
		fontWeight: "700",
		textAlign: "center",
	},
	timerBox: {
		alignItems: "center",
		paddingVertical: 18,
		borderRadius: 14,
		borderWidth: 1,
		marginBottom: 20,
	},
	timerText: {
		fontSize: 44,
		fontWeight: "900",
		letterSpacing: 1,
	},
	row: {
		flexDirection: "row",
		gap: 12,
	},
	primaryBtn: {
		flex: 1,
		paddingVertical: 13,
		borderRadius: 12,
		alignItems: "center",
	},
	primaryText: {
		fontWeight: "600",
		fontSize: 16,
	},
	secondaryBtn: {
		flex: 1,
		paddingVertical: 13,
		borderRadius: 12,
		alignItems: "center",
		borderWidth: 1,
	},
	secondaryText: {
		fontWeight: "600",
		fontSize: 16,
	},
	hint: {
		marginTop: 12,
		textAlign: "center",
		fontSize: 13,
	},
});
