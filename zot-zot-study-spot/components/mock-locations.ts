import type { LocationResult, StudySpace } from "@/components/types";

/** ---------- Raw shapes (match your real data) ---------- */
type RawRoom = {
	id: number;
	name: string;
	capacity: number;
	must_reserve: boolean;
	tech_enhanced: boolean;
	building_id: "SLIB" | "LLIB" | "GSC" | "ALP" | "MLTM";
	is_indoor: boolean;
	is_talking_allowed: boolean;
};

type RawLocationInfo = {
	name: string;
	has_printer: boolean;
	opening_time: string; // "08:00"
	closing_time: string; // "22:00"
	latitude: number;
	longitude: number;
};

/** ---------- Realistic mock “API” data ---------- */
export const RAW_LOCATIONS: Record<string, RawLocationInfo> = {
	SLIB: {
		name: "Science Library",
		has_printer: true,
		opening_time: "08:00",
		closing_time: "22:00",
		latitude: 33.645751466897906,
		longitude: -117.84655896516696,
	},
	LLIB: {
		name: "Langson Library",
		has_printer: false,
		opening_time: "08:00",
		closing_time: "22:00",
		latitude: 33.64725208711623,
		longitude: -117.8409255543131,
	},
	GSC: {
		name: "Gateway Study Center",
		has_printer: true,
		opening_time: "08:00",
		closing_time: "22:00",
		latitude: 33.64753724953823,
		longitude: -117.8417469762085,
	},
	ALP: {
		name: "Anteater Learning Pavilion",
		has_printer: true,
		opening_time: "08:00",
		closing_time: "22:00",
		latitude: 33.64718037556207,
		longitude: -117.84455436965455,
	},
	MLTM: {
		name: "Multimedia Resources Center",
		has_printer: false,
		opening_time: "08:00",
		closing_time: "22:00",
		latitude: 33.645751466897906, // you had same coords as SLIB in your snippet—keeping for now
		longitude: -117.84655896516696,
	},
};

const RAW_ROOMS: RawRoom[] = [
	// --- Science Library (SLIB) ---
	{ id: 111031, name: "Science 277", capacity: 6, must_reserve: true, tech_enhanced: true, building_id: "SLIB", is_indoor: true, is_talking_allowed: true },
	{ id: 44667, name: "Science 371", capacity: 8, must_reserve: true, tech_enhanced: true, building_id: "SLIB", is_indoor: true, is_talking_allowed: true },
	{ id: 44668, name: "Science 402", capacity: 4, must_reserve: true, tech_enhanced: false, building_id: "SLIB", is_indoor: true, is_talking_allowed: true },
	{ id: 44669, name: "Science 410", capacity: 6, must_reserve: true, tech_enhanced: false, building_id: "SLIB", is_indoor: true, is_talking_allowed: true },
	{ id: 44672, name: "Science 476", capacity: 4, must_reserve: true, tech_enhanced: false, building_id: "SLIB", is_indoor: true, is_talking_allowed: true },

	// --- Anteater Learning Pavilion (ALP) ---
	{ id: 34681, name: "ALP 2210", capacity: 6, must_reserve: true, tech_enhanced: false, building_id: "ALP", is_indoor: true, is_talking_allowed: true },
	{ id: 34680, name: "ALP 2510", capacity: 10, must_reserve: true, tech_enhanced: false, building_id: "ALP", is_indoor: true, is_talking_allowed: true },
	{ id: 34682, name: "ALP 2610", capacity: 10, must_reserve: true, tech_enhanced: false, building_id: "ALP", is_indoor: true, is_talking_allowed: true },
	{ id: 34683, name: "ALP 2710", capacity: 6, must_reserve: true, tech_enhanced: false, building_id: "ALP", is_indoor: true, is_talking_allowed: true },

	// --- Langson (LLIB) ---
	{ id: 44696, name: "Langson 380", capacity: 6, must_reserve: true, tech_enhanced: false, building_id: "LLIB", is_indoor: true, is_talking_allowed: true },
	{ id: 44697, name: "Langson 382", capacity: 6, must_reserve: true, tech_enhanced: false, building_id: "LLIB", is_indoor: true, is_talking_allowed: true },
	{ id: 44698, name: "Langson 386", capacity: 4, must_reserve: true, tech_enhanced: false, building_id: "LLIB", is_indoor: true, is_talking_allowed: true },
	{ id: 44702, name: "Langson 394", capacity: 4, must_reserve: true, tech_enhanced: false, building_id: "LLIB", is_indoor: true, is_talking_allowed: true },

	// --- Multimedia (MLTM) ---
	{
		id: 44717,
		name: "Study room 172",
		capacity: 4,
		must_reserve: true,
		tech_enhanced: false,
		building_id: "MLTM",
		is_indoor: true,
		is_talking_allowed: true,
	},
	{ id: 44718, name: "Study room 173", capacity: 7, must_reserve: true, tech_enhanced: true, building_id: "MLTM", is_indoor: true, is_talking_allowed: true },
	{
		id: 59309,
		name: "Study room 174",
		capacity: 2,
		must_reserve: true,
		tech_enhanced: false,
		building_id: "MLTM",
		is_indoor: true,
		is_talking_allowed: true,
	},

	// --- Gateway Study Center (GSC) ---
	{ id: 44704, name: "Gateway 2101", capacity: 4, must_reserve: true, tech_enhanced: false, building_id: "GSC", is_indoor: true, is_talking_allowed: true },
	{ id: 44705, name: "Gateway 2102", capacity: 4, must_reserve: true, tech_enhanced: false, building_id: "GSC", is_indoor: true, is_talking_allowed: true },
	{ id: 44708, name: "Gateway 2105", capacity: 4, must_reserve: true, tech_enhanced: false, building_id: "GSC", is_indoor: true, is_talking_allowed: true },
];

