from playwright.sync_api import sync_playwright
import json
import re

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
                    tech_enhanced,
                    location: null
                });
            });

            return rooms;
        }
        """
OUTPUT_DIR = "./data"
def extract_space_id(url):
    match = re.search(r"/space/(\d+)", url)
    return match.group(1) if match else None


def extract_antcaves_id(url):
    """
    Extract a stable numeric ID from Antcaves room URLs.
    Example:
    /reserve/antcave-12 → 12
    """
    match = re.search(r"(\d+)$", url)
    return int(match.group(1)) if match else None


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # LIBRARY LOCATIONS (with lid)

    locations = {
        "Science": 6580,
        "Langson": 6539,
        "Gateway": 6579,
        "Multimedia": 6581
    }

    for location, l_id in locations.items():
        page.goto(f"https://spaces.lib.uci.edu/spaces?lid={l_id}", timeout=100000)
        page.wait_for_selector(".fc-timeline-body")

        page.wait_for_selector(".fc-datagrid-cell", timeout=100000)

        data_rooms = page.evaluate(SCRAPING_JS_CODE_BLOCK)

        for r in data_rooms:
            r["location"] = location

        with open(f"{OUTPUT_DIR}/room_info/{location}_room_info.json", "w", encoding="utf-8") as f:
            json.dump(data_rooms, f, indent=4)

        print(f"{location} rooms:", data_rooms)


    # ALP Rooms

    page.goto(ANTCAVES_URL, timeout=100000)
    page.wait_for_selector(".fc-timeline-body")

    antcaves_rooms = page.evaluate(SCRAPING_JS_CODE_BLOCK)


    print(len(antcaves_rooms))
    for r in antcaves_rooms:
        r["location"] = "ALP"

    with open(f"{OUTPUT_DIR}/room_info/ALP_room_info.json", "w", encoding="utf-8") as f:
        json.dump(antcaves_rooms, f, indent=4)

    print("ALP rooms:", antcaves_rooms)

    browser.close()
