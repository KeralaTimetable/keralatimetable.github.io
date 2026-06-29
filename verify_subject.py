import os
import sqlite3
import sys
from huggingface_hub import HfApi

# --- CONFIGURATION ---
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ktu_index.db")
DATASET_REPO_ID = "KeralaTimetable/ktu-pyq-archive"

# Reads from GitHub input, defaults to GAMAT101 if run locally without an environment variable
SUBJECT_CODE = os.getenv("SUBJECT_CODE", "GAMAT101").strip()
HF_TOKEN = os.getenv("HF_TOKEN") # Optional for public datasets, but good to have

api = HfApi()

def verify_subject_papers():
    print(f"🔍 Starting verification for subject: {SUBJECT_CODE}")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Error: Database file not found at {DB_PATH}")
        sys.exit(1)

    # 1. Download the list of files currently on Hugging Face
    print("Scanning Hugging Face for uploaded files...")
    try:
        hf_files = set(api.list_repo_files(repo_id=DATASET_REPO_ID, repo_type="dataset", token=HF_TOKEN))
        print(f"Found {len(hf_files)} files safely in the cloud.")
    except Exception as e:
        print(f"❌ Error fetching Hugging Face repository files: {e}")
        sys.exit(1)

    # 2. Connect to your local database
    con = sqlite3.connect(DB_PATH)
    cursor = con.cursor()
    
    # We will dynamically check columns to ensure we don't crash if your column is named differently
    try:
        cursor.execute("PRAGMA table_info(papers)")
        columns = [col[1] for col in cursor.fetchall()]
    except Exception as e:
        print(f"❌ Error reading database schema: {e}")
        con.close()
        sys.exit(1)

    # Determine which column to look up (handles 'subject', 'course_code', or falls back to 'title')
    search_column = "subject"
    if "subject" not in columns:
        if "course_code" in columns:
            search_column = "course_code"
        elif "title" in columns:
            search_column = "title"
        else:
            # Fallback to the first column that isn't 'handle'
            non_handle_cols = [c for c in columns if c != "handle"]
            if non_handle_cols:
                search_column = non_handle_cols[0]

    print(f"Using database column '{search_column}' for subject matching.")

    # 3. Query the database for the chosen subject
    try:
        query = f"SELECT handle FROM papers WHERE {search_column} LIKE ?"
        cursor.execute(query, (f"%{SUBJECT_CODE}%",))
        rows = cursor.fetchall()
    except Exception as e:
        print(f"❌ Database query failed: {e}")
        con.close()
        sys.exit(1)

    if not rows:
        print(f"\n❌ No papers found in your local database for '{SUBJECT_CODE}'.")
        print("This means the scraper never extracted this code from the JEC website.")
        con.close()
        return
        
    print(f"\nFound {len(rows)} papers for {SUBJECT_CODE} in local database. Verifying cloud sync...")
    print("-" * 60)
    
    # 4. Cross-reference database handles with Hugging Face files
    missing_count = 0
    for row in rows:
        handle = row[0]
        safe_filename = f"{handle.replace('/', '_')}.pdf"
        
        if safe_filename in hf_files:
            print(f"✅ MATCHED: {safe_filename} is safe on Hugging Face")
        else:
            print(f"❌ MISSING: {safe_filename} (Handle: {handle})")
            missing_count += 1
            
    print("-" * 60)
    if missing_count == 0:
        print(f"🎉 SUCCESS: All {len(rows)} papers for {SUBJECT_CODE} are fully backed up!")
    else:
        print(f"⚠️ Warning: {missing_count} out of {len(rows)} papers are missing from Hugging Face.")
        
    con.close()

if __name__ == "__main__":
    verify_subject_papers()
