import os
import notion_client
from datetime import datetime, time
from zoneinfo import ZoneInfo # Recommended for handling timezones

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
    Fetches the Notion page created today, and before 8 AM local time,
    updates its 'Status' based on the number of unchecked workout checkboxes.
    """
    try:
        # --- 1. TIME CHECK: Stop execution if it's 8 AM or later ---
        now_local = datetime.now(LOCAL_TIMEZONE)
        if now_local.time() >= time(8, 0, tzinfo=LOCAL_TIMEZONE):
            print(f"Script stopped: Current time ({now_local.strftime('%H:%M')}) is past 8:00 AM.")
            return

        notion = notion_client.Client(auth=NOTION_KEY)

        # --- 2. FILTER: Get only pages created today ---
        # Get the start of today in your local timezone
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

        # Assuming you only want to update the first page found for today
        page = pages_to_update[0]
        page_id = page["id"]
        properties = page["properties"]

        unchecked_count = 0
        for prop_name in CHECKBOX_PROPERTIES:
            prop_data = properties.get(prop_name)
            # Check if the property exists, is a checkbox, and is unchecked
            if prop_data and prop_data["type"] == "checkbox" and not prop_data["checkbox"]:
                unchecked_count += 1

        new_status = ""
        if unchecked_count == 0:
            new_status = "Green"
        elif unchecked_count <= 2:
            new_status = "Orange"
        else: # unchecked_count > 2
            new_status = "Red"

        # Check if an update is needed to avoid unnecessary API calls
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
        # It's helpful to print the error to know what went wrong
        print(f"An error occurred: {e}")
        return

if __name__ == "__main__":
    main()
