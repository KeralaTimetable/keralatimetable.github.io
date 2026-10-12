// ==============================================================================
// 0. AUTO DARK THEME ENGINE & ADAPTIVE GLASSMORPHISM
// ==============================================================================
(function initTheme() {
    const savedTheme = localStorage.getItem('kt_theme') || 'light';
    if (savedTheme === 'dark') {
        document.documentElement.classList.add('dark');
    }
    
    if (!document.getElementById('kt-dark-theme-styles')) {
        const style = document.createElement('style');
        style.id = 'kt-dark-theme-styles';
        style.innerHTML = `
            /* ==================================================================
               A. LIGHT MODE ENHANCEMENTS (Fixes laptop washing out in notes.html)
               ================================================================== */
            html:not(.dark) .branch-card {
                border: 1.5px solid rgba(0, 0, 0, 0.12) !important;
                background: rgba(255, 255, 255, 0.85) !important;
                box-shadow: 0 4px 18px -2px rgba(31, 38, 135, 0.06) !important;
            }
            html:not(.dark) .branch-card:hover {
                border-color: #000000 !important;
                background: #ffffff !important;
            }
            html:not(.dark) .real-glass {
                border: 1.5px solid rgba(0, 0, 0, 0.14) !important;
                box-shadow: inset 0 1px 1px #fff, 0 16px 40px rgba(31, 38, 135, 0.08) !important;
            }
            html:not(.dark) select.custom-select {
                border: 1.5px solid rgba(0, 0, 0, 0.12) !important;
            }
            html:not(.dark) span.bg-white\\/80 {
                border: 1px solid rgba(0, 0, 0, 0.12) !important;
            }

            /* ==================================================================
               B. DARK MODE ENGINE (Fixes all notes.html & index.html issues)
               ================================================================== */
            /* 1. Base Canvas */
            html.dark body,
            html.dark .bg-mesh {
                background-color: #070B14 !important;
                background-image: 
                    radial-gradient(at 0% 0%, rgba(54, 128, 103, 0.18) 0px, transparent 50%),
                    radial-gradient(at 100% 0%, rgba(37, 99, 235, 0.18) 0px, transparent 50%),
                    radial-gradient(at 100% 100%, rgba(54, 128, 103, 0.15) 0px, transparent 50%),
                    radial-gradient(at 0% 100%, rgba(15, 23, 42, 0.6) 0px, transparent 50%) !important;
                color: #f1f5f9 !important;
            }
            
            /* 2. Text Transparency Fix (Protects multi-color gradients) */
            html.dark .text-transparent {
                color: transparent !important;
                -webkit-text-fill-color: transparent !important;
            }

            /* 3. Text Hierarchy & Readability Fixes */
            html.dark .text-slate-900:not(.text-transparent) { color: #ffffff !important; }
            html.dark .text-slate-800:not(.text-transparent) { color: #f1f5f9 !important; }
            html.dark .text-slate-700:not(.text-transparent) { color: #e2e8f0 !important; }
            html.dark .text-slate-600:not(.text-transparent) { color: #cbd5e1 !important; }
            html.dark .text-slate-500:not(.text-transparent) { color: #94a3b8 !important; }
            html.dark .text-slate-400:not(.text-transparent) { color: #94a3b8 !important; } /* Fixed: Was #475569 */

            /* 4. NOTES.HTML FIX: Parallax Orbs (Screen mode prevents pitch-black orbs) */
            html.dark #mouse-orb-1,
            html.dark #mouse-orb-2 {
                mix-blend-mode: screen !important;
                opacity: 0.35 !important;
                filter: blur(80px) !important;
            }

            /* 5. NOTES.HTML FIX: 3D Real-Glass Finder Card */
            html.dark .real-glass {
                background: rgba(15, 23, 42, 0.7) !important;
                backdrop-filter: blur(28px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(28px) saturate(180%) !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                border-top: 1px solid rgba(255, 255, 255, 0.25) !important;
                border-left: 1px solid rgba(255, 255, 255, 0.15) !important;
                box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6) !important;
            }

            /* 6. NOTES.HTML FIX: Dropdown Inputs (Prevents hover:bg-white/70 whiteout) */
            html.dark .inner-glass,
            html.dark select.custom-select {
                background-color: rgba(0, 0, 0, 0.4) !important;
                border: 1px solid rgba(255, 255, 255, 0.12) !important;
                color: #f8fafc !important;
                background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%2394a3b8%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E") !important;
            }
            html.dark select.custom-select:hover,
            html.dark .inner-glass:hover {
                background-color: rgba(255, 255, 255, 0.08) !important;
                border-color: rgba(54, 128, 103, 0.5) !important;
            }
            html.dark select.custom-select option,
            html.dark select option {
                background-color: #0f172a !important;
                color: #f8fafc !important;
            }
            html.dark select option:disabled {
                color: #64748b !important;
            }

            /* 7. NOTES.HTML FIX: Branch Cards */
            html.dark .branch-card {
                background: rgba(255, 255, 255, 0.035) !important;
                backdrop-filter: blur(20px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
                border-top: 1px solid rgba(255, 255, 255, 0.18) !important;
                box-shadow: 0 10px 28px rgba(0, 0, 0, 0.35) !important;
            }
            html.dark .branch-card:hover {
                background: rgba(255, 255, 255, 0.08) !important;
                border-color: rgba(54, 128, 103, 0.6) !important;
                box-shadow: 0 16px 36px rgba(0, 0, 0, 0.5) !important;
            }
            html.dark .branch-card:hover h3 {
                color: #4ade80 !important;
            }
            html.dark .branch-card .bg-indigo-100 { background-color: rgba(99, 102, 241, 0.15) !important; }
            html.dark .branch-card .bg-emerald-100 { background-color: rgba(16, 185, 129, 0.15) !important; }

            /* 8. NOTES.HTML FIX: Disabled / Coming Soon Cards */
            html.dark .cursor-not-allowed {
                opacity: 0.55 !important;
            }
            html.dark .cursor-not-allowed .text-slate-700 {
                color: #94a3b8 !important;
            }
            html.dark .cursor-not-allowed .text-slate-400 {
                color: #64748b !important;
            }

            /* 9. NOTES.HTML FIX: Remove Harsh White Outlines */
            html.dark .border-white {
                border-color: rgba(255, 255, 255, 0.1) !important;
            }
            html.dark .bg-white\\/80,
            html.dark .bg-white\\/70 {
                background-color: rgba(255, 255, 255, 0.06) !important;
            }

            /* 10. NOTES.HTML FIX: Trending Searches Tags */
            html.dark span.bg-white\\/80 {
                background-color: rgba(255, 255, 255, 0.04) !important;
                border-color: rgba(255, 255, 255, 0.08) !important;
                color: #cbd5e1 !important;
            }
            html.dark span.bg-white\\/80:hover {
                background-color: rgba(54, 128, 103, 0.2) !important;
                border-color: rgba(54, 128, 103, 0.5) !important;
                color: #6ee7b7 !important;
            }

            /* 11. NOTES.HTML FIX: Footer (Prevents milky white slab) */
            html.dark footer,
            html.dark footer.bg-white\\/50 {
                background-color: rgba(7, 11, 20, 0.85) !important;
                border-top-color: rgba(255, 255, 255, 0.08) !important;
            }

            /* 12. INDEX.HTML GLASS & HYBRID CARD INTEGRATION */
            html.dark .glass-panel {
                background: rgba(255, 255, 255, 0.035) !important;
                backdrop-filter: blur(24px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(24px) saturate(180%) !important;
                border: 1px solid rgba(255, 255, 255, 0.09) !important;
                border-top: 1px solid rgba(255, 255, 255, 0.2) !important;
                box-shadow: 0 14px 40px rgba(0, 0, 0, 0.5) !important;
            }
            html.dark .glass-panel-hover:hover {
                background: rgba(255, 255, 255, 0.075) !important;
                border-color: rgba(54, 128, 103, 0.5) !important;
                box-shadow: 0 18px 48px rgba(0, 0, 0, 0.6) !important;
            }
            html.dark .hybrid-card {
                background: rgba(255, 255, 255, 0.035) !important;
                backdrop-filter: blur(20px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
                border-top: 1px solid rgba(255, 255, 255, 0.18) !important;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3) !important;
            }
            html.dark .hybrid-card:hover {
                background: rgba(255, 255, 255, 0.08) !important;
                border-color: rgba(54, 128, 103, 0.6) !important;
                box-shadow: 0 14px 32px rgba(0, 0, 0, 0.5) !important;
            }
            html.dark .hybrid-card .bg-white {
                background-color: rgba(255, 255, 255, 0.07) !important;
                border-color: rgba(255, 255, 255, 0.1) !important;
                color: #cbd5e1 !important;
            }
            html.dark .hybrid-card:hover .bg-white {
                background-color: #368067 !important;
                color: #ffffff !important;
                border-color: #368067 !important;
            }

            /* 13. Search bar on index.html */
            html.dark div[class*="bg-white/75"],
            html.dark div[class*="bg-white/60"],
            html.dark .glass-panel.bg-white\\/95 {
                background: rgba(15, 23, 42, 0.7) !important;
                border-color: rgba(255, 255, 255, 0.12) !important;
                box-shadow: inset 0 1px 1px rgba(255,255,255,0.1), 0 12px 36px rgba(0, 0, 0, 0.5) !important;
            }
            html.dark div[class*="focus-within:border-black"]:focus-within {
                border-color: #368067 !important;
            }

            /* 14. Global Note Ad in Dark Mode */
            html.dark #global-note-ad {
                background-color: rgba(255, 255, 255, 0.03) !important;
                border-color: rgba(255, 255, 255, 0.08) !important;
            }

            /* 15. Header, Theme Toggles & Navigation */
            html.dark header {
                background-color: rgba(7, 11, 20, 0.85) !important;
                border-bottom-color: rgba(255, 255, 255, 0.08) !important;
            }
            html.dark #mobile-menu {
                background-color: #0b0f19 !important;
                border-color: rgba(255, 255, 255, 0.08) !important;
            }
            html.dark #mobile-menu .bg-slate-50 {
                background-color: #070b14 !important;
                border-bottom-color: rgba(255, 255, 255, 0.08) !important;
            }
            html.dark #mobile-menu a { color: #cbd5e1 !important; }
            html.dark #mobile-menu a:hover {
                background-color: rgba(255, 255, 255, 0.05) !important;
                color: #ffffff !important;
            }
            html.dark #mobile-menu a.bg-indigo-50 {
                background-color: rgba(54, 128, 103, 0.2) !important;
                color: #34d399 !important;
                border-color: rgba(54, 128, 103, 0.4) !important;
            }
            html.dark .theme-toggle-btn {
                background-color: rgba(255, 255, 255, 0.07) !important;
                border-color: rgba(255, 255, 255, 0.12) !important;
                color: #f1f5f9 !important;
            }
            html.dark .theme-toggle-btn:hover {
                background-color: rgba(255, 255, 255, 0.15) !important;
            }
        `;
        document.head.appendChild(style);
    }
})();

