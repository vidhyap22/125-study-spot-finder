import { Filters } from "@/components/filter-bar";
import type { StudySpace, LocationResult } from "./types";

export type SearchRequest = {
	user_id: string;
	filters?: Record<string, any>;
	debug?: boolean;
};

export type SearchResponse = {
	success: true;
	count: number;
	data: LocationResult[] | StudySpace[] | any[];
};

export type ApiFailure = { success: false; error: string };
export type ApiResponse<T> = T | ApiFailure;

export type SearchFilterTelemetryReq = {
	user_id: string;
	filters: Record<string, any>;
	debug?: boolean;
};

export type StudySessionTelemetryReq = {
	user_id: string;
	session: {
		study_space_id: string | number;
		building_id: string;
		started_at: string;
		ended_at: string;
		start_date: string;
		end_date: string;

		[k: string]: any;
	};
	debug?: boolean;
};

export type AddBookmarkReq = {
	user_id: string;
	bookmark: {
		study_space_id: string | number;
		building_id: string | number; // SQL has int
		created_at: string;
		[k: string]: any;
	};
	debug?: boolean;
};

export type DeleteBookmarkReq = {
	user_id: string;
	bookmark: {
		study_space_id: string | number;
		[k: string]: any;
	};
	debug?: boolean;
};

export type AddUserReq = {
	user_id: string;
	info: {
		created_at: string;
		[k: string]: any;
	};
	debug?: boolean;
};

export type SpotViewReq = {
	user_id: string;
	view: {
		study_space_id: string | number;
		building_id: string | number;
		opened_at: string;

		// optional SQL fields:
		closed_at?: string;
		dwell_ms?: number;
		source?: string;
		list_rank?: number;

		[k: string]: any;
	};
	debug?: boolean;
};

export type SpotFeedbackReq = {
	user_id: string;
	feedback: {
		study_space_id: string | number;
		building_id: string | number;
		rating: number;
		updated_at: string;

		[k: string]: any;
	};
	debug?: boolean;
};

export const API_BASE_URL = "http://192.168.0.85:3000"; // Currently copy pasting from output after starting api.py

// ---- Helpers ----

type FetchOpts = {
	method?: "GET" | "POST";
	path: string;
	body?: any;
	timeoutMs?: number;
	headers?: Record<string, string>;
};

async function fetchJson<T>({ method = "GET", path, body, timeoutMs = 15000, headers }: FetchOpts): Promise<T> {
	const controller = new AbortController();
	const t = setTimeout(() => controller.abort(), timeoutMs);

	try {
		const res = await fetch(`${API_BASE_URL}${path}`, {
			method,
			headers: {
				Accept: "application/json",
				...(method === "POST" ? { "Content-Type": "application/json" } : {}),
				...(headers ?? {}),
			},
			body: method === "POST" ? JSON.stringify(body ?? {}) : undefined,
			signal: controller.signal,
		});

		const text = await res.text();
		const isJson = text.trim().startsWith("{") || text.trim().startsWith("[");
		const data = (isJson && text.length ? JSON.parse(text) : text) as any;

		if (!res.ok) {
			const msg = (data && typeof data === "object" && data.error) || (typeof data === "string" ? data : `HTTP ${res.status}`);
			throw new Error(msg);
		}

		return data as T;
	} finally {
		clearTimeout(t);
	}
}

