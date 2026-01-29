
import os

# --------------------------
# API KEYS (replace with your keys or load securely)
# --------------------------
GOOGLE_VISION_API_KEY = os.getenv("GOOGLE_VISION_API_KEY", "your-google-vision-api-key-here")

DEEPL_SEEK_API_KEY = os.getenv("DEEPL_SEEK_API_KEY", "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")

# --------------------------
# FILE HANDLING
# --------------------------
ALLOWED_FILE_EXTENSIONS = ['pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg']

UPLOAD_FOLDER = "uploads/"
PROCESSED_FOLDER = "processed/"
RESULTS_FOLDER = "results/"

# --------------------------
# GRADING DEFAULTS
# --------------------------
DEFAULT_PASSING_MARK = 50  # Example default passing mark
DEFAULT_BIN_SIZE = 10      # For analytics bins

# --------------------------
# STREAMLIT SETTINGS
# --------------------------
MAX_UPLOAD_SIZE_MB = 50    # Max file size to upload (adjust as needed)

# --------------------------
# OTHER CONSTANTS
# --------------------------
LOG_FILE = "logs/app.log"

# Ensure folders exist at runtime
for folder in [UPLOAD_FOLDER, PROCESSED_FOLDER, RESULTS_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)
