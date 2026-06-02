# Standalone KTU Syllabus Splitter & Metadata Generator
# Commit this script to your GitHub repository!
# Usage: python split_syllabus.py --pdf Cse.pdf --branch "Computer Science and Engineering" --scheme "B.Tech Full Time 2024 Scheme"
# Requirements: pip install pymupdf

import argparse
import fitz  # PyMuPDF
import json
import csv
import os
import re

def clean_subject_name(name):
    name = name.strip()
    name = re.sub(r'^(COURSE NAME\s*:\s*)', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+', ' ', name)
    return name

def split_ktu_syllabus(pdf_path, branch, scheme, output_dir):
    pdf_dir = os.path.join(output_dir, "pdfs")
    os.makedirs(pdf_dir, exist_ok=True)
    
    print(f"Opening PDF: {pdf_path}")
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    print(f"Total pages: {total_pages}")
    
    subjects = []
    current_subject = None
    
    # Scan every page for subject headers
    for page_idx in range(total_pages):
        page = doc.load_page(page_idx)
        text = page.get_text()
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        
        is_subject_start = False
        sem_tag = None
        course_name = None
        course_code = None
        
        for i, line in enumerate(lines):
            # Detect semester marker (e.g. SEMESTER S3 to S8)
            if line.startswith("SEMESTER S") and len(line) <= 12:
                sem_tag = line
                # Next line is usually the course name
                if i + 1 < len(lines):
                    course_name = lines[i+1]
                    if i + 2 < len(lines) and (lines[i+2].startswith("(") or "group" in lines[i+2].lower()):
                        course_name += " " + lines[i+2]
                        
                # Find "Course Code" and its value
                for j in range(i, min(i + 15, len(lines))):
                    if lines[j] == "Course Code" and j + 1 < len(lines):
                        course_code = lines[j+1]
                        break
                        
                if course_code:
                    is_subject_start = True
                    break
                    
        if is_subject_start:
            # Terminate and save previous running subject boundary
            if current_subject:
                current_subject["end_page"] = page_idx # 1-based index (prev page)
                subjects.append(current_subject)
                
            current_subject = {
                "semester": sem_tag.replace("SEMESTER ", "").strip(),
                "subject_name": clean_subject_name(course_name),
                "course_code": course_code.strip(),
                "start_page": page_idx + 1,
                "end_page": None
            }
            
    if current_subject:
        current_subject["end_page"] = total_pages
        subjects.append(current_subject)
        
    print(f"Discovered {len(subjects)} subjects in total.")
    
    # Datasets compilation
    nested_db = {
        "branch": branch,
        "scheme": scheme,
        "semesters": {}
    }
    
    # Standard 2024 S3-S8 semesters init
    for s_num in range(3, 9):
        nested_db["semesters"][f"S{s_num}"] = []
        
    flat_db = []
    
    print("Splitting PDF pages and writing single subject files...")
    for sub in subjects:
        sem = sub["semester"]
        code = sub["course_code"]
        name = sub["subject_name"]
        start = sub["start_page"]
        end = sub["end_page"]
        
        pdf_filename = f"{sem}_{code}.pdf"
        pdf_relative_path = f"pdfs/{pdf_filename}"
        pdf_out_path = os.path.join(pdf_dir, pdf_filename)
        
        # Write PDF snippet (pages are 0-indexed in insert_pdf)
        sub_doc = fitz.open()
        sub_doc.insert_pdf(doc, from_page=start-1, to_page=end-1)
        sub_doc.save(pdf_out_path)
        sub_doc.close()
        
        # Flat schema dictionary
        flat_entry = {
            "branch": branch,
            "scheme": scheme,
            "semester": sem,
            "course_code": code,
            "subject_name": name,
            "start_page": start,
            "end_page": end,
            "page_count": end - start + 1,
            "pdf_file": pdf_relative_path
        }
        flat_db.append(flat_entry)
        
        # Nested schema dictionary
        nested_entry = {
            "course_code": code,
            "subject_name": name,
            "pdf_file": pdf_relative_path,
            "start_page": start,
            "end_page": end,
            "page_count": end - start + 1
        }
        
        if sem in nested_db["semesters"]:
            nested_db["semesters"][sem].append(nested_entry)
        else:
            if sem not in nested_db["semesters"]:
                nested_db["semesters"][sem] = []
            nested_db["semesters"][sem].append(nested_entry)
            
    # Save files
    # 1. syllabus_data.json (nested)
    with open(os.path.join(output_dir, "syllabus_data.json"), "w") as jn:
        json.dump(nested_db, jn, indent=2)
        
    # 2. syllabus_flat.json (flat array)
    with open(os.path.join(output_dir, "syllabus_flat.json"), "w") as jf:
        json.dump(flat_db, jf, indent=2)
        
    # 3. syllabus_database.csv (CSV spreadsheet)
    csv_fields = ["branch", "scheme", "semester", "course_code", "subject_name", "start_page", "end_page", "page_count", "pdf_file"]
    with open(os.path.join(output_dir, "syllabus_database.csv"), "w", newline="", encoding="utf-8") as cf:
        writer = csv.DictWriter(cf, fieldnames=csv_fields)
        writer.writeheader()
        writer.writerows(flat_db)
        
    print("\n=== PROCESS COMPLETED ===")
    print(f"Created {len(flat_db)} split PDFs in {pdf_dir}")
    print(f"Generated indices in: {output_dir}")
    print("  - syllabus_data.json")
    print("  - syllabus_flat.json")
    print("  - syllabus_database.csv")
    
    doc.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KTU PDF Syllabus Splitter & Metadata Generator")
    parser.add_argument("--pdf", required=True, help="Path to the massive KTU PDF file (e.g. Cse.pdf)")
    parser.add_argument("--branch", default="Computer Science and Engineering", help="Name of the branch")
    parser.add_argument("--scheme", default="B.Tech Full Time 2024 Scheme", help="Syllabus regulation/scheme name")
    parser.add_argument("--outdir", default=".", help="Directory to output split PDFs and metadata")
    
    args = parser.parse_args()
    split_ktu_syllabus(args.pdf, args.branch, args.scheme, args.outdir)