async function safe<T>(fn: () => Promise<T>): Promise<T | ApiFailure> {
	try {
		return await fn();
	} catch (e: any) {
		return { success: false, error: e?.message ?? "Network error" };
	}
}
export function groupJoinedRowsToLocationResults(rows: any[]): LocationResult[] {
	const byBuilding = new Map<string, LocationResult>();

	for (const row of rows) {
		const buildingId = String(row.building_id ?? row.locationId ?? row.location_id ?? "");
		if (!buildingId) continue;

		// Determine space indoor status from backend field
		const spaceIsIndoor = !!(row.indoor ?? row.is_indoor ?? row.isIndoors);

		let building = byBuilding.get(buildingId);

		if (!building) {
			building = {
				id: buildingId,
				title: String(row.building_name ?? row.locationName ?? row.location_title ?? row.buildingTitle ?? ""),
				distanceText: String(row.distance_text ?? row.distanceText ?? "N/A"),
				printerAvailable: row.has_printer != null ? !!row.has_printer : undefined,

				// initialize to false
				isIndoors: false,
				isOutdoors: false,

				spaces: [],
			};

			byBuilding.set(buildingId, building);
		}

		// Add the space
		building.spaces.push(normalizeStudySpace(row));

		// Update building-level flags
		if (spaceIsIndoor) {
			building.isIndoors = true;
		} else {
			building.isOutdoors = true;
		}
	}

	return Array.from(byBuilding.values());
}
export function normalizeStudySpace(row: any): StudySpace {
	const isIndoor = !!(row.is_indoor ?? row.isIndoors ?? row.environment === "indoors");
	return {
		id: String(row.study_space_id ?? row.id),
		title: String(row.name ?? row.title ?? ""),
		capacity: Number(row.capacity ?? 0),
		techEnhanced: row.tech_enhanced != null ? !!row.tech_enhanced : row.techEnhanced,
		environment: isIndoor ? "indoors" : "outdoors",
		reservable: row.must_reserve != null ? !!row.must_reserve : !!row.reservable,
		talkingAllowed: row.is_talking_allowed != null ? !!row.is_talking_allowed : !!row.talkingAllowed,
		locationId: String(row.building_id ?? row.locationId ?? ""),
		locationName: String(row.building_name ?? row.locationName ?? row.location_title ?? ""),
	};
}

export function normalizeLocationResult(obj: any): LocationResult {
	// If backend already returns LocationResult shape, this is basically a no-op.
	const spacesRaw = obj.spaces ?? obj.data ?? obj.study_spaces ?? [];
	const spaces = Array.isArray(spacesRaw) ? spacesRaw.map(normalizeStudySpace) : [];
	return {
		id: String(obj.building_id ?? obj.id ?? ""),
		title: String(obj.name ?? obj.title ?? ""),
		distanceText: String(obj.distanceText ?? obj.distance_text ?? "N/A"),
		printerAvailable: obj.has_printer != null ? !!obj.has_printer : obj.printerAvailable,
		isIndoors: obj.isIndoors ?? undefined,
		isOutdoors: obj.isOutdoors ?? undefined,
		spaces,
	};
}

export function toApiFilters(f: Filters) {
	const api: Record<string, any> = {};

	if (typeof f.capacity === "number") {
		const cap = f.capacity;

		if (cap <= 4) api.capacity_range = "1-4";
		else if (cap <= 10) api.capacity_range = "5-10";
		else if (cap <= 20) api.capacity_range = "11-20";
		else api.capacity_range = "20+";
	}

	if (typeof f.techEnhanced === "boolean" && f.techEnhanced) {
		api.tech_enhanced = f.techEnhanced;
	}

	if (f.environment === "indoors") {
		api.indoor = true;
	} else if (f.environment === "outdoors") {
		api.indoor = false;
	}

	return api;
}

// ---- Endpoint functions  ----

export async function apiIndex(): Promise<string | ApiFailure> {
	return safe(async () => {
		const res = await fetch(`${API_BASE_URL}/`);
		if (!res.ok) throw new Error(`HTTP ${res.status}`);
		return await res.text();
	});
}

// GET /api/health
export async function apiHealth(): Promise<{ success: true; message: string } | ApiFailure> {
	return safe(() => fetchJson<{ success: true; message: string }>({ path: "/api/health", method: "GET" }));
}

