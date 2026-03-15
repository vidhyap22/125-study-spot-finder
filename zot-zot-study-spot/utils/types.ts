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
	floor: string;
	traffic: string | null;
};

export type LocationResult = {
	id: string;
	title: string;
	distanceText: string;
	printerAvailable?: boolean;
	isIndoors?: boolean;
	isOutdoors?: boolean;
	spaces: StudySpace[];
	latitude:number;
	longitude:number;
};
