import sqlite3
from huggingface_hub import HfApi

# --- CONFIGURATION ---
DB_PATH = "ktu_index.db"
DATASET_REPO_ID = "KeralaTimetable/ktu-pyq-archive"
SUBJECT_CODE = "GAMAT101"  # You can change this to any subject

api = HfApi()

def verify_subject_papers():
    # 1. Download the list of the 7,834 files currently on Hugging Face
    print("Scanning Hugging Face for uploaded files...")
    hf_files = set(api.list_repo_files(repo_id=DATASET_REPO_ID, repo_type="dataset"))

    # 2. Connect to your database
    con = sqlite3.connect(DB_PATH)
    cursor = con.cursor()
    
    # NOTE: Adjust the column name 'subject' below if your database uses 
    # a different column name (like 'course_code', 'title', or 'metadata')
    try:
        query = "SELECT handle FROM papers WHERE subject LIKE ?"
        cursor.execute(query, (f"%{SUBJECT_CODE}%",))
        rows = cursor.fetchall()
    except sqlite3.OperationalError:
        # Fallback if the column is named differently
        print("⚠️ 'subject' column not found. Please update the SQL query with your exact column name.")
        con.close()
        return

    if not rows:
        print(f"\n❌ No papers found in your local database for {SUBJECT_CODE}.")
        print("This means the scraper never found them on the JEC website to begin with.")
        con.close()
        return
        
    print(f"\nFound {len(rows)} papers for {SUBJECT_CODE} in your local database. Checking cloud...")
    print("-" * 40)
    
    # 3. Cross-reference database handles with Hugging Face files
    missing_count = 0
    for row in rows:
        handle = row[0]
        safe_filename = f"{handle.replace('/', '_')}.pdf"
        
        if safe_filename in hf_files:
            print(f"✅ {safe_filename} is on Hugging Face")
        else:
            print(f"❌ {safe_filename} is MISSING from Hugging Face")
            missing_count += 1
            
    print("-" * 40)
    if missing_count == 0:
        print(f"🎉 SUCCESS: All {len(rows)} papers for {SUBJECT_CODE} are safely backed up!")
    else:
        print(f"⚠️ Warning: {missing_count} papers failed to upload.")
        
    con.close()

if __name__ == "__main__":
    verify_subject_papers()
