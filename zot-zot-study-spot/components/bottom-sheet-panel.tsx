import React, { useEffect, useRef } from "react";
import { Animated, Easing, StyleSheet, View } from "react-native";
import type { StyleProp, ViewStyle } from "react-native";

type Props = {
	height: number;
	bottomOffset?: number;
	style?: StyleProp<ViewStyle>;
	children: React.ReactNode;
};

export const BottomSheetPanel = ({ height, bottomOffset = 0, style, children }: Props) => {
	const animHeight = useRef(new Animated.Value(height)).current;

	(useEffect(() => {
		Animated.timing(animHeight, {
			toValue: height,
			duration: 220,
			easing: Easing.out(Easing.cubic),
			useNativeDriver: false,
		}).start();
	}),
		[height, animHeight]);
	return (
		<Animated.View
			style={[
				styles.panel,
				{
					height: animHeight,
					bottom: bottomOffset,
				},
				style,
			]}
		>
			{children}
		</Animated.View>
	);
};

const styles = StyleSheet.create({
	panel: {
		position: "absolute",
		left: 0,
		right: 0,

		borderTopLeftRadius: 22,
		borderTopRightRadius: 22,
		overflow: "hidden",
		backgroundColor: "#FFFFFF",
		shadowOpacity: 0.12,
		shadowRadius: 10,
		shadowOffset: { width: 0, height: -4 },
		elevation: 6,
	},
});
