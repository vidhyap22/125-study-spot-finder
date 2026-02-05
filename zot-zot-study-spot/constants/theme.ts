// app/constants/theme.ts
import { Platform } from "react-native";

export const Brand = {
	purple: "#5438DC",
	dark_purple: "#3d29a2",
	white: "#FFFFFF",
	black: "#1a191a",
};

const shared = {
	brand: Brand.purple,

	// surfaces
	surface: Brand.white,
	surfaceVariant: "rgb(255, 251, 251)",

	// text
	text: "#11181C",
	textOnBrand: Brand.white,

	// outlines / dividers
	outline: "rgba(0,0,0,0.15)",
	outlineSoft: "rgba(0,0,0,0.06)",

	// tab colors
	tabActive: Brand.white,
	tabInactive: "rgba(255,255,255,0.7)",

	// shadows
	shadow: Brand.black,
};

export const Colors = {
	light: {
		...shared,

		// you can add more as you grow:
		background: Brand.white,
	},
	dark: {
		...shared,

		// darkmode?
		background: "#151718",
		surface: "#1C1D20",
		surfaceVariant: "#23252A",
		text: "#ECEDEE",
		outline: "rgba(255,255,255,0.18)",
		outlineSoft: "rgba(255,255,255,0.10)",
	},
};

export const Fonts = Platform.select({
	ios: {
		sans: "system-ui",
		serif: "ui-serif",
		rounded: "ui-rounded",
		mono: "ui-monospace",
	},
	default: {
		sans: "normal",
		serif: "serif",
		rounded: "normal",
		mono: "monospace",
	},
	web: {
		sans: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
		serif: "Georgia, 'Times New Roman', serif",
		rounded: "'SF Pro Rounded', 'Hiragino Maru Gothic ProN', Meiryo, 'MS PGothic', sans-serif",
		mono: "SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace",
	},
});