// ==============================================================================
// 1. GOOGLE ANALYTICS 4 (GA4) LIVE TRACKING
// ==============================================================================
(function() {
    if (window._ga4Initialized) return;
    window._ga4Initialized = true;

    const gaScript = document.createElement('script');
    gaScript.async = true;
    gaScript.src = 'https://www.googletagmanager.com/gtag/js?id=G-TK5MBC372D';
    document.head.appendChild(gaScript);

    window.dataLayer = window.dataLayer || [];
    function gtag(){ dataLayer.push(arguments); }
    gtag('js', new Date());
    gtag('config', 'G-TK5MBC372D');
})();

// ==============================================================================
// 2. RESPONSIVE NAVIGATION LOADER
// ==============================================================================
function loadNavigation(activePage, basePath = '', isBlog = false) { 
    const container = document.getElementById('navigation-container');
    if (!container) return;

    const logoExtension = isBlog ? ' <span class="text-slate-400 font-medium ml-1">| Blog</span>' : '';

    const navHTML = `
        <div id="mobile-menu" aria-hidden="true" style="visibility: hidden;" class="fixed inset-y-0 left-0 w-64 bg-white shadow-2xl transform -translate-x-full z-[60] flex flex-col border-r border-slate-100 will-change-transform">
            <div class="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50">
                <h2 class="text-lg font-extrabold text-slate-900 tracking-tight">Menu</h2>
                <button id="close-menu-btn" aria-label="Close menu" class="p-2 text-slate-400 hover:text-red-500 transition-colors rounded-full hover:bg-white shadow-sm focus:outline-none">
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

                <a href="/pyq.html" class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activePage === 'pyq' ? 'bg-indigo-50 text-indigo-700 font-bold border border-indigo-100' : 'text-slate-600 hover:text-indigo-600 hover:bg-indigo-50 font-semibold'}">
                    <i class="fas fa-file-alt w-5 text-center ${activePage === 'pyq' ? 'text-indigo-600' : 'text-slate-400'}"></i> Previous Papers
                </a>

                <a href="/doubts.html" class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activePage === 'qa' ? 'bg-indigo-50 text-indigo-700 font-bold border border-indigo-100' : 'text-slate-600 hover:text-indigo-600 hover:bg-indigo-50 font-semibold'}">
                    <i class="fas fa-comments w-5 text-center ${activePage === 'qa' ? 'text-indigo-600' : 'text-slate-400'}"></i> Q&A Hub
                </a>

                <a href="/status.html" class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activePage === 'status' ? 'bg-indigo-50 text-indigo-700 font-bold border border-indigo-100' : 'text-slate-600 hover:text-indigo-600 hover:bg-indigo-50 font-semibold'}">
                    <i class="fas fa-server w-5 text-center ${activePage === 'status' ? 'text-indigo-600' : 'text-slate-400'}"></i> Server Status
                </a>
                
                <a href="/updates.html" class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activePage === 'updates' ? 'bg-indigo-50 text-indigo-700 font-bold border border-indigo-100' : 'text-slate-600 hover:text-indigo-600 hover:bg-indigo-50 font-semibold'}">
                    <i class="fas fa-bullhorn w-5 text-center ${activePage === 'updates' ? 'text-indigo-600' : 'text-slate-400'}"></i> Latest Updates
                </a>
                
                <a href="/blog/index.html" class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activePage === 'blog' ? 'bg-indigo-50 text-indigo-700 font-bold border border-indigo-100' : 'text-slate-600 hover:text-indigo-600 hover:bg-indigo-50 font-semibold'}">
                    <i class="fas fa-feather-alt w-5 text-center ${activePage === 'blog' ? 'text-indigo-600' : 'text-slate-400'}"></i> Blog
                </a>

                <a href="/about.html" class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activePage === 'about' ? 'bg-indigo-50 text-indigo-700 font-bold border border-indigo-100' : 'text-slate-600 hover:text-indigo-600 hover:bg-indigo-50 font-semibold'}">
                    <i class="fas fa-info-circle w-5 text-center ${activePage === 'about' ? 'text-indigo-600' : 'text-slate-400'}"></i> About
                </a>
            </nav>
        </div>

        <div id="menu-overlay" style="visibility: hidden;" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 opacity-0 pointer-events-none will-change-[opacity]"></div>

        <header class="sticky top-0 z-40 bg-white/70 backdrop-blur-md border-b border-slate-200/50 shadow-sm transition-all duration-300">
            <div class="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex justify-between items-center">
                <div class="flex items-center gap-3">
                    <button id="open-menu-btn" aria-label="Open menu" class="p-2 -ml-2 text-slate-600 hover:text-indigo-600 hover:bg-slate-100 rounded-lg transition-colors focus:outline-none lg:hidden">
                        <i class="fas fa-bars text-xl"></i>
                    </button>
                    <a href="/index.html" class="flex items-center gap-2 hover:opacity-80 transition-opacity">
                        <img src="/k.png" alt="Kerala Timetable Logo" class="w-6 h-6 sm:w-7 sm:h-7 object-contain shrink-0" width="28" height="28" />
                        <h1 class="text-xl sm:text-2xl font-extrabold tracking-tight text-slate-900 leading-none">Kerala <span class="text-indigo-600">Timetable</span>${logoExtension}</h1>
                    </a>
                </div>

                <div class="hidden lg:flex gap-2 items-center">
                    <a href="/notes.html" class="text-sm px-4 py-2 rounded-full flex items-center gap-2 transition-colors ${activePage === 'notes' ? 'font-bold text-indigo-700 bg-indigo-50 border border-indigo-100 shadow-sm' : 'font-bold text-slate-600 hover:text-indigo-600 hover:bg-slate-100'}">
                        <i class="fas fa-book-open text-[10px]"></i> Study Notes
                    </a>
                    
                    <a href="/pyq.html" class="text-sm px-4 py-2 rounded-full flex items-center gap-2 transition-colors ${activePage === 'pyq' ? 'font-bold text-indigo-700 bg-indigo-50 border border-indigo-100 shadow-sm' : 'font-bold text-slate-600 hover:text-indigo-600 hover:bg-slate-100'}">
                        <i class="fas fa-file-alt text-[10px]"></i> PYQs
                    </a>

                    <a href="/doubts.html" class="text-sm px-4 py-2 rounded-full flex items-center gap-2 transition-colors ${activePage === 'qa' ? 'font-bold text-indigo-700 bg-indigo-50 border border-indigo-100 shadow-sm' : 'font-bold text-slate-600 hover:text-indigo-600 hover:bg-slate-100'}">
                        <i class="fas fa-comments text-[10px]"></i> Q&A
                    </a>
                    
                    <div class="w-px h-5 bg-slate-200 mx-1"></div>
                    
                    <a href="/updates.html" class="text-sm px-4 py-2 rounded-full flex items-center gap-2 transition-colors ${activePage === 'updates' ? 'font-bold text-white bg-indigo-600 shadow-md' : 'font-bold text-slate-600 bg-slate-100 hover:bg-indigo-600 hover:text-white'}">
                        <i class="fas fa-bullhorn text-[10px]"></i> Notice Board
                    </a>

                    <!-- Desktop Theme Toggle -->
                    <button class="theme-toggle-btn w-9 h-9 ml-1 rounded-full flex items-center justify-center bg-slate-100 text-slate-600 hover:bg-slate-200 border border-slate-200 transition-colors shadow-inner focus:outline-none" aria-label="Toggle Theme">
                        <i class="fas fa-moon text-[13px]"></i>
                    </button>
                </div>
                
                <div class="lg:hidden flex items-center gap-2">
                    <!-- Mobile Theme Toggle -->
                    <button class="theme-toggle-btn w-10 h-10 flex items-center justify-center bg-slate-100 text-slate-600 rounded-full border border-slate-200 shadow-sm transition-colors focus:outline-none" aria-label="Toggle Theme">
                        <i class="fas fa-moon text-[14px]"></i>
                    </button>
                    <a href="/updates.html" aria-label="Notifications" class="w-10 h-10 flex items-center justify-center bg-indigo-50 text-indigo-600 rounded-full border border-indigo-100 shadow-sm">
                       <i class="fas fa-bell"></i>
                    </a>
                </div>
            </div>
        </header>
    `;

    container.innerHTML = navHTML;
    
    // Theme Toggle Logic
    const themeBtns = document.querySelectorAll('.theme-toggle-btn');
    
    function updateThemeIcons() {
        const isDark = document.documentElement.classList.contains('dark');
        themeBtns.forEach(btn => {
            btn.innerHTML = isDark ? '<i class="fas fa-sun text-[14px] text-amber-400"></i>' : '<i class="fas fa-moon text-[14px] text-slate-600"></i>';
        });
    }
    
    updateThemeIcons();

    function showBetaToast(isDark) {
        const existingToast = document.getElementById('beta-theme-toast');
        if (existingToast) existingToast.remove();

        const toast = document.createElement('div');
        toast.id = 'beta-theme-toast';
        toast.className = 'fixed bottom-5 left-1/2 -translate-x-1/2 z-[100] bg-slate-900/95 dark:bg-slate-800/95 text-white text-xs font-bold py-2.5 px-4 rounded-full shadow-2xl backdrop-blur-md border border-slate-700/60 flex items-center gap-2.5 transition-all duration-300 transform translate-y-10 opacity-0';
        toast.innerHTML = isDark ? `
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>Dark Theme enabled</span>
        ` : `
            <span class="w-2 h-2 rounded-full bg-amber-400"></span>
            <span>Light Theme enabled</span>
        `;
        document.body.appendChild(toast);

        requestAnimationFrame(() => {
            toast.classList.remove('translate-y-10', 'opacity-0');
        });

        setTimeout(() => {
            toast.classList.add('translate-y-10', 'opacity-0');
            setTimeout(() => toast.remove(), 300);
        }, 2000);
    }
    
    themeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            document.documentElement.classList.toggle('dark');
            const isDark = document.documentElement.classList.contains('dark');
            localStorage.setItem('kt_theme', isDark ? 'dark' : 'light');
            updateThemeIcons();
            showBetaToast(isDark);
        });
    });

    const openBtn = document.getElementById('open-menu-btn');
    const closeBtn = document.getElementById('close-menu-btn');
    const menu = document.getElementById('mobile-menu');
    const overlay = document.getElementById('menu-overlay');

    if (!menu || !overlay) return;

    let menuTransitionTimeout = null;

    function setMenuState(isOpen) {
        clearTimeout(menuTransitionTimeout);

        if (isOpen) {
            menu.style.visibility = 'visible';
            overlay.style.visibility = 'visible';

            menu.classList.add('transition-transform', 'duration-300', 'ease-in-out');
            overlay.classList.add('transition-opacity', 'duration-300');

            void menu.offsetWidth;

            menu.classList.remove('-translate-x-full');
            menu.setAttribute('aria-hidden', 'false');
            overlay.classList.remove('opacity-0', 'pointer-events-none');
            overlay.classList.add('opacity-100', 'pointer-events-auto');
            document.body.style.overflow = 'hidden';
        } else {
            menu.classList.add('-translate-x-full');
            menu.setAttribute('aria-hidden', 'true');
            overlay.classList.remove('opacity-100', 'pointer-events-auto');
            overlay.classList.add('opacity-0', 'pointer-events-none');
            document.body.style.overflow = '';

            menuTransitionTimeout = setTimeout(() => {
                if (menu.getAttribute('aria-hidden') === 'true') {
                    menu.style.visibility = 'hidden';
                    overlay.style.visibility = 'hidden';
                }
            }, 300);
        }
    }

    openBtn?.addEventListener('click', () => setMenuState(true));
    closeBtn?.addEventListener('click', () => setMenuState(false));
    overlay.addEventListener('click', () => setMenuState(false));

    window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !menu.classList.contains('-translate-x-full')) {
            setMenuState(false);
        }
    });
}

