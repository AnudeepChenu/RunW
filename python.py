import os
import notion_client
from datetime import datetime, time
from zoneinfo import ZoneInfo

# --- CONFIGURATION ---
NOTION_KEY = os.environ.get("NOTION_API_KEY")
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")
CHECKBOX_PROPERTIES = [
    "Bicep", "Hammer", "Tricep", "Shoulder",
    "Chest", "Russian", "Plank"
]
# Define your local timezone (India Standard Time)
LOCAL_TIMEZONE = ZoneInfo("Asia/Kolkata")

def main():
    """
    Fetches the Notion page created today and updates its 'Status' based on
    the number of unchecked workout checkboxes. It will run even after 8 AM.
    """
    try:
        # --- 1. TIME CHECK: Warns but does not stop execution ---
        now_local = datetime.now(LOCAL_TIMEZONE)
        if now_local.time() >= time(8, 0, tzinfo=LOCAL_TIMEZONE):
            # This block now only prints a warning and allows the script to continue.
            print(f"Warning: Current time ({now_local.strftime('%H:%M')}) is past the 8:00 AM deadline.")
        
        # The script will now proceed regardless of the time.
        notion = notion_client.Client(auth=NOTION_KEY)

        # --- 2. FILTER: Get only pages created today ---
        start_of_today = datetime.combine(now_local.date(), time.min, tzinfo=LOCAL_TIMEZONE)

        response = notion.databases.query(
            database_id=DATABASE_ID,
            filter={
                "property": "Created time",
                "created_time": {
                    "on_or_after": start_of_today.isoformat()
                }
            }
        )

        pages_to_update = response.get("results")

        if not pages_to_update:
            print("No page found that was created today.")
            return

        page = pages_to_update[0]
        page_id = page["id"]
        properties = page["properties"]

        unchecked_count = 0
        for prop_name in CHECKBOX_PROPERTIES:
            prop_data = properties.get(prop_name)
            if prop_data and prop_data["type"] == "checkbox" and not prop_data["checkbox"]:
                unchecked_count += 1

        new_status = ""
        if unchecked_count == 0:
            new_status = "Green"
        elif unchecked_count <= 2:
            new_status = "Orange"
        else:
            new_status = "Red"
        
        current_status_data = properties.get("Status", {}).get("select")
        current_status = current_status_data["name"] if current_status_data else ""

        if new_status and new_status != current_status:
            notion.pages.update(
                page_id=page_id,
                properties={
                    "Status": {
                        "select": {
                            "name": new_status
                        }
                    }
                }
            )
            print(f"Page status updated to '{new_status}'.")
        else:
            print("Page status is already up-to-date. No changes made.")

    except Exception as e:
        print(f"An error occurred: {e}")
        return

if __name__ == "__main__":
    main()
