from playwright.sync_api import sync_playwright
import json
import re
import os 
from datetime import datetime

BASE_URL = "https://spaces.lib.uci.edu"
OUTPUT_DIR = "./data/scraped_info"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(f'{OUTPUT_DIR}/room_availability', exist_ok=True)

SCRAPING_JS_CODE_BLOCK = """
        () => {
            const results = {};

            function parseDateSafe(raw) {
                const match = raw.match(/(\\d{1,2}:\\d{2})(am|pm) .*?, (.*)$/);
                if (!match) return null;

                let [_, time, meridiem, datePart] = match;
                let [hour, minute] = time.split(":").map(Number);

                if (meridiem === "pm" && hour !== 12) hour += 12;
                if (meridiem === "am" && hour === 12) hour = 0;

                return new Date(`${datePart} ${hour}:${minute}`);
            }

            function toPacificISOString(date) {
                const options = {
                    timeZone: "America/Los_Angeles",
                    year: "numeric",
                    month: "2-digit",
                    day: "2-digit",
                    hour: "2-digit",
                    minute: "2-digit",
                    second: "2-digit",
                    hour12: false
                };

                const parts = new Intl.DateTimeFormat("en-US", options).formatToParts(date);
                const y = parts.find(p => p.type === "year").value;
                const m = parts.find(p => p.type === "month").value;
                const d = parts.find(p => p.type === "day").value;
                const h = parts.find(p => p.type === "hour").value;
                const min = parts.find(p => p.type === "minute").value;
                const s = parts.find(p => p.type === "second").value;

                const pacificDate = new Date(
                    date.toLocaleString("en-US", { timeZone: "America/Los_Angeles" })
                );
                const offsetMinutes = pacificDate.getTimezoneOffset();
                const offsetHours = Math.floor(Math.abs(offsetMinutes) / 60);
                const offsetMins = Math.abs(offsetMinutes) % 60;
                const sign = offsetMinutes <= 0 ? "+" : "-";
                const offsetStr =
                    sign +
                    String(offsetHours).padStart(2, "0") +
                    ":" +
                    String(offsetMins).padStart(2, "0");

                return `${y}-${m}-${d}T${h}:${min}:${s}${offsetStr}`;
            }

            const timelineBody = document.querySelector(".fc-timeline-body");
            if (!timelineBody) return results;

            const rows = timelineBody.querySelectorAll(
                "table.fc-scrollgrid-sync-table tbody tr"
            );

            rows.forEach(tr => {
                const laneTd = tr.querySelector("td.fc-timeline-lane.fc-resource");
                if (!laneTd) return;

                const resourceIdRaw = laneTd.dataset.resourceId;
                if (!resourceIdRaw) return;

                const roomId = parseInt(resourceIdRaw.split("_")[1]);
                if (isNaN(roomId)) return;

                const events = laneTd.querySelectorAll(
                    ".fc-timeline-events a.fc-timeline-event"
                );

                events.forEach(eventEl => {
                    const label = eventEl.getAttribute("aria-label") || eventEl.title;
                    if (!label) return;

                    const parts = label.split(" - ");
                    if (parts.length < 2) return;

                    const start = parseDateSafe(parts[0]);
                    if (!start || isNaN(start)) return;

                    const end = new Date(start.getTime() + 30 * 60 * 1000);

                    let isAvailable = null;
                    if (/unavailable/i.test(label)) isAvailable = false;
                    else if (/available/i.test(label)) isAvailable = true;
                    if (isAvailable === null) return;

                    if (!results[roomId]) results[roomId] = [];
                    results[roomId].push({
                        start: toPacificISOString(start),
                        end: toPacificISOString(end),
                        isAvailable
                    });
                });
            });

            return results;
        }
        """

def extract_space_id(url):
    match = re.search(r"/space/(\\d+)", url)
    return match.group(1) if match else None


def main():
    print(f"🕐 Starting availability scrape at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        locations = {
            "Science": 6580,
            "Langson": 6539,
            "Gateway": 6579,
            "Multimedia": 6581
        }

        for location, l_id in locations.items():
            try:
                page.goto(f"https://spaces.lib.uci.edu/spaces?lid={l_id}", timeout=60000)
                page.wait_for_selector(".fc-timeline-body")
                page.wait_for_selector(".fc-timeline-events a.fc-timeline-event", timeout=60000)

                data = page.evaluate(SCRAPING_JS_CODE_BLOCK)

                output_file = f"{OUTPUT_DIR}/room_availability/{location}_room_availability.json"
                
                # Write data (will replace if file exists)
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)

                print(f"✅ {location} availability saved ({len(data)} rooms)")
            except Exception as e:
                print(f"❌ Error scraping {location}: {e}")

        # ALP
        try:
            page.goto("https://scheduler.oit.uci.edu/reserve/Antcaves", timeout=60000)
            page.wait_for_selector(".fc-timeline-body")
            page.wait_for_selector(".fc-timeline-events a.fc-timeline-event", timeout=60000)

            data = page.evaluate(SCRAPING_JS_CODE_BLOCK)

            output_file = f"{OUTPUT_DIR}/room_availability/ALP_room_availability.json"
            
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            print(f"✅ ALP availability saved ({len(data)} rooms)")
        except Exception as e:
            print(f"❌ Error scraping ALP: {e}")

        browser.close()
    
    print(f"✅ Scraping completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()