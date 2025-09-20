import os
import notion_client
from datetime import datetime, time
from zoneinfo import ZoneInfo

# --- CONFIGURATION (Global Scope) ---
NOTION_KEY = os.environ.get("NOTION_API_KEY")
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")
CHECKBOX_PROPERTIES = [
    "Bicep", "Hammer", "Tricep", "Shoulder",
    "Chest", "Russian", "Plank"
]
LOCAL_TIMEZONE = ZoneInfo("Asia/Kolkata")

# --- EXECUTION LOGIC (Inside the main function) ---
def main():
    """
    Fetches the Notion page created today and updates its 'Status' based on
    the number of unchecked workout checkboxes.
    """
    try:
        # All logic is now correctly placed inside the function
        now_local = datetime.now(LOCAL_TIMEZONE)
        if now_local.time() >= time(8, 0, tzinfo=LOCAL_TIMEZONE):
            print(f"Script stopped: Current time ({now_local.strftime('%H:%M')}) is past the 8:00 AM deadline.")
            return
        
        # This variable is now defined before it is used below
        start_of_today = datetime.combine(now_local.date(), time.min, tzinfo=LOCAL_TIMEZONE)

        notion = notion_client.Client(auth=NOTION_KEY)

        response = notion.databases.query(
            database_id=DATABASE_ID,
            filter={
                "timestamp": "created_time",
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

# --- SCRIPT ENTRY POINT ---
if __name__ == "__main__":
    main()
