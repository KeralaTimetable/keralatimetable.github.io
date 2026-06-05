// components.js

// Added 'isBlog' which tells the header to add the "| Blog" text!
function loadNavigation(activePage, basePath = '', isBlog = false) { 
    
    // If it's a blog, create the extra text. If not, leave it blank.
    const logoExtension = isBlog ? ' <span class="text-slate-400 font-medium ml-1">| Blog</span>' : '';

    const navHTML = `
        <div id="mobile-menu" class="fixed inset-y-0 left-0 w-64 bg-white shadow-2xl transform -translate-x-full transition-transform duration-300 ease-in-out z-[60] flex flex-col border-r border-slate-100">
            <div class="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50">
                <h2 class="text-lg font-extrabold text-slate-900 tracking-tight">Menu</h2>
                <button id="close-menu-btn" class="p-2 text-slate-400 hover:text-red-500 transition-colors rounded-full hover:bg-white shadow-sm focus:outline-none">
                    <i class="fas fa-times text-lg"></i>
                </button>
            </div>
            
            <nav class="flex-grow py-6 px-4 flex flex-col gap-2 overflow-y-auto">
                <a href="/index.html" class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activePage === 'home' ? 'bg-indigo-50 text-indigo-700 font-bold border border-indigo-100' : 'text-slate-600 hover:text-indigo-600 hover:bg-indigo-50 font-semibold'}">
                    <i class="fas fa-home w-5 text-center ${activePage === 'home' ? 'text-indigo-600' : 'text-slate-400'}"></i> Home
                </a>
                
                <a href="/timetable.html" class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activePage === 'timetable' ? 'bg-indigo-50 text-indigo-700 font-bold border border-indigo-100' : 'text-slate-600 hover:text-indigo-600 hover:bg-indigo-50 font-semibold'}">
                    <i class="fas fa-calendar-day w-5 text-center ${activePage === 'timetable' ? 'text-indigo-600' : 'text-slate-400'}"></i> Timetables
                </a>
                
                <a href="/notes.html" class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activePage === 'notes' ? 'bg-indigo-50 text-indigo-700 font-bold border border-indigo-100' : 'text-slate-600 hover:text-indigo-600 hover:bg-indigo-50 font-semibold'}">
                    <i class="fas fa-book-open w-5 text-center ${activePage === 'notes' ? 'text-indigo-600' : 'text-slate-400'}"></i> Study Notes
                </a>

                <a href="/status.html" class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activePage === 'status' ? 'bg-indigo-50 text-indigo-700 font-bold border border-indigo-100' : 'text-slate-600 hover:text-indigo-600 hover:bg-indigo-50 font-semibold'}">
                    <i class="fas fa-server w-5 text-center ${activePage === 'status' ? 'text-indigo-600' : 'text-slate-400'}"></i> KTU Server Status
                </a>
                <a href="/updates.html" class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activePage === 'updates' ? 'bg-indigo-50 text-indigo-700 font-bold border border-indigo-100' : 'text-slate-600 hover:text-indigo-600 hover:bg-indigo-50 font-semibold'}">
                    <i class="fas fa-bullhorn w-5 text-center ${activePage === 'updates' ? 'text-indigo-600' : 'text-slate-400'}"></i> KTU Latest Updates
                </a>
                <a href="/blog/index.html" class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activePage === 'blog' ? 'bg-indigo-50 text-indigo-700 font-bold border border-indigo-100' : 'text-slate-600 hover:text-indigo-600 hover:bg-indigo-50 font-semibold'}">
                    <i class="fas fa-feather-alt w-5 text-center ${activePage === 'blog' ? 'text-indigo-600' : 'text-slate-400'}"></i> Blog
                </a>
                <a href="/about.html" class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activePage === 'about' ? 'bg-indigo-50 text-indigo-700 font-bold border border-indigo-100' : 'text-slate-600 hover:text-indigo-600 hover:bg-indigo-50 font-semibold'}">
                    <i class="fas fa-info-circle w-5 text-center ${activePage === 'about' ? 'text-indigo-600' : 'text-slate-400'}"></i> About
                </a>
            </nav>
            
            <div class="p-6 border-t border-slate-100 text-center">
                <p class="text-xs text-slate-400 font-medium tracking-wide">© 2026 Kerala Timetable</p>
            </div>
        </div>

        <div id="menu-overlay" class="fixed inset-0 bg-slate-900/20 backdrop-blur-sm z-50 opacity-0 pointer-events-none transition-opacity duration-300"></div>

        <header class="sticky top-0 z-40 bg-white/70 backdrop-blur-md border-b border-slate-200/50 shadow-sm transition-all duration-300">
            <div class="max-w-4xl mx-auto px-4 sm:px-6 py-4 flex justify-between items-center">
                <div class="flex items-center gap-3">
                    <button id="open-menu-btn" class="p-2 -ml-2 text-slate-600 hover:text-indigo-600 hover:bg-slate-100 rounded-lg transition-colors focus:outline-none lg:hidden">
                        <i class="fas fa-bars text-xl"></i>
                    </button>
                    <a href="/index.html" class="flex items-center gap-2 hover:opacity-80 transition-opacity">
                        <svg class="w-6 h-6 sm:w-7 sm:h-7 text-indigo-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                        <h1 class="text-xl sm:text-2xl font-extrabold tracking-tight text-slate-900 leading-none">Kerala <span class="text-indigo-600">Timetable</span>${logoExtension}</h1>
                    </a>
                </div>

                <div class="hidden lg:flex gap-3 items-center">
                    <a href="/status.html" class="text-sm px-5 py-2.5 rounded-full flex items-center gap-2 transition-colors ${activePage === 'status' ? 'font-bold text-slate-800 bg-white border border-slate-200 shadow-sm' : 'font-bold text-slate-600 bg-slate-100 hover:bg-slate-200'}">
                        <span class="relative flex h-2 w-2">
                          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                          <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                        </span>
                        Status
                    </a>
                    <a href="/updates.html" class="text-sm px-5 py-2.5 rounded-full flex items-center gap-2 transition-colors ${activePage === 'updates' ? 'font-bold text-white bg-indigo-600 shadow-md' : 'font-bold text-slate-600 bg-slate-100 hover:bg-indigo-600 hover:text-white'}">
                        <i class="fas fa-bullhorn text-[10px]"></i> Notice Board
                    </a>
                    <a href="/blog/index.html" class="text-sm px-5 py-2.5 rounded-full flex items-center gap-2 transition-colors ${activePage === 'blog' ? 'font-bold text-white bg-indigo-600 shadow-md' : 'font-bold text-slate-600 bg-slate-100 hover:bg-indigo-600 hover:text-white'}">
                        <i class="fas fa-feather-alt text-[10px]"></i> Blog
                    </a>
                    
                    <button id="theme-toggle-desktop" class="w-10 h-10 flex items-center justify-center rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 transition-colors focus:outline-none ml-1">
                        <i class="fas fa-moon text-lg transition-transform duration-300"></i>
                    </button>
                </div>
                
                <div class="lg:hidden flex items-center gap-3">
                    <button id="theme-toggle-mobile" class="w-10 h-10 flex items-center justify-center rounded-full bg-slate-100 text-slate-600 transition-colors focus:outline-none">
                        <i class="fas fa-moon transition-transform duration-300"></i>
                    </button>
                    
                    <a href="/updates.html" class="w-10 h-10 flex items-center justify-center bg-indigo-50 text-indigo-600 rounded-full border border-indigo-100 shadow-sm">
                       <i class="fas fa-bell"></i>
                    </a>
                </div>
            </div>
        </header>
    `;

    document.getElementById('navigation-container').innerHTML = navHTML;
    
    // --- MENU LOGIC ---
    const openBtn = document.getElementById('open-menu-btn');
    const closeBtn = document.getElementById('close-menu-btn');
    const menu = document.getElementById('mobile-menu');
    const overlay = document.getElementById('menu-overlay');

    function toggleMenu() {
        menu.classList.toggle('-translate-x-full');
        if (menu.classList.contains('-translate-x-full')) {
            overlay.classList.remove('opacity-100', 'pointer-events-auto');
            overlay.classList.add('opacity-0', 'pointer-events-none');
            document.body.style.overflow = ''; 
        } else {
            overlay.classList.remove('opacity-0', 'pointer-events-none');
            overlay.classList.add('opacity-100', 'pointer-events-auto');
            document.body.style.overflow = 'hidden'; 
        }
    }

    openBtn.addEventListener('click', toggleMenu);
    closeBtn.addEventListener('click', toggleMenu);
    overlay.addEventListener('click', toggleMenu);


    // --- DARK MODE LOGIC ---
    const themeToggleDesktop = document.getElementById('theme-toggle-desktop');
    const themeToggleMobile = document.getElementById('theme-toggle-mobile');
    const icons = document.querySelectorAll('#theme-toggle-desktop i, #theme-toggle-mobile i');

    function updateThemeIcons(isDark) {
        icons.forEach(icon => {
            if (isDark) {
                icon.classList.remove('fa-moon');
                icon.classList.add('fa-sun');
                icon.style.transform = 'rotate(360deg)';
                icon.style.color = '#fbbf24'; // Golden amber color for Sun
            } else {
                icon.classList.remove('fa-sun');
                icon.classList.add('fa-moon');
                icon.style.transform = 'rotate(0deg)';
                icon.style.color = ''; // Revert to default text-slate-600
            }
        });
    }

    // Check system preference or localStorage
    if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.classList.add('dark');
        updateThemeIcons(true);
    } else {
        document.documentElement.classList.remove('dark');
        updateThemeIcons(false);
    }

    // Toggle Action
    function toggleTheme() {
        document.documentElement.classList.toggle('dark');
        const isDark = document.documentElement.classList.contains('dark');
        
        if (isDark) {
            localStorage.theme = 'dark';
            updateThemeIcons(true);
        } else {
            localStorage.theme = 'light';
            updateThemeIcons(false);
        }
    }

    if(themeToggleDesktop) themeToggleDesktop.addEventListener('click', toggleTheme);
    if(themeToggleMobile) themeToggleMobile.addEventListener('click', toggleTheme);
}

