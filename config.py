import os
from dotenv import load_dotenv

# Load .env into environment
load_dotenv()

class Config:
    # -----------------------
    # Flask
    # -----------------------
    SECRET_KEY = os.getenv("SECRET_KEY")
    FLASK_ENV = os.getenv("FLASK_ENV", "production")
    DEBUG = os.getenv("FLASK_DEBUG", "False") == "True"

    # -----------------------
    # Supabase
    # -----------------------
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    # -----------------------
    # App Settings
    # -----------------------
    APP_NAME = os.getenv("APP_NAME", "E-Democracy")
    TOKEN_EXPIRY_MINUTES = int(os.getenv("TOKEN_EXPIRY_MINUTES", 60))

    # -----------------------
    # Role Definitions
    # -----------------------
    ROLES = {
        "CEC": "Chief Election Commissioner",
        "CEO": "Chief Electoral Officer",
        "DEO": "District Election Officer",
        "RO": "Returning Officer",
        "ERO": "Electoral Registration Officer",
        "BLO": "Booth Level Officer",
        "CITIZEN": "Citizen",
        "ELECTED_REP": "Elected Representative",
        "OPPOSITION_REP": "Opposition Representative"
    }

    # -----------------------
    # Security
    # -----------------------
    PASSWORD_MIN_LENGTH = 8
