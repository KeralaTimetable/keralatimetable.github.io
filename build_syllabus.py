import json
import os
import re

# ==========================================
# CONFIGURATION
# ==========================================
INPUT_FILE = 'ktu_syllabus_raw.json'
OUTPUT_DIR = 'syllabus_out' # Rename to 'syllabus' before pushing to GitHub
SITE_URL = 'https://keralatimetable.github.io'

# Load JSON Data
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def extract_code(name):
    # Extracts text inside parenthesis, e.g., "Subject Name - (GAMAT101)" -> "GAMAT101"
    match = re.search(r'\((.*?)\)', name)
    return match.group(1) if match else "KTU"

def clean_name(name):
    # Removes the hyphen and the code in parenthesis
    return re.sub(r'\s*-\s*\(.*?\)', '', name).strip()

def get_branch_acronym(branch_name):
    # Converts long branch names to SEO-friendly acronyms
    b = branch_name.upper()
    if 'COMPUTER' in b: return 'CSE'
    if 'MECHANICAL' in b: return 'ME'
    if 'CIVIL' in b: return 'CE'
    if 'ELECTRICAL AND ELECTRONICS' in b: return 'EEE'
    if 'ELECTRONICS AND COMMUNICATION' in b: return 'ECE'
    if 'INFORMATION TECHNOLOGY' in b: return 'IT'
    
    # Fallback: creates acronym from first letters of each word
    return "".join([word[0] for word in branch_name.split() if word.isalpha()])

