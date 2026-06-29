import os
import sqlite3
import io
import sys
from huggingface_hub import HfApi

# Ensure we can import from ktu_repo if it's in the same directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from ktu_repo import resolve_pdf_url, download_pdf
except ImportError:
    print("❌ Error: Could not find 'ktu_repo.py' in the current directory.")
    print("Make sure hf_sync.py is placed right next to ktu_repo.py.")
    sys.exit(1)

# --- CONFIGURATION ---
# Reads HF_TOKEN from environment (GitHub Actions). Fallback to a string for local testing.
HF_TOKEN = os.getenv("HF_TOKEN", "YOUR_LOCAL_WRITE_TOKEN_IF_TESTING_LOCALLY") 
DATASET_REPO_ID = "KeralaTimetable/ktu-pyq-archive"
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ktu_index.db")

api = HfApi()

def sync_to_huggingface():
    if not os.path.exists(DB_PATH):
        print(f"❌ Error: Database file not found at {DB_PATH}")
        print("Please run 'python ktu_repo.py harvest' first to build the index.")
        return

    # Connect to your existing SQLite database
    con = sqlite3.connect(DB_PATH)
    cursor = con.cursor()
    
    # Grab all papers from your harvested index
    try:
        cursor.execute("SELECT handle FROM papers")
        rows = cursor.fetchall()
    except sqlite3.OperationalError as e:
        print(f"❌ Database error: {e}. Is your schema matching?")
        con.close()
        return
    
    print(f"Found {len(rows)} papers in the local database. Starting sync to {DATASET_REPO_ID}...")
    
    success_count = 0
    skipped_count = 0
    fail_count = 0

    for row in rows:
        handle = row[0]
        # Transform handle "1/8891" -> "1_8891.pdf" for a safe cloud file path
        safe_filename = f"{handle.replace('/', '_')}.pdf"
        
        try:
            # 1. Check if it already exists on Hugging Face to save bandwidth and time
            file_exists = api.file_exists(
                repo_id=DATASET_REPO_ID, 
                filename=safe_filename, 
                repo_type="dataset", 
                token=HF_TOKEN
            )
            
            if file_exists:
                print(f"⏩ Skipped: {handle} (Already backed up)")
                skipped_count += 1
                continue

            # 2. Use your existing ktu_repo lazy-resolution logic to get the live JEC URL
            print(f"Resolving URL for {handle}...")
            pdf_url = resolve_pdf_url(handle)
            
            if not pdf_url:
                print(f"❌ Could not resolve PDF link for handle: {handle}")
                fail_count += 1
                continue
                
            # 3. Download the PDF bytes straight into server memory (avoids eating disk space)
            print(f"Downloading from JEC: {pdf_url}")
            pdf_bytes = download_pdf(pdf_url)
            
            # 4. Stream upload directly to Hugging Face
            api.upload_file(
                path_or_fileobj=io.BytesIO(pdf_bytes),
                path_in_repo=safe_filename,
                repo_id=DATASET_REPO_ID,
                repo_type="dataset",
                token=HF_TOKEN
            )
            
            print(f"✅ Successfully backed up: {handle}")
            success_count += 1
            
        except Exception as e:
            print(f"⚠️ Error processing handle {handle}: {e}")
            fail_count += 1

    con.close()
    print("\n" + "="*40)
    print("🎉 Sync Session Complete!")
    print(f"✅ Successfully Backed Up: {success_count}")
    print(f"⏩ Skipped (Already Exists): {skipped_count}")
    print(f"❌ Failed/Errors: {fail_count}")
    print("="*40)

if __name__ == "__main__":
    sync_to_huggingface()
