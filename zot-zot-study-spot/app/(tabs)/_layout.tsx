import { Tabs } from "expo-router";
import React from "react";

import { HapticTab } from "@/components/haptic-tab";
import { IconSymbol } from "@/components/ui/icon-symbol";
import { FontAwesome6 } from "@expo/vector-icons";

import { Colors, Fonts } from "@/constants/theme";

export default function TabLayout() {
	const theme = Colors.light;

	return (
		<Tabs
			screenOptions={{
				headerShown: false,
				tabBarButton: HapticTab,

				tabBarStyle: {
					backgroundColor: theme.brand,
					height: 80,
					borderTopWidth: 0,

					shadowColor: theme.shadow,
					shadowOpacity: 0.2,
					shadowRadius: 6,
					shadowOffset: { width: 0, height: -4 },

					elevation: 0,
				},

				tabBarItemStyle: {
					paddingTop: 10,
				},

				tabBarActiveTintColor: theme.tabActive,
				tabBarInactiveTintColor: theme.tabInactive,

				tabBarLabelStyle: {
					fontWeight: "600",
					marginTop: 4,

					fontFamily: Fonts.sans ?? undefined,
				},

				tabBarLabelPosition: "below-icon",
			}}
		>
			<Tabs.Screen
				name="index"
				options={{
					title: "Explore",
					tabBarIcon: ({ color }) => <IconSymbol size={20} name="paperplane.fill" color={color} />,
				}}
			/>
			<Tabs.Screen
				name="bookmarks"
				options={{
					title: "Bookmarks",
					tabBarIcon: ({ color }) => <FontAwesome6 name="bookmark" size={20} color={color} />,
				}}
			/>
			<Tabs.Screen
				name="settings"
				options={{
					title: "Settings",
					tabBarIcon: ({ color }) => <FontAwesome6 name="gear" size={20} color={color} />,
				}}
			/>
		</Tabs>
	);
}
