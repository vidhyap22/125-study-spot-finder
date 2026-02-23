// types.ts (optional, or keep in the same file)
export type StudySpace = {
	id: string;
	title: string;
	capacity: number;
	techEnhanced?: boolean;
	environment: "indoors" | "outdoors";
	reservable: boolean;
	talkingAllowed: boolean;
};

export type LocationResult = {
	id: string;
	name: string;
	distanceText: string;
	has_printer?: boolean;
	opening_time:string;
	closing_time:string;
	longitude:number;
	lattidue:number;
	//isIndoors?: boolean; <- I think we should remove these two since this information is in StudySpace
	//isOutdoors?: boolean;
	//spaces: StudySpace[]; <- I temporarily took this out to test something but put it back after
							//recreating the json with a JOIN with study space to get their ids?
};
