import os

PER_CAPITA_DOMESTIC = 1500
AGRICULTURAL_BENCHMARK = 10000
INDUSTRIAL_BENCHMARK = 5000
RESERVOIR_SAFE_LEVEL = 80
DROUGHT_THRESHOLD = 50
RESERVOIR_LEVELS = {1: 90, 2: 40}
TOTAL_SUPPLIES = {1: 1000000, 2: 500000}

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KB_PDF_PATH = os.path.join(BASE_DIR, "kb_pdfs")

# Create directory with proper error handling
try:
    os.makedirs(KB_PDF_PATH, exist_ok=True)
except PermissionError:
    print(f"Permission denied: Cannot create {KB_PDF_PATH}")
except Exception as e:
    print(f"Error creating directory: {e}")