// ==============================================================================
// 3. GLOBAL AD INJECTOR STRICTLY FOR NOTE PAGES
// ==============================================================================
function injectGlobalAd() {
    if (document.getElementById('global-note-ad')) return;

    const isNotePage = window.location.pathname.toLowerCase().includes('notes');
    const firstModule = document.querySelector('.module-card');
    
    if (!isNotePage || !firstModule || !firstModule.parentElement) return;

    const adImageUrl = '/images/Ad.png';
    const adLink = 'https://forms.gle/VT8NGk9vi7gT7tgT7';
    
    const testImage = new Image();
    testImage.src = adImageUrl;

    const renderAd = () => {
        const moduleGridContainer = firstModule.parentElement;
        const adHTML = `
            <a id="global-note-ad" href="${adLink}" target="_blank" rel="noopener noreferrer" class="fade-in-ad block w-full md:max-w-xl lg:max-w-2xl mx-auto mb-10 rounded-2xl overflow-hidden shadow-sm hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 group border border-slate-100 bg-slate-50">
                <img src="${adImageUrl}" alt="Vortex Tournament Registration" width="1881" height="836" loading="lazy" decoding="async" class="w-full h-auto group-hover:scale-105 transition-transform duration-500 ease-out">
            </a>
            <style>
                @keyframes fadeInAd { 
                    from { opacity: 0; transform: translateY(12px); } 
                    to { opacity: 1; transform: translateY(0); } 
                }
                .fade-in-ad { 
                    animation: fadeInAd 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards; 
                    will-change: opacity, transform; 
                }
            </style>
        `;
        moduleGridContainer.insertAdjacentHTML('beforebegin', adHTML);
    };

    if ('decode' in testImage) {
        testImage.decode().then(renderAd).catch(() => {
            console.warn("Global ad image not found or decoding failed. Injection skipped.");
        });
    } else {
        testImage.onload = renderAd;
        testImage.onerror = () => {
            console.warn("Global ad image not found. Injection skipped.");
        };
    }
}

