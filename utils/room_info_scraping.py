from playwright.sync_api import sync_playwright
import json
import re
import os

BASE_URL = "https://spaces.lib.uci.edu"
ANTCAVES_URL = "https://scheduler.oit.uci.edu/reserve/Antcaves"

SCRAPING_JS_CODE_BLOCK = """
        () => {
            const rooms = [];
            const tbody = document.querySelector(
                "table.fc-datagrid-body.fc-scrollgrid-sync-table tbody"
            );
            if (!tbody) return rooms;

            tbody.querySelectorAll("tr").forEach(tr => {
                const td = tr.querySelector("td[data-resource-id]");
                if (!td) return;

                const id = parseInt(td.dataset.resourceId.split("_")[1]);

                const textEl = td.querySelector("span.fc-cell-text");
                if (!textEl) return;

                const fullText = textEl.textContent.trim();
                const tech_enhanced = /Tech Enhanced/i.test(fullText);

                const capMatch = fullText.match(/Capacity (\\d+)/i);
                const capacity = capMatch ? parseInt(capMatch[1]) : null;

                let name = fullText
                    .replace(/\\(Tech Enhanced\\)|\\(Capacity \\d+\\)/gi, "")
                    .split("-")[0]
                    .trim();

                rooms.push({
                    id,
                    name,
                    capacity,
                    tech_enhanced
                });
            });

            return rooms;
        }
"""

OUTPUT_DIR = "./data/room_info"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Building normalization rules
BUILDING_INFO = {
    "Langson": {
        "building_name": "Langson Library",
        "building_id": "LLIB"
    },
    "Science": {
        "building_name": "Science Library",
        "building_id": "SLIB"
    },
    "Multimedia": {
        "building_name": "Multimedia ResourcesCenter",
        "building_id": "MLTM"
    },
    "Gateway": {
        "building_name": "Gateway Study Center",
        "building_id": "GSC"
    },
    "ALP": {
        "building_name": "Anteater Learning Pavilion",
        "building_id": "ALP"
    }
}


def format_room(room, location_key):
    return {
        "id": room["id"],
        "name": f'{room["name"]}',
        "capacity": room["capacity"],
        "must_reserve": True,
        "tech_enhanced": room["tech_enhanced"],
        "building_id": BUILDING_INFO[location_key]["building_id"],
        "is_indoor": True,
        "is_talking_allowed": True
    }


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # Library locations (unchanged)
    locations = {
        "Science": 6580,
        "Langson": 6539,
        "Gateway": 6579,
        "Multimedia": 6581
    }

    # Scrape library rooms
    for location, lid in locations.items():
        page.goto(f"https://spaces.lib.uci.edu/spaces?lid={lid}", timeout=100000)
        page.wait_for_selector(".fc-timeline-body")
        page.wait_for_selector(".fc-datagrid-cell", timeout=100000)

        raw_rooms = page.evaluate(SCRAPING_JS_CODE_BLOCK)
        formatted_rooms = [
            format_room(r, location) for r in raw_rooms
        ]

        with open(f"{OUTPUT_DIR}/{location}_room_info.json", "w", encoding="utf-8") as f:
            json.dump(formatted_rooms, f, indent=4)

        print(f"{location} rooms saved: {len(formatted_rooms)}")

    # ALP (Antcaves)
    page.goto(ANTCAVES_URL, timeout=100000)
    page.wait_for_selector(".fc-timeline-body")

    alp_raw_rooms = page.evaluate(SCRAPING_JS_CODE_BLOCK)
    alp_formatted = [
        format_room(r, "ALP") for r in alp_raw_rooms
    ]

    with open(f"{OUTPUT_DIR}/ALP_room_info.json", "w", encoding="utf-8") as f:
        json.dump(alp_formatted, f, indent=4)

    print(f"ALP rooms saved: {len(alp_formatted)}")

    browser.close()
