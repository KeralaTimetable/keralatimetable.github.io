import os
import sqlite3
import shutil
import sys
from huggingface_hub import HfApi

# Ensure local import works properly in GitHub Actions
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from ktu_repo import resolve_pdf_url, download_pdf
except ImportError:
    print("❌ Error: Could not find 'ktu_repo.py' in the current directory.")
    sys.exit(1)

# --- CONFIGURATION ---
HF_TOKEN = os.getenv("HF_TOKEN") 
DATASET_REPO_ID = "KeralaTimetable/ktu-pyq-archive"
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ktu_index.db")

# Batching variables
BATCH_DIR = "temp_batch"
BATCH_SIZE = 50  # Uploads 50 files at a time to prevent rate limits

api = HfApi()

def sync_to_huggingface():
    if not os.path.exists(DB_PATH):
        print(f"❌ Error: Database file not found at {DB_PATH}")
        return

    # 1. Fetch all existing files ONCE to make skipping instant
    print("Scanning Hugging Face dataset for already uploaded files...")
    try:
        existing_files = set(api.list_repo_files(
            repo_id=DATASET_REPO_ID, 
            repo_type="dataset", 
            token=HF_TOKEN
        ))
        print(f"Found {len(existing_files)} files already safely in the cloud.")
    except Exception as e:
        print(f"⚠️ Could not fetch existing files list (Rate limit?): {e}")
        existing_files = set()

    # 2. Setup the batch folder
    if not os.path.exists(BATCH_DIR):
        os.makedirs(BATCH_DIR)

    con = sqlite3.connect(DB_PATH)
    cursor = con.cursor()
    cursor.execute("SELECT handle FROM papers")
    rows = cursor.fetchall()
    
    queued_count = 0
    new_files_processed = 0

    print(f"Starting database processing for {len(rows)} papers...")

    for row in rows:
        handle = row[0]
        safe_filename = f"{handle.replace('/', '_')}.pdf"
        
        # INSTANT SKIP: If it's in the list we grabbed earlier, move on!
        if safe_filename in existing_files:
            continue

        local_path = os.path.join(BATCH_DIR, safe_filename)
        print(f"Downloading {handle} from JEC...")

        try:
            pdf_url = resolve_pdf_url(handle)
            if not pdf_url:
                print(f"❌ Could not resolve URL for {handle}")
                continue
                
            pdf_bytes = download_pdf(pdf_url)
            
            # Save the file into our temporary batch folder
            with open(local_path, "wb") as f:
                f.write(pdf_bytes)
                
            queued_count += 1
            new_files_processed += 1
            
        except Exception as e:
            print(f"⚠️ Failed to process {handle}: {e}")
            continue

        # 3. If we hit 50 files in the folder, upload them all at once!
        if queued_count >= BATCH_SIZE:
            print(f"🚀 Uploading batch of {queued_count} files to Hugging Face...")
            try:
                api.upload_folder(
                    folder_path=BATCH_DIR,
                    repo_id=DATASET_REPO_ID,
                    repo_type="dataset",
                    token=HF_TOKEN,
                    commit_message=f"Batch upload of {queued_count} PYQs"
                )
                print("✅ Batch upload successful!")
            except Exception as e:
                print(f"❌ Batch upload failed: {e}")
            
            # Empty the temporary folder for the next batch of 50
            shutil.rmtree(BATCH_DIR)
            os.makedirs(BATCH_DIR)
            queued_count = 0

    # 4. Final upload for any remaining files (e.g., the last 14 files)
    if queued_count > 0:
        print(f"🚀 Uploading final batch of {queued_count} files...")
        try:
            api.upload_folder(
                folder_path=BATCH_DIR,
                repo_id=DATASET_REPO_ID,
                repo_type="dataset",
                token=HF_TOKEN,
                commit_message=f"Final batch upload of {queued_count} PYQs"
            )
            print("✅ Final batch successful!")
        except Exception as e:
            print(f"❌ Final batch upload failed: {e}")

    # Clean up the temporary folder and close database
    if os.path.exists(BATCH_DIR):
        shutil.rmtree(BATCH_DIR)
    con.close()
    
    print("\n" + "="*40)
    print("🎉 Sync Session Complete!")
    print(f"✅ New Files Backed Up Today: {new_files_processed}")
    print("="*40)

if __name__ == "__main__":
    sync_to_huggingface()
