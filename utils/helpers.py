import hashlib
import uuid
from datetime import date, datetime, timezone
import pytz
import secrets
import string


# -----------------------------
# Time Helpers
# -----------------------------
'''
def utc_now():
    """Return current UTC timestamp"""
    return datetime.now(timezone.utc)
'''
from datetime import datetime, timezone, timedelta

def utc_now():
    """Return current IST time (UTC +5:30)"""
    return datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)

from datetime import datetime

def format_datetime(ts):
    if not ts:
        return ""

    # If already formatted like "12 Feb 2026, 05:53 PM"
    if isinstance(ts, str):
        # If it already matches your display format, return as-is
        try:
            datetime.strptime(ts, "%d %b %Y, %I:%M %p")
            return ts  # already formatted
        except ValueError:
            pass

        # Try ISO (Supabase)
        try:
            ts = ts.replace("Z", "")
            dt = datetime.fromisoformat(ts)
        except ValueError:
            # Try DB format with microseconds
            try:
                dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                # Try DB format without microseconds
                dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
    else:
        dt = ts  # already datetime object

    return dt.strftime("%d %b %Y, %I:%M %p")



def _time_ago(ts):
    """Return relative time string like '2h ago'."""
    if not ts:
        return ""
    dt = datetime.fromisoformat(ts.replace("Z", ""))
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    diff = now - dt

    seconds = diff.total_seconds()

    if seconds < 60:
        return "just now"
    if seconds < 3600:
        return f"{int(seconds//60)}m ago"
    if seconds < 86400:
        return f"{int(seconds//3600)}h ago"
    if seconds < 604800:
        return f"{int(seconds//86400)}d ago"

    return dt.strftime("%d %b %Y")

# -----------------------------
# ID & Hash Helpers
# -----------------------------

def generate_uuid():
    """Generate UUID4 string"""
    return str(uuid.uuid4())

def generate_voter_id():
    return f"VTR-{uuid.uuid4().hex[:10].upper()}"


def sha256_hash(value: str) -> str:
    """Generate SHA256 hash for any string value"""
    if value is None:
        raise ValueError("Value cannot be None for hashing")
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def generate_transaction_id(prefix: str = "TX") -> str:
    """
    Generate readable transaction ID
    Example: TX-9f3a7c2e-20260126
    """
    short_id = uuid.uuid4().hex[:8]
    date_part = datetime.utcnow().strftime("%Y%m%d")
    return f"{prefix}-{short_id}-{date_part}"


# -----------------------------
# Validation Helpers
# -----------------------------

def is_valid_email(email: str) -> bool:
    if not email:
        return False
    return "@" in email and "." in email


def is_strong_password(password: str, min_length: int = 8) -> bool:
    if not password or len(password) < min_length:
        return False
    return True


# -----------------------------
# Pagination Helper
# -----------------------------

def paginate(query_result: list, page: int = 1, per_page: int = 10):
    """
    Simple pagination for Supabase responses
    """
    if page < 1:
        page = 1
    start = (page - 1) * per_page
    end = start + per_page
    return query_result[start:end]


# -----------------------------
# Response Helpers
# -----------------------------

def success_response(message: str = "Success", data=None):
    return {
        "status": "success",
        "message": message,
        "data": data
    }


def error_response(message: str = "Error", errors=None):
    return {
        "status": "error",
        "message": message,
        "errors": errors
    }


# -----------------------------
# Role & Access Helpers
# -----------------------------

def normalize_role(role: str) -> str:
    """Normalize role names to uppercase"""
    if not role:
        return None
    return role.strip().upper()


def is_commission_role(role: str) -> bool:
    return normalize_role(role) in {"CEC", "CEO", "DEO", "RO", "ERO", "BLO"}

def assign_constituencies_to_election(election_id: str, constituency_ids: list[str]):
    for cid in constituency_ids:
        add_constituency_to_election(election_id, cid)
'''
def parse_iso_date(value) -> date:
    """
    Converts ISO date/datetime string to date object.
    Works with:
    - 'YYYY-MM-DD'
    - 'YYYY-MM-DDTHH:MM:SS'
    """
    if isinstance(value, date):
        return value

    # Strip time part if present
    return date.fromisoformat(value[:10])
'''
from datetime import datetime, date

def parse_iso_date(value):
    if not value:
        return None

    # Try ISO first
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        pass

    # Try human-readable format like "21 Feb 2026"
    try:
        return datetime.strptime(value, "%d %b %Y").date()
    except ValueError:
        raise ValueError(f"Unsupported date format: {value}")

IST = pytz.timezone("Asia/Kolkata")

def today_ist() -> date:
    return datetime.now(IST).date()

def time_ago(timestamp):
    if not timestamp:
        return ""

    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp.replace("Z", ""))

    now = datetime.utcnow()
    diff = now - timestamp

    seconds = diff.total_seconds()

    if seconds < 60:
        return "Just now"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m ago"
    elif seconds < 86400:
        return f"{int(seconds // 3600)}h ago"
    elif seconds < 604800:
        return f"{int(seconds // 86400)}d ago"
    else:
        return timestamp.strftime("%d %b %Y")
    

from datetime import datetime

def _time_ago_issue(timestamp):
    if not timestamp:
        return ""

    if isinstance(timestamp, str):
        # Try ISO
        try:
            timestamp = datetime.fromisoformat(timestamp.replace("Z", ""))
        except ValueError:
            pass

        # Try DB format with microseconds
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                pass

        # Try DB format without microseconds
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                pass

        # Try formatted display format
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.strptime(timestamp, "%d %b %Y, %I:%M %p")
            except ValueError:
                return ""  # Avoid crashing

    now = datetime.utcnow()
    diff = now - timestamp
    seconds = diff.total_seconds()

    if seconds < 60:
        return "Just now"
    elif seconds < 3600:
        return f"{int(seconds // 60)} minutes ago"
    elif seconds < 86400:
        return f"{int(seconds // 3600)} hours ago"
    else:
        return f"{int(seconds // 86400)} days ago"


def generate_temp_password(length=10):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))
