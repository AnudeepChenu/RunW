# New, correct filter
filter={
    "timestamp": "created_time", # <-- Correct way to target the timestamp
    "created_time": {
        "on_or_after": start_of_today.isoformat()
    }
}
