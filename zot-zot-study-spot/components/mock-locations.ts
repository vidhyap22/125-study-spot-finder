import type { LocationResult } from "@/components/types";

export const MOCK_LOCATIONS: LocationResult[] = [
	{
		id: "langson",
		title: "Langson Library",
		distanceText: "0.2 mi",
		printerAvailable: true,
		isIndoors: true,
		spaces: [
			{
				id: "langson-quiet",
				title: "4th Floor Quiet Study",
				capacity: 120,
				techEnhanced: false,
				environment: "indoors",
				reservable: false, // floor
			},
			{
				id: "langson-computers",
				title: "Technology Commons",
				capacity: 80,
				techEnhanced: true,
				environment: "indoors",
				reservable: false, // open area
			},
			{
				id: "langson-group",
				title: "Group Study Rooms",
				capacity: 36,
				techEnhanced: true,
				environment: "indoors",
				reservable: true, // specific rooms
			},
		],
	},

	{
		id: "science-library",
		title: "Science Library",
		distanceText: "0.4 mi",
		printerAvailable: true,
		isIndoors: true,
		spaces: [
			{
				id: "sci-silent",
				title: "Science 501",
				capacity: 60,
				techEnhanced: false,
				environment: "indoors",
				reservable: false,
			},
			{
				id: "sci-open",
				title: "Science Library Floor 2",
				capacity: 140,
				techEnhanced: true,
				environment: "indoors",
				reservable: false,
			},
		],
	},

	{
		id: "student-center",
		title: "Student Center Terrace",
		distanceText: "700 ft",
		printerAvailable: false,
		isOutdoors: true,
		spaces: [
			{
				id: "sc-patio",
				title: "Outdoor Patio Tables",
				capacity: 90,
				techEnhanced: false,
				environment: "outdoors",
				reservable: false,
			},
			{
				id: "sc-covered",
				title: "Covered Lounge Area",
				capacity: 45,
				techEnhanced: true,
				environment: "outdoors",
				reservable: false,
			},
		],
	},

	{
		id: "engineering-hall",
		title: "Engineering Hall",
		distanceText: "0.6 mi",
		printerAvailable: true,
		isIndoors: true,
		spaces: [
			{
				id: "eng-lab",
				title: "Computer Lab",
				capacity: 55,
				techEnhanced: true,
				environment: "indoors",
				reservable: false,
			},
			{
				id: "eng-lounge",
				title: "Student Lounge",
				capacity: 70,
				techEnhanced: false,
				environment: "indoors",
				reservable: false,
			},
		],
	},

	{
		id: "ald-rich-park",
		title: "Aldrich Park",
		distanceText: "0.1 mi",
		printerAvailable: false,
		isOutdoors: true,
		spaces: [
			{
				id: "park-benches",
				title: "Shaded Bench Circle",
				capacity: 50,
				techEnhanced: false,
				environment: "outdoors",
				reservable: false,
			},
			{
				id: "park-lawn",
				title: "Open Lawn",
				capacity: 200,
				techEnhanced: false,
				environment: "outdoors",
				reservable: false,
			},
		],
	},
];
