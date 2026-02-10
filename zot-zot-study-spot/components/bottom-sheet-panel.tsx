import React from "react";
import { StyleSheet, View } from "react-native";
import type { StyleProp, ViewStyle } from "react-native";

type Props = {
	height: number;
	bottomOffset?: number;
	style?: StyleProp<ViewStyle>;
	children: React.ReactNode;
};

export const BottomSheetPanel = ({
   height,
   bottomOffset = 0,
   style,
   children,
}: Props) => {
   return (
      <View style={[styles.panel, { height, marginBottom: bottomOffset }, style]}>
         {children}
      </View>
   );
};


const styles = StyleSheet.create({
	panel: {
		position: "absolute",
		left: 0,
		right: 0,
		bottom: 0,
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
