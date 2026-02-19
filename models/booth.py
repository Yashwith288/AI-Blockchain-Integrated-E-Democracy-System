from supabase_db.db import fetch_all

BOOTHS_TABLE = "booths"

def get_booths_by_constituency(constituency_id: str):
    """
    Returns all booths belonging to a constituency
    """
    return fetch_all(
        BOOTHS_TABLE,
        {"constituency_id": constituency_id}
    )