# ==========================================
# HTML TEMPLATES
# ==========================================
def get_header(title, desc):
    return f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="google-site-verification" content="cPHgzg8741NBFQ5HszgVIPA3EMrKJLlj7IHcyLGM2Lo" />
    <title>{title}</title>
    <meta name="description" content="{desc}">
    <meta name="robots" content="index, follow">
    
    <script src="/tailwind-local.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    
    <style>
        body {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
        .font-sporty {{ font-family: 'Orbitron', sans-serif; letter-spacing: 0.05em; }}
        .bg-mesh {{
            background-color: #f8fafc;
            background-image: radial-gradient(at 40% 20%, hsla(228,100%,74%,0.15) 0px, transparent 50%),
                              radial-gradient(at 80% 0%, hsla(189,100%,56%,0.15) 0px, transparent 50%),
                              radial-gradient(at 0% 50%, hsla(228,100%,74%,0.15) 0px, transparent 50%);
        }}
        .no-scrollbar::-webkit-scrollbar {{ display: none; }}
        .no-scrollbar {{ -ms-overflow-style: none; scrollbar-width: none; }}
        .subject-card {{ transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1); }}
        .subject-card:hover {{ transform: translateY(-4px); box-shadow: 0 15px 30px -5px rgba(99, 102, 241, 0.15); border-color: #c7d2fe; }}
        @keyframes fadeUpEntry {{ 0% {{ opacity: 0; transform: translateY(15px); }} 100% {{ opacity: 1; transform: translateY(0); }} }}
        .animate-fade-up {{ animation: fadeUpEntry 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards; }}
    </style>
</head>
<body class="bg-mesh text-slate-800 antialiased flex flex-col min-h-screen relative overflow-x-hidden">
    <div id="navigation-container" class="min-h-[73px] w-full"></div>
    <main class="flex-grow w-full pb-20">
"""

def get_footer():
    return f"""
    </main>
    <script src="/components.js?v=12"></script>
    <script>
        if(typeof loadNavigation === 'function') loadNavigation('', '', false);
    </script>
</body>
</html>
"""

# ==========================================
# 1. GENERATE MAIN HUB (index.html)
# ==========================================
main_title = "KTU B.Tech Syllabus 2024 Scheme | All Branches"
main_desc = "Download official KTU B.Tech syllabus PDFs for the 2024 scheme. Select your branch to access semester-wise study materials."

main_html = get_header(main_title, main_desc)
main_html += """
        <div class="w-full max-w-6xl mx-auto px-4 pt-10 pb-6 text-center relative z-20">
            <div class="animate-fade-up inline-flex items-center gap-2 px-4 py-2 rounded-full bg-slate-800 border border-slate-700 text-white text-xs font-bold uppercase tracking-wider mb-6 shadow-sm">
                <i class="fas fa-book-open text-indigo-400"></i> Official Curriculum
            </div>
            <h1 class="animate-fade-up delay-100 text-4xl md:text-5xl font-black text-slate-900 tracking-tight leading-tight mb-4">
                B.Tech Syllabus <span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-500 to-emerald-500">2024 Scheme</span>
            </h1>
            <p class="animate-fade-up delay-200 text-slate-500 font-medium md:text-lg max-w-2xl mx-auto mb-8">
                Select your engineering branch below to access semester-wise syllabus PDFs.
            </p>
        </div>
        <div class="w-full max-w-5xl mx-auto px-4 relative z-20 animate-fade-up delay-300">
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
"""

for branch in data.keys():
    branch_slug = slugify(branch)
    branch_acronym = get_branch_acronym(branch)
    main_html += f"""
                <a href="{branch_slug}/index.html" class="subject-card bg-white/90 backdrop-blur-md border border-slate-200 rounded-2xl p-6 flex flex-col items-center justify-center text-center group">
                    <div class="w-14 h-14 bg-indigo-50 text-indigo-600 rounded-2xl flex items-center justify-center text-2xl mb-4 group-hover:bg-indigo-600 group-hover:text-white transition-colors shadow-sm">
                        <i class="fas fa-microchip"></i>
                    </div>
                    <span class="text-[10px] font-black bg-slate-800 text-white px-2 py-1 rounded mb-2">B.TECH</span>
                    <h2 class="font-bold text-slate-800 text-base leading-snug">{branch} ({branch_acronym})</h2>
                </a>
    """
main_html += "</div></div>" + get_footer()

with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(main_html)

# ==========================================
# 2. GENERATE BRANCH & SEMESTER PAGES
# ==========================================
for branch, years in data.items():
    branch_slug = slugify(branch)
    branch_dir = os.path.join(OUTPUT_DIR, branch_slug)
    os.makedirs(branch_dir, exist_ok=True)
    branch_acronym = get_branch_acronym(branch)
    
    # --- BRANCH INDEX (e.g., /computer-science-and-engineering/index.html) ---
    
    # NEW SEO TITLE FORMAT: KTU btech CSE SYLLABUS 2024 SCHEME
    branch_page_title = f"KTU B.Tech {branch_acronym} Syllabus 2024 Scheme"
    branch_page_desc = f"Download complete KTU B.Tech {branch_acronym} ({branch}) syllabus PDFs for the 2024 scheme. All semesters available."
    
    branch_html = get_header(branch_page_title, branch_page_desc)
    branch_html += f"""
        <div class="w-full max-w-5xl mx-auto px-4 pt-8 pb-4 relative z-20 animate-fade-up">
            <div class="flex items-center flex-wrap text-xs font-bold text-slate-400 uppercase tracking-wider mb-6 gap-2">
                <a href="/syllabus/index.html" class="hover:text-indigo-600 transition-colors">Syllabus Hub</a>
                <i class="fas fa-chevron-right text-[8px]"></i>
                <span class="text-slate-700">{branch_acronym}</span>
            </div>
            
            <h1 class="text-3xl md:text-4xl font-black text-slate-900 leading-tight mb-2">KTU B.Tech {branch_acronym} Syllabus</h1>
            <p class="text-slate-500 font-medium mb-8">2024 Scheme • {branch}</p>
            
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
    """
    
    for year, semesters in years.items():
        for semester in semesters.keys():
            sem_slug = slugify(semester)
            short_sem = semester.replace('Semester ', 'S')
            sub_count = len(semesters[semester])
            
            # Add Sem Card to Branch Index
            branch_html += f"""
                <a href="{sem_slug}.html" class="subject-card bg-white border border-slate-200 rounded-xl p-5 text-center group">
                    <h3 class="font-black text-2xl text-slate-800 group-hover:text-indigo-600 transition-colors mb-1">{short_sem}</h3>
                    <p class="text-xs font-bold text-slate-400 uppercase tracking-widest">{sub_count} Subjects</p>
                </a>
            """
            
            # --- SEMESTER SPECIFIC PAGE (e.g., /computer-science/semester-1.html) ---
            
            # NEW SEO TITLE FORMAT: KTU B.Tech S1 CSE Syllabus 2024 Scheme
            sem_page_title = f"KTU B.Tech {short_sem} {branch_acronym} Syllabus 2024 Scheme"
            sem_page_desc = f"Download individual subject syllabus PDFs for KTU B.Tech {short_sem} {branch_acronym} (2024 Scheme). Direct downloads available."
            
            sem_html = get_header(sem_page_title, sem_page_desc)
            sem_html += f"""
        <div class="w-full max-w-6xl mx-auto px-4 pt-8 pb-4 relative z-20 animate-fade-up">
            <div class="flex items-center flex-wrap text-xs font-bold text-slate-400 uppercase tracking-wider mb-6 gap-2">
                <a href="/syllabus/index.html" class="hover:text-indigo-600 transition-colors">Hub</a>
                <i class="fas fa-chevron-right text-[8px]"></i>
                <a href="index.html" class="hover:text-indigo-600 transition-colors">{branch_acronym}</a>
                <i class="fas fa-chevron-right text-[8px]"></i>
                <span class="text-slate-700">{short_sem}</span>
            </div>
            
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
                <div>
                    <h1 class="text-3xl md:text-4xl font-black text-slate-900 leading-tight mb-2">{short_sem} {branch_acronym} Syllabus</h1>
                    <p class="text-slate-500 font-medium">B.Tech 2024 Scheme</p>
                </div>
                <span class="bg-indigo-100 text-indigo-700 text-xs font-black px-4 py-2 rounded-full uppercase tracking-widest w-max">{sub_count} Subjects</span>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            """
            
            for subject in semesters[semester]:
                sub_name = clean_name(subject['name'])
                sub_code = extract_code(subject['name'])
                sub_link = subject['link']
                
                # Subject Card
                sem_html += f"""
                <div class="subject-card bg-white/90 backdrop-blur-md rounded-2xl border border-slate-200 shadow-sm flex flex-col p-5 group relative overflow-hidden">
                    
                    <div class="absolute -bottom-2 -right-2 text-6xl font-black text-slate-900 opacity-[0.02] pointer-events-none select-none z-0">
                        {short_sem}
                    </div>
                    
                    <div class="relative z-10 flex-grow flex flex-col">
                        <div class="flex items-center flex-wrap gap-2 mb-4">
                            <span class="px-2.5 py-1 rounded-md text-[10px] font-black uppercase tracking-wider bg-slate-800 text-white shadow-sm">B.TECH</span>
                            <span class="px-2.5 py-1 rounded-md text-[10px] font-black uppercase tracking-wider bg-indigo-100 text-indigo-700 border border-indigo-200">{short_sem}</span>
                            <span class="px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider bg-slate-100 text-slate-600 border border-slate-200 font-sporty">{sub_code}</span>
                        </div>
                        
                        <h3 class="text-base font-extrabold text-slate-800 leading-tight mb-6 pr-2 flex-grow">{sub_name}</h3>
                        
                        <a href="{sub_link}" target="_blank" class="w-full bg-slate-50 hover:bg-emerald-500 text-slate-600 hover:text-white border border-slate-200 hover:border-emerald-500 font-bold text-sm px-4 py-2.5 rounded-xl flex items-center justify-center gap-2 transition-colors">
                            <i class="fas fa-file-pdf"></i> Download PDF
                        </a>
                    </div>
                </div>
                """
            
            sem_html += "</div></div>" + get_footer()
            
            with open(os.path.join(branch_dir, f"{sem_slug}.html"), 'w', encoding='utf-8') as f:
                f.write(sem_html)

        branch_html += "</div></div>" + get_footer()
        with open(os.path.join(branch_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(branch_html)

print("✅ SUCCESS! Your B.Tech SEO syllabus site is generated in the 'syllabus_out' folder.")
print("ℹ️  IMPORTANT: Make sure to rename the output folder to 'syllabus' when moving it to your main repository!")
