BOOKINGS_LIST_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["bookingid"],
        "properties": {
            "bookingid": {"type": "integer"}
        }
    }
}
