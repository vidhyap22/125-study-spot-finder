import { Brand } from "@/constants/theme";
import { Modal, Pressable, StyleSheet, Text, View } from "react-native";

type Props = {
	visible: boolean;
	message?: string;
	onConfirmation?: () => void;
	onClose?: () => void;
};

export function ConfirmationModal({ visible, message = "Are you sure?", onConfirmation, onClose }: Props) {
	return (
		<Modal visible={visible} transparent animationType="fade" onRequestClose={onClose}>
			{/* Backdrop */}
			<View style={styles.backdrop}>
				{/* Modal Card */}
				<View style={styles.card}>
					<Text style={styles.message}>{message}</Text>

					<View style={styles.buttonRow}>
						{/* NO */}
						<Pressable onPress={onClose} style={({ pressed }) => [styles.secondaryButton, pressed && { opacity: 0.7 }]}>
							<Text style={styles.secondaryText}>No</Text>
						</Pressable>

						{/* YES */}
						<Pressable
							onPress={() => {
								onConfirmation?.();
								onClose?.();
							}}
							style={({ pressed }) => [styles.primaryButton, pressed && { backgroundColor: Brand.dark_purple }]}
						>
							<Text style={styles.primaryText}>Yes</Text>
						</Pressable>
					</View>
				</View>
			</View>
		</Modal>
	);
}

const styles = StyleSheet.create({
	backdrop: {
		flex: 1,
		backgroundColor: "rgba(0,0,0,0.45)",
		justifyContent: "center",
		alignItems: "center",
		padding: 20,
	},

	card: {
		width: "100%",
		maxWidth: 420,
		backgroundColor: Brand.white,
		borderRadius: 18,
		padding: 20,

		shadowColor: "#232324",
		shadowOpacity: 0.15,
		shadowRadius: 20,
		shadowOffset: { width: 0, height: 10 },
		elevation: 10,
	},

	message: {
		fontSize: 17,
		fontWeight: "600",
		color: Brand.black,
		textAlign: "center",
		marginBottom: 22,
	},

	buttonRow: {
		flexDirection: "row",
		gap: 12,
	},

	primaryButton: {
		flex: 1,
		backgroundColor: Brand.purple,
		paddingVertical: 13,
		borderRadius: 12,
		alignItems: "center",
	},

	primaryText: {
		color: Brand.white,
		fontWeight: "800",
		fontSize: 16,
	},

	secondaryButton: {
		flex: 1,
		backgroundColor: "#F3F2F7",
		paddingVertical: 13,
		borderRadius: 12,
		alignItems: "center",
	},

	secondaryText: {
		color: Brand.black,
		fontWeight: "700",
		fontSize: 16,
	},
});