// --- GLOBAL CSS OVERRIDE FOR DARK MODE ---
// This injects a stylesheet into every page to force dark mode colors seamlessly
const globalDarkModeStyles = `
<style>
    /* Base Body Overrides */
    html.dark body { background-color: #0f172a !important; color: #f8fafc !important; }
    
    /* Global Cards & White Sections */
    html.dark .bg-white { background-color: #1e293b !important; border-color: #334155 !important; }
    
    /* Lighter Gray background areas */
    html.dark .bg-slate-50, html.dark .bg-slate-100 { background-color: #0f172a !important; border-color: #334155 !important; }
    
    /* Text Color Normalization */
    html.dark .text-slate-900, html.dark .text-slate-800, html.dark .text-slate-700 { color: #f8fafc !important; }
    html.dark .text-slate-600, html.dark .text-slate-500 { color: #94a3b8 !important; }
    
    /* Borders */
    html.dark .border-slate-200, html.dark .border-slate-100 { border-color: #334155 !important; }
    
    /* Header Translucency Fix */
    html.dark .bg-white\\/70 { background-color: rgba(30, 41, 59, 0.85) !important; border-color: rgba(51, 65, 85, 0.5) !important; }
    
    /* Keep Primary Accents Vibrant */
    html.dark .text-indigo-600 { color: #818cf8 !important; }
    html.dark .bg-indigo-50 { background-color: rgba(99, 102, 241, 0.1) !important; border-color: rgba(99, 102, 241, 0.2) !important; }
    
    /* Mobile Menu Drawer Fix */
    html.dark #mobile-menu { background-color: #1e293b !important; border-color: #334155 !important; }
    html.dark #mobile-menu .bg-slate-50 { background-color: #0f172a !important; }
    
    /* Buttons / Hover states */
    html.dark .hover\\:bg-slate-100:hover, html.dark .hover\\:bg-slate-200:hover { background-color: #334155 !important; color: #f8fafc !important; }
</style>
`;
document.head.insertAdjacentHTML('beforeend', globalDarkModeStyles);
