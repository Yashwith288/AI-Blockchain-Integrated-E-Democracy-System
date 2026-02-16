from supabase_db.db import fetch_one, insert_record, update_record
from utils.helpers import generate_uuid, utc_now

TABLE = "constituency_ai_briefs"


def get_brief(constituency_id: str):
    return fetch_one(TABLE, {"constituency_id": constituency_id})


def save_brief(constituency_id: str, text: str):
    existing = get_brief(constituency_id)

    payload = {
        "constituency_id": constituency_id,
        "summary_text": text,
        "generated_at": utc_now().isoformat()
    }

    if existing:
        return update_record(TABLE, {"id": existing["id"]}, payload, use_admin=True)
    else:
        payload["id"] = generate_uuid()
        return insert_record(TABLE, payload, use_admin=True)