// GET /api/buildings
export async function apiGetBuildings(): Promise<SearchResponse | ApiFailure> {
	const result = await safe(() =>
		fetchJson<SearchResponse>({
			path: "/api/buildings",
			method: "GET",
		}),
	);
	if ((result as any).success === false) return result as ApiFailure;

	const ok = result as SearchResponse;
	if (ok.success && Array.isArray(ok.data)) {
		// Try to detect "already grouped by building" vs "flat study spaces"
		const looksLikeLocation = ok.data.length === 0 ? false : "spaces" in (ok.data[0] as any) || "building_id" in (ok.data[0] as any);
		if (looksLikeLocation) {
			ok.data = (ok.data as any[]).map(normalizeLocationResult);
		} else {
			// flat list -> put into a single bucket or keep as-is; here we keep as-is
			ok.data = ok.data.map((x: any) => x);
		}
	}
	console.log(ok.data, "building info on front end");
	return ok;
}

// POST /api/search: TODO: change to normalize to study space type instead of location type
export async function apiSearchSpaces(req: SearchRequest): Promise<SearchResponse | ApiFailure> {
	const result = await safe(() =>
		fetchJson<SearchResponse>({
			path: "/api/search",
			method: "POST",
			body: {
				user_id: req.user_id,
				filters: req.filters ?? {},
				debug: req.debug ?? false,
			},
		}),
	);

	if ((result as any).success === false) return result as ApiFailure;

	const ok = result as SearchResponse;

	if (ok.success && Array.isArray(ok.data)) {
		const rows = ok.data as any[];

		// Detect "joined flat rows" from your /api/search
		const looksLikeJoinedRow =
			rows.length > 0 && ("study_space_id" in rows[0] || "id" in rows[0]) && ("building_id" in rows[0] || "building_name" in rows[0]);

		// Detect "already grouped LocationResult"
		const looksLikeLocationResult = rows.length > 0 && "spaces" in rows[0];

		if (looksLikeLocationResult) {
			ok.data = rows.map(normalizeLocationResult);
		} else if (looksLikeJoinedRow) {
			ok.data = groupJoinedRowsToLocationResults(rows);
		} else {
			// fallback: keep raw
			ok.data = rows;
		}
	}

	return ok;
}
// POST /api/personal_model/search_filter
export async function apiStoreSearchFilter(req: SearchFilterTelemetryReq): Promise<{ success: true; received_filters: Record<string, any> } | ApiFailure> {
	return safe(() =>
		fetchJson({
			path: "/api/personal_model/search_filter",
			method: "POST",
			body: req,
		}),
	);
}

// POST /api/personal_model/study_session
export async function apiStoreStudySession(req: StudySessionTelemetryReq): Promise<{ success: true; received_session: any } | ApiFailure> {
	return safe(() =>
		fetchJson({
			path: "/api/personal_model/study_session",
			method: "POST",
			body: req,
		}),
	);
}

// POST /api/personal_model/add_bookmark
export async function apiAddBookmark(req: AddBookmarkReq): Promise<{ success: true; received_bookmark: any } | ApiFailure> {
	return safe(() =>
		fetchJson({
			path: "/api/personal_model/add_bookmark",
			method: "POST",
			body: req,
		}),
	);
}

// POST /api/personal_model/delete_bookmark
export async function apiDeleteBookmark(req: DeleteBookmarkReq): Promise<{ success: true; received_bookmark: any } | ApiFailure> {
	return safe(() =>
		fetchJson({
			path: "/api/personal_model/delete_bookmark",
			method: "POST",
			body: req,
		}),
	);
}

// POST /api/personal_model/spot_view
export async function apiStoreSpotView(req: SpotViewReq): Promise<{ success: true; received_view: any } | ApiFailure> {
	return safe(() =>
		fetchJson({
			path: "/api/personal_model/spot_view",
			method: "POST",
			body: req,
		}),
	);
}

// POST /api/personal_model/spot_feedback
export async function apiStoreSpotFeedback(req: SpotFeedbackReq): Promise<{ success: true; received_feedback: any } | ApiFailure> {
	return safe(() =>
		fetchJson({
			path: "/api/personal_model/spot_feedback",
			method: "POST",
			body: req,
		}),
	);
}

// POST /api/personal_model/add_user
export async function apiAddUser(req: AddUserReq): Promise<{ success: true; received_user: string } | ApiFailure> {
	return safe(() =>
		fetchJson({
			path: "/api/personal_model/add_user",
			method: "POST",
			body: req,
		}),
	);
}
