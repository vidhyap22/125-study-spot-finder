import React, { createContext, useContext, useMemo, useState } from "react";

export type SelectedSpot = {
	locationId: string;
	locationTitle: string;
	spaceId: string;
	spaceTitle: string;
	kind: "reservable" | "public";
};

type SessionState = {
	selectedSpot: SelectedSpot | null;
	setSelectedSpot: (spot: SelectedSpot | null) => void;
	clearSelectedSpot: () => void;
};

const SessionContext = createContext<SessionState | null>(null);

export function SessionProvider({ children }: { children: React.ReactNode }) {
	const [selectedSpot, setSelectedSpot] = useState<SelectedSpot | null>(null);

	const value = useMemo(
		() => ({
			selectedSpot,
			setSelectedSpot,
			clearSelectedSpot: () => setSelectedSpot(null),
		}),
		[selectedSpot],
	);

	return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

export function useSession() {
	const ctx = useContext(SessionContext);
	if (!ctx) throw new Error("useSession must be used inside <SessionProvider>");
	return ctx;
}