// ==============================================================================
// 4. AUTHENTIC LIQUID GLASS WHATSAPP CHANNEL PROMPT (MATCHING SCREENSHOT 1:1)
// ==============================================================================
function initWhatsAppPopup() {
    const STORAGE_KEY = 'ktu_wa_popup_cooldown_until';
    const CANCEL_DAYS = 1;   
    const FOLLOW_DAYS = 20;  
    const CHANNEL_URL = 'https://whatsapp.com/channel/0029Vb7zhxw5vKABedfmht0D';

    const cooldownUntil = localStorage.getItem(STORAGE_KEY);
    if (cooldownUntil && Date.now() < parseInt(cooldownUntil, 10)) {
        return; 
    }

    setTimeout(() => {
        if (document.getElementById('ktu-wa-popup')) return;

        const popupHTML = `
            <div id="ktu-wa-popup" class="fixed bottom-5 left-1/2 -translate-x-1/2 sm:left-auto sm:right-6 sm:translate-x-0 z-[100] w-[calc(100%-2rem)] max-w-[430px] p-5 sm:p-6 rounded-[2rem] text-white shadow-2xl transition-all duration-500 ease-out transform translate-y-12 opacity-0 overflow-hidden will-change-transform"
                 style="
                    background: rgba(18, 24, 38, 0.78);
                    backdrop-filter: blur(32px) saturate(190%);
                    -webkit-backdrop-filter: blur(32px) saturate(190%);
                    border: 1px solid rgba(255, 255, 255, 0.12);
                    box-shadow: 
                        inset 0 1px 1px 0 rgba(255, 255, 255, 0.25),
                        0 24px 48px -12px rgba(0, 0, 0, 0.6);
                 ">
                 
                <!-- Ambient glowing refraction orbs inside the clear glass -->
                <div class="absolute -bottom-6 -left-6 w-36 h-36 bg-sky-500/25 blur-[40px] rounded-full pointer-events-none"></div>
                <div class="absolute -top-6 -right-6 w-36 h-36 bg-emerald-500/20 blur-[40px] rounded-full pointer-events-none"></div>
                <div class="absolute bottom-4 right-12 w-28 h-28 bg-emerald-400/20 blur-[35px] rounded-full pointer-events-none"></div>

                <div class="relative z-10 flex flex-col gap-3.5 sm:gap-4">
                    <!-- Top Row -->
                    <div class="flex items-start justify-between gap-3">
                        <div class="flex items-center gap-3.5">
                            <!-- WhatsApp Badge -->
                            <div class="w-12 h-12 rounded-2xl bg-[#0f2c25]/90 border border-emerald-400/60 flex items-center justify-center text-emerald-400 text-2xl shadow-inner shrink-0">
                                <i class="fab fa-whatsapp"></i>
                            </div>
                            <div>
                                <h3 class="font-extrabold text-white text-base sm:text-lg tracking-tight leading-snug">Follow WhatsApp Channel</h3>
                            </div>
                        </div>
                        
                        <!-- Close 'X' Button -->
                        <button id="ktu-wa-close-btn" aria-label="Close" class="text-slate-400 hover:text-white transition-colors p-1 rounded-full hover:bg-white/10 focus:outline-none shrink-0">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
                            </svg>
                        </button>
                    </div>

                    <!-- Description with Glowing Accents -->
                    <p class="text-slate-300 text-xs sm:text-sm font-medium leading-relaxed pl-0.5">
                        Follow our channel for latest <strong class="text-sky-300 font-bold">KTU Updates</strong>, alerts & verified <strong class="text-emerald-300 font-bold">Study Notes</strong>.
                    </p>

                    <!-- Pill Action Buttons -->
                    <div class="grid grid-cols-2 gap-3 pt-1">
                        <button id="ktu-wa-later-btn" class="w-full py-3 px-4 rounded-full bg-white/10 hover:bg-white/15 text-slate-200 font-bold text-xs sm:text-sm transition-all border border-white/5 active:scale-95 text-center">
                            Maybe Later
                        </button>
                        <a id="ktu-wa-follow-btn" href="${CHANNEL_URL}" target="_blank" rel="noopener noreferrer" class="w-full py-3 px-4 rounded-full bg-emerald-500 hover:bg-emerald-400 text-white font-bold text-xs sm:text-sm transition-all shadow-lg shadow-emerald-500/30 flex items-center justify-center gap-2 active:scale-95 text-center">
                            <span>Follow Channel</span>
                            <i class="fas fa-arrow-right text-xs"></i>
                        </a>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', popupHTML);

        const popup = document.getElementById('ktu-wa-popup');
        const closeBtn = document.getElementById('ktu-wa-close-btn');
        const laterBtn = document.getElementById('ktu-wa-later-btn');
        const followBtn = document.getElementById('ktu-wa-follow-btn');

        requestAnimationFrame(() => {
            popup.classList.remove('translate-y-12', 'opacity-0');
        });

        function dismissPopup(days) {
            const expireDate = Date.now() + days * 24 * 60 * 60 * 1000;
            localStorage.setItem(STORAGE_KEY, expireDate.toString());

            popup.classList.add('translate-y-12', 'opacity-0');
            setTimeout(() => {
                popup.remove();
            }, 350);
        }

        closeBtn?.addEventListener('click', () => dismissPopup(CANCEL_DAYS));
        laterBtn?.addEventListener('click', () => dismissPopup(CANCEL_DAYS));
        followBtn?.addEventListener('click', () => dismissPopup(FOLLOW_DAYS));
    }, 3500);
}

// ==============================================================================
// 5. SAFE AUTO-INIT
// ==============================================================================
function runInitializers() {
    injectGlobalAd();
    initWhatsAppPopup();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', runInitializers);
} else {
    runInitializers();
}