/** ---------- Helpers: raw -> UI types ---------- */
function toStudySpace(r: RawRoom): StudySpace {
	return {
		id: String(r.id),
		title: r.name,
		capacity: r.capacity,
		techEnhanced: r.tech_enhanced,
		environment: r.is_indoor ? "indoors" : "outdoors",
		reservable: r.must_reserve,
		talkingAllowed: r.is_talking_allowed,
	};
}

// Add some realistic “public/open” areas per building (not in your API list, but matches UX)
function publicAreasFor(buildingId: string): StudySpace[] {
	switch (buildingId) {
		case "SLIB":
			return [
				{
					id: "SLIB-floor2",
					title: "Science Library – Floor 2 (Open Study)",
					capacity: 80,
					techEnhanced: false,
					environment: "indoors",
					reservable: false,
					talkingAllowed: true,
				},
				{
					id: "SLIB-floor4",
					title: "Science Library – Floor 4 (Quiet Zone)",
					capacity: 60,
					techEnhanced: false,
					environment: "indoors",
					reservable: false,
					talkingAllowed: false,
				},
			];
		case "LLIB":
			return [
				{
					id: "LLIB-floor2",
					title: "Langson – Floor 2 (Open Study)",
					capacity: 100,
					techEnhanced: false,
					environment: "indoors",
					reservable: false,
					talkingAllowed: true,
				},
				{
					id: "LLIB-floor4",
					title: "Langson – Floor 4 (Quiet Study)",
					capacity: 70,
					techEnhanced: false,
					environment: "indoors",
					reservable: false,
					talkingAllowed: false,
				},
			];
		case "GSC":
			return [
				{
					id: "GSC-lounge",
					title: "Gateway – Main Lounge",
					capacity: 60,
					techEnhanced: true,
					environment: "indoors",
					reservable: false,
					talkingAllowed: false,
				},
			];
		case "ALP":
			return [
				{
					id: "ALP-atrium",
					title: "ALP – Atrium Tables",
					capacity: 50,
					techEnhanced: false,
					environment: "indoors",
					reservable: false,
					talkingAllowed: true,
				},
			];
		case "MLTM":
			return [
				{
					id: "MLTM-reading",
					title: "Multimedia – Reading Area",
					capacity: 25,
					techEnhanced: true,
					environment: "indoors",
					reservable: false,
					talkingAllowed: true,
				},
			];
		default:
			return [];
	}
}

function toLocationResult(buildingId: keyof typeof RAW_LOCATIONS, distanceText: string): LocationResult {
	const info = RAW_LOCATIONS[buildingId];

	const reservableRooms = RAW_ROOMS.filter((r) => r.building_id === buildingId).map(toStudySpace);
	const publicAreas = publicAreasFor(buildingId);

	const spaces = [...publicAreas, ...reservableRooms];

	return {
		id: buildingId, // nice: matches building_id
		title: info.name,
		distanceText,
		printerAvailable: info.has_printer,
		isIndoors: true, // these buildings are indoor locations
		isOutdoors: false,

		// Your UI expects this
		spaces,

		// Optional extras (won’t break anything if your type allows them later)
		// openingTime: info.opening_time,
		// closingTime: info.closing_time,
		// latitude: info.latitude,
		// longitude: info.longitude,
	};
}

/** ---------- Exported UI mock ---------- */
export const MOCK_LOCATIONS: LocationResult[] = [
	toLocationResult("SLIB", "0.4 mi"),
	toLocationResult("LLIB", "0.2 mi"),
	toLocationResult("GSC", "0.3 mi"),
	toLocationResult("ALP", "0.5 mi"),
	toLocationResult("MLTM", "0.6 mi"),
];


export const MOCK_MARKERS: RawLocationInfo[] = [
	{
		name: "Science Library",
		has_printer: true,
		opening_time: "08:00",
		closing_time: "22:00",
		latitude: 33.645751466897906,
		longitude: -117.84655896516696,
	},
	{
		name: "Langson Library",
		has_printer: false,
		opening_time: "08:00",
		closing_time: "22:00",
		latitude: 33.64725208711623,
		longitude: -117.8409255543131,
	},
	{
		name: "Gateway Study Center",
		has_printer: true,
		opening_time: "08:00",
		closing_time: "22:00",
		latitude: 33.64753724953823,
		longitude: -117.8417469762085,
	},
	{
		name: "Anteater Learning Pavilion",
		has_printer: true,
		opening_time: "08:00",
		closing_time: "22:00",
		latitude: 33.64718037556207,
		longitude: -117.84455436965455,
	},
	{
		name: "Multimedia Resources Center",
		has_printer: false,
		opening_time: "08:00",
		closing_time: "22:00",
		latitude: 33.645751466897906, // you had same coords as SLIB in your snippet—keeping for now
		longitude: -117.84655896516696,
	}
];