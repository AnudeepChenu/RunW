import os
import notion_client
from datetime import datetime, timedelta, timezone

NOTION_KEY = os.environ.get("NOTION_KEY")
DATABASE_ID = os.environ.get("DATABASE_ID")
CHECKBOX_PROPERTIES = [
    "Bicep", "Hammer", "Tricep", "Shoulder",
    "Chest", "Russian", "Plank"
]
def main():
    try:
        notion = notion_client.Client(auth=NOTION_KEY)
        five_minutes_ago = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
        response = notion.databases.query(
            database_id=DATABASE_ID,
            filter={"timestamp": "last_edited_time", "last_edited_time": {"on_or_after": five_minutes_ago}}
        )
        pages_to_update = response.get("results")
        if not pages_to_update:
            return
        for page in pages_to_update:
            page_id = page["id"]
            properties = page["properties"]
            unchecked_count = 0
            for prop_name in CHECKBOX_PROPERTIES:
                if properties.get(prop_name) and properties[prop_name]["type"] == "checkbox":
                    if not properties[prop_name]["checkbox"]: # If the box is unchecked (False)
                        unchecked_count += 1
            new_status = ""
            if unchecked_count == 0:
                new_status = "Green"
            elif unchecked_count <= 2:
                new_status = "Orange"
            else: # unchecked_count > 2
                new_status = "Red"
            current_status = properties["Status"]["select"]["name"] if properties["Status"]["select"] else ""
            if new_status != current_status:
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
            else:
                return

    except Exception as e:
        return

if __name__ == "__main__":
    main()