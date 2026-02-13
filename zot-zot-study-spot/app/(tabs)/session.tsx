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

function ratingLabel(r: number) {
	switch (r) {
		case 1:
			return "Horrible";
		case 2:
			return "Bad";
		case 3:
			return "Okay";
		case 4:
			return "Good";
		case 5:
			return "Amazing";
		default:
			return "";
	}
}

export default function Session() {
	const scheme = useColorScheme();
	const theme = scheme === "dark" ? Colors.dark : Colors.light;

	const { selectedSpot, clearSelectedSpot } = useSession();
	const canStart = !!selectedSpot;

	const [elapsedMs, setElapsedMs] = useState(0);
	const [running, setRunning] = useState(false);

	// rating flow
	const [showRating, setShowRating] = useState(false);
	const [rating, setRating] = useState<number | null>(null);

	const startedAtRef = useRef<number | null>(null);
	const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

	const clearIntervalSafe = () => {
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
		clearIntervalSafe();
		intervalRef.current = setInterval(tick, 50);
	};

	const pause = () => {
		if (!running) return;
		setRunning(false);
		startedAtRef.current = null;
		clearIntervalSafe();
	};

	const endSession = () => {
		// stop timer
		setRunning(false);
		startedAtRef.current = null;
		clearIntervalSafe();

		// If there was a real session, ask for rating
		if (selectedSpot && elapsedMs > 0) {
			setShowRating(true);
			setRating(null);
			return;
		}

		// Otherwise just clear immediately
		setElapsedMs(0);
		clearSelectedSpot();
		setShowRating(false);
		setRating(null);
	};

	const submitRating = () => {
		// TODO: persist rating somewhere (AsyncStorage / Supabase / context)
		if (selectedSpot) {
			console.log("Session rating:", {
				rating,
				elapsedMs,
				locationId: selectedSpot.locationId,
				locationTitle: selectedSpot.locationTitle,
				spaceId: selectedSpot.spaceId,
				spaceTitle: selectedSpot.spaceTitle,
			});
		}

		// reset
		setShowRating(false);
		setRating(null);
		setElapsedMs(0);
		clearSelectedSpot();
	};

	const skipRating = () => {
		setShowRating(false);
		setRating(null);
		setElapsedMs(0);
		clearSelectedSpot();
	};

	useEffect(() => {
		return () => clearIntervalSafe();
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

			<View
				style={[
					styles.card,
					{
						backgroundColor: theme.surface,
						borderColor: theme.outline,
						shadowColor: theme.shadow,
						marginTop: 14,
						opacity: showRating ? 1 : 0.55,
					},
				]}
			>
				<Text style={[styles.title, { color: theme.text }]}>Rate your session</Text>

				{!showRating ? (
					<Text style={[styles.hint, { color: theme.text, opacity: 0.7 }]}>End your session to rate it.</Text>
				) : (
					<>
						<Text style={[styles.ratingPrompt, { color: theme.text, opacity: 0.85 }]}>How was it?</Text>

						<View style={styles.ratingRow}>
							{[1, 2, 3, 4, 5].map((r) => {
								const selected = rating === r;
								return (
									<Pressable
										key={r}
										onPress={() => setRating(r)}
										style={({ pressed }) => [
											styles.ratingPill,
											{
												backgroundColor: selected ? "rgba(84,56,220,0.14)" : theme.surfaceVariant,
												borderColor: selected ? theme.brand : theme.outlineSoft,
												opacity: pressed ? 0.85 : 1,
											},
										]}
									>
										<Text style={[styles.ratingNumber, { color: selected ? theme.brand : theme.text }]}>{r}</Text>
									</Pressable>
								);
							})}
						</View>

						<Text style={[styles.ratingLabel, { color: theme.text, opacity: 0.8 }]}>
							{rating ? `${rating} — ${ratingLabel(rating)}` : "Tap a number (1 = Horrible, 5 = Amazing)"}
						</Text>

						<View style={[styles.row, { marginTop: 12 }]}>
							<Pressable
								onPress={submitRating}
								disabled={rating == null}
								style={({ pressed }) => [
									styles.primaryBtn,
									{
										backgroundColor: rating == null ? theme.outlineSoft : pressed ? Brand.dark_purple : theme.brand,
										opacity: rating == null ? 0.6 : 1,
									},
								]}
							>
								<Text style={[styles.primaryText, { color: theme.textOnBrand }]}>Save rating</Text>
							</Pressable>

							<Pressable
								onPress={skipRating}
								style={({ pressed }) => [
									styles.secondaryBtn,
									{
										backgroundColor: theme.surfaceVariant,
										borderColor: theme.outlineSoft,
										opacity: pressed ? 0.75 : 1,
									},
								]}
							>
								<Text style={[styles.secondaryText, { color: theme.text }]}>Skip</Text>
							</Pressable>
						</View>
					</>
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
		fontWeight: "700",
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
		fontWeight: "700",
		fontSize: 16,
	},
	hint: {
		marginTop: 12,
		textAlign: "center",
		fontSize: 13,
	},

	// rating styles
	ratingPrompt: {
		textAlign: "center",
		fontSize: 14,
		fontWeight: "700",
		marginBottom: 10,
	},
	ratingRow: {
		flexDirection: "row",
		justifyContent: "center",
		gap: 10,
		marginBottom: 10,
	},
	ratingPill: {
		width: 46,
		height: 46,
		borderRadius: 23,
		alignItems: "center",
		justifyContent: "center",
		borderWidth: 1,
	},
	ratingNumber: {
		fontSize: 18,
		fontWeight: "900",
	},
	ratingLabel: {
		textAlign: "center",
		fontSize: 13,
	},
});
