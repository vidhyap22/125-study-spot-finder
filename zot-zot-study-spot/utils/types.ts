export type StudySpace = {
	id: string;
	title: string;
	capacity: number;
	techEnhanced?: boolean;
	environment: "indoors" | "outdoors";
	reservable: boolean;
	talkingAllowed: boolean;
	locationId: string;
	locationName: string;
};

export type LocationResult = {
	id: string;
	title: string;
	distanceText: string;
	printerAvailable?: boolean;
	isIndoors?: boolean;
	isOutdoors?: boolean;
	spaces: StudySpace[];
};
