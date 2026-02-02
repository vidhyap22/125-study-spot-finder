"""
update_availability.py - Scrape room availability and update database
Run this script periodically to keep availability data fresh
"""

import subprocess
import sqlite3
from pathlib import Path
from datetime import datetime
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "utils"))

from json_to_db import (
    load_json, 
    insert_room_availability,
    ROOM_AVAILABILITY_JSON,
    DB_PATH
)


def clear_old_availability(cursor):
    """Delete all existing availability data"""
    cursor.execute("DELETE FROM room_availability")
    deleted = cursor.rowcount
    print(f"🗑️  Cleared {deleted} old availability records")


def scrape_availability():
    """Run the scraping script"""
    print("🕷️  Starting availability scraper...")
    
    scraper_path = BASE_DIR / "utils" / "room_availability_scraping.py"
    
    try:
        result = subprocess.run(
            ["python", str(scraper_path)],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Scraping failed: {e}")
        print(e.stderr)
        return False


def update_database():
    """Update database with newly scraped data"""
    print("📊 Updating database...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Clear old data
        clear_old_availability(cursor)
        
        # Insert new data
        total_slots = 0
        for json_file in ROOM_AVAILABILITY_JSON:
            if json_file.exists():
                print(f"Processing {json_file.name}...")
                room_availability = load_json(json_file)
                insert_room_availability(cursor, room_availability)
                
                # Count total slots
                for room_id, slots in room_availability.items():
                    total_slots += len(slots)
                
                print(f"✅ Inserted {len(room_availability)} rooms from {json_file.name}")
            else:
                print(f"⚠️  {json_file.name} not found, skipping...")
        
        conn.commit()
        print(f"✅ Database updated with {total_slots} total time slots")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Database update failed: {e}")
        raise
    finally:
        conn.close()


def main():
    print("="*60)
    print(f"🔄 AVAILABILITY UPDATE STARTED")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Step 1: Scrape fresh data
    if not scrape_availability():
        print("❌ Update failed: scraping error")
        return
    
    print()
    
    # Step 2: Update database
    try:
        update_database()
    except Exception as e:
        print(f"❌ Update failed: {e}")
        return
    
    print()
    print("="*60)
    print("✅ AVAILABILITY UPDATE COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()