// ==============================================================================
// 0. FLOW CORE ENGINE (Global State, Zero-Latency Cache & UI Toasts)
// ==============================================================================
window.KTUFlow = (function() {
    const PROFILE_KEY = 'ktu_flow_profile_v2';
    const RECENT_KEY = 'ktu_flow_recent_v2';
    const CATALOG_CACHE_KEY = 'ktu_flow_catalog_cache_v2';
    let memoryCatalog = null;

    return {
        // 1. Student Profile Sync (Scheme, Branch, Semester across all pages)
        getProfile() {
            try {
                return JSON.parse(localStorage.getItem(PROFILE_KEY)) || { scheme: '', branch: '', sem: '' };
            } catch (e) {
                return { scheme: '', branch: '', sem: '' };
            }
        },
        setProfile(updates) {
            try {
                const current = this.getProfile();
                const next = { ...current, ...updates };
                localStorage.setItem(PROFILE_KEY, JSON.stringify(next));
                window.dispatchEvent(new CustomEvent('ktu:profile-updated', { detail: next }));
                return next;
            } catch (e) {}
        },

        // 2. Recent Course Queries Memory
        getRecent() {
            try {
                return JSON.parse(localStorage.getItem(RECENT_KEY)) || [];
            } catch (e) {
                return [];
            }
        },
        addRecent(code) {
            if (!code) return;
            try {
                const clean = code.trim().toUpperCase();
                const list = [clean, ...this.getRecent().filter(item => item !== clean)].slice(0, 6);
                localStorage.setItem(RECENT_KEY, JSON.stringify(list));
                return list;
            } catch (e) {}
        },

        // 3. Zero-Latency Subject Catalog Loader (Memory + SessionStorage)
        async getCatalog(url = '/ktu_subjects_no_lab.json') {
            if (memoryCatalog) return memoryCatalog;
            try {
                const cached = sessionStorage.getItem(CATALOG_CACHE_KEY);
                if (cached) {
                    memoryCatalog = JSON.parse(cached);
                    return memoryCatalog;
                }
            } catch (e) {}

            const response = await fetch(url);
            if (!response.ok) throw new Error('Catalog fetch failed');
            memoryCatalog = await response.json();
            try {
                sessionStorage.setItem(CATALOG_CACHE_KEY, JSON.stringify(memoryCatalog));
            } catch (e) {}
            return memoryCatalog;
        },

        // 4. Global Liquid Glass Toast Notification (Replaces native alert())
        toast(message, type = 'success') {
            const existing = document.getElementById('ktu-flow-toast');
            if (existing) existing.remove();

            const dotColor = type === 'error' ? 'bg-rose-400' : type === 'amber' ? 'bg-amber-400' : 'bg-emerald-400 animate-pulse';
            const toast = document.createElement('div');
            toast.id = 'ktu-flow-toast';
            toast.className = 'fixed bottom-5 left-1/2 -translate-x-1/2 z-[110] bg-slate-900/95 dark:bg-slate-800/95 text-white text-xs font-bold py-2.5 px-4 rounded-full shadow-2xl backdrop-blur-md border border-slate-700/60 flex items-center gap-2.5 transition-all duration-300 transform translate-y-10 opacity-0 pointer-events-none whitespace-nowrap';
            toast.innerHTML = `
                <span class="w-2 h-2 rounded-full ${dotColor} shrink-0"></span>
                <span>${message}</span>
            `;
            document.body.appendChild(toast);

            requestAnimationFrame(() => {
                toast.classList.remove('translate-y-10', 'opacity-0');
            });

            setTimeout(() => {
                toast.classList.add('translate-y-10', 'opacity-0');
                setTimeout(() => toast.remove(), 300);
            }, 2200);
        }
    };
})();

// ==============================================================================
// 1. AUTO THEME ENGINE & ADAPTIVE GLASSMORPHISM (Light Mode Default)
// ==============================================================================
(function initTheme() {
    const savedTheme = localStorage.getItem('kt_theme') || 'light';
    if (savedTheme === 'dark') {
        document.documentElement.classList.add('dark');
    } else {
        document.documentElement.classList.remove('dark');
    }
    
    if (!document.getElementById('kt-dark-theme-styles')) {
        const style = document.createElement('style');
        style.id = 'kt-dark-theme-styles';
        style.innerHTML = `
            /* ==================================================================
               A. LIGHT MODE ENHANCEMENTS (Crisp glass borders across laptops/phones)
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
                border: 1.5px solid rgba(0, 0, 0, 0.12) !important;
                box-shadow: inset 0 1px 1px #fff, 0 16px 40px rgba(31, 38, 135, 0.07) !important;
            }
            html:not(.dark) select.custom-select {
                border: 1.5px solid rgba(0, 0, 0, 0.12) !important;
            }
            html:not(.dark) span.bg-white\\/80 {
                border: 1px solid rgba(0, 0, 0, 0.12) !important;
            }

            /* ==================================================================
               B. DARK MODE ENGINE (Unified across index.html, notes.html & pyq.html)
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
            html.dark .text-slate-400:not(.text-transparent) { color: #94a3b8 !important; }

            /* 4. Ambient Parallax Orbs (Screen mode prevents pitch-black orbs) */
            html.dark #mouse-orb-1,
            html.dark #mouse-orb-2 {
                mix-blend-mode: screen !important;
                opacity: 0.35 !important;
                filter: blur(80px) !important;
            }

            /* 5. 3D Real-Glass & PYQ Result-Glass Cards */
            html.dark .real-glass {
                background: rgba(15, 23, 42, 0.72) !important;
                backdrop-filter: blur(28px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(28px) saturate(180%) !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                border-top: 1px solid rgba(255, 255, 255, 0.22) !important;
                border-left: 1px solid rgba(255, 255, 255, 0.14) !important;
                box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6) !important;
            }
            html.dark .result-glass {
                background: rgba(15, 23, 42, 0.68) !important;
                backdrop-filter: blur(20px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
                border: 1px solid rgba(255, 255, 255, 0.09) !important;
                border-top: 1px solid rgba(255, 255, 255, 0.18) !important;
                box-shadow: 0 10px 28px rgba(0, 0, 0, 0.4) !important;
            }
            html.dark .result-glass:hover {
                background: rgba(30, 41, 59, 0.85) !important;
                border-color: rgba(59, 130, 246, 0.45) !important;
                box-shadow: 0 16px 36px rgba(0, 0, 0, 0.55) !important;
            }

            /* 6. Inputs & Dropdowns (Notes & PYQ) */
            html.dark .inner-glass,
            html.dark .glass-input,
            html.dark select.custom-select {
                background-color: rgba(9, 14, 26, 0.65) !important;
                border: 1.5px solid rgba(255, 255, 255, 0.12) !important;
                color: #f8fafc !important;
            }
            html.dark select.custom-select {
                background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%2394a3b8%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E") !important;
            }
            html.dark .glass-input:focus {
                background-color: rgba(15, 23, 42, 0.9) !important;
                border-color: #3b82f6 !important;
                box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.2) !important;
            }
            html.dark .glass-input:disabled {
                background-color: rgba(15, 23, 42, 0.35) !important;
                color: #475569 !important;
                border-color: rgba(255, 255, 255, 0.05) !important;
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

            /* 7. Branch Cards */
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

            /* 8. Disabled / Coming Soon Cards */
            html.dark .cursor-not-allowed {
                opacity: 0.55 !important;
            }
            html.dark .cursor-not-allowed .text-slate-700 {
                color: #94a3b8 !important;
            }
            html.dark .cursor-not-allowed .text-slate-400 {
                color: #64748b !important;
            }

            /* 9. Subtle Surface Overrides for White Utility Classes */
            html.dark .border-white {
                border-color: rgba(255, 255, 255, 0.1) !important;
            }
            html.dark .bg-white\\/80,
            html.dark .bg-white\\/70,
            html.dark .bg-white\\/90 {
                background-color: rgba(255, 255, 255, 0.06) !important;
                border-color: rgba(255, 255, 255, 0.1) !important;
            }
            html.dark .bg-slate-200\\/50,
            html.dark .bg-slate-200\\/60 {
                background-color: rgba(15, 23, 42, 0.75) !important;
                border-color: rgba(255, 255, 255, 0.08) !important;
            }

            /* 10. Trending Searches Tags */
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

            /* 11. Footer */
            html.dark footer,
            html.dark footer.bg-white\\/50,
            html.dark footer.bg-white\\/60 {
                background-color: rgba(7, 11, 20, 0.85) !important;
                border-top-color: rgba(255, 255, 255, 0.08) !important;
            }

            /* 12. INDEX.HTML Glass & Hybrid Cards */
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

            /* 15. Header, Theme Toggles & Liquid Glass Mobile Menu */
            html.dark header {
                background-color: rgba(7, 11, 20, 0.82) !important;
                border-bottom-color: rgba(255, 255, 255, 0.08) !important;
            }
            html.dark #mobile-menu {
                background: rgba(11, 15, 25, 0.92) !important;
                border-right-color: rgba(255, 255, 255, 0.08) !important;
            }
            html.dark #mobile-menu .drawer-header {
                background: rgba(7, 11, 20, 0.6) !important;
                border-bottom-color: rgba(255, 255, 255, 0.08) !important;
            }
            html.dark #mobile-menu a { color: #cbd5e1 !important; }
            html.dark #mobile-menu a:hover {
                background-color: rgba(255, 255, 255, 0.06) !important;
                color: #ffffff !important;
            }
            html.dark #mobile-menu a.bg-indigo-50 {
                background-color: rgba(79, 70, 229, 0.18) !important;
                color: #818cf8 !important;
                border-color: rgba(99, 102, 241, 0.35) !important;
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
// 2. GOOGLE ANALYTICS 4 (GA4) LIVE TRACKING
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
// 3. RESPONSIVE NAVIGATION LOADER (Exact Branding Lockup + Liquid Glass Drawer)
// ==============================================================================
function loadNavigation(activePage, basePath = '', isBlog = false) { 
    const container = document.getElementById('navigation-container');
    if (!container) return;

    const logoExtension = isBlog ? ' <span class="text-slate-400 font-medium ml-1">| Blog</span>' : '';

    const navItemClass = (key) => activePage === key
        ? 'bg-indigo-50 text-indigo-700 font-bold border border-indigo-100 shadow-sm'
        : 'text-slate-600 hover:text-indigo-600 hover:bg-indigo-50/60 font-semibold border border-transparent';

    const navIconClass = (key) => activePage === key ? 'text-indigo-600' : 'text-slate-400';

    const navHTML = `
        <!-- Liquid Glass Mobile Drawer -->
        <div id="mobile-menu" aria-hidden="true" style="visibility: hidden; backdrop-filter: blur(28px) saturate(180%); -webkit-backdrop-filter: blur(28px) saturate(180%);" 
             class="fixed inset-y-0 left-0 w-72 bg-white/95 shadow-2xl transform -translate-x-full z-[60] flex flex-col border-r border-slate-200/80 will-change-transform">
            
            <div class="drawer-header p-5 border-b border-slate-100 flex justify-between items-center bg-slate-50/70">
                <div class="flex items-center gap-2">
                    <img src="/k.png" alt="Kerala Timetable Logo" class="w-6 h-6 object-contain shrink-0" width="24" height="24" />
                    <span class="text-base font-extrabold text-slate-900 tracking-tight leading-none">Kerala <span class="text-indigo-600">Timetable</span></span>
                </div>
                <button id="close-menu-btn" aria-label="Close menu" class="w-8 h-8 flex items-center justify-center text-slate-400 hover:text-rose-500 transition-all rounded-full hover:bg-white shadow-sm active:scale-95 focus:outline-none">
                    <i class="fas fa-times text-base"></i>
                </button>
            </div>
            
            <nav class="flex-grow py-4 px-3.5 flex flex-col gap-1 overflow-y-auto">
                <p class="px-3 pt-1 pb-1.5 text-[10px] font-extrabold uppercase tracking-wider text-slate-400">Academics</p>
                
                <a href="/index.html" class="flex items-center gap-3 px-3.5 py-2.5 rounded-2xl text-sm transition-all active:scale-[0.98] ${navItemClass('home')}">
                    <i class="fas fa-home w-5 text-center ${navIconClass('home')}"></i> Home
                </a>
                
                <a href="/timetable.html" class="flex items-center gap-3 px-3.5 py-2.5 rounded-2xl text-sm transition-all active:scale-[0.98] ${navItemClass('timetable')}">
                    <i class="fas fa-calendar-day w-5 text-center ${navIconClass('timetable')}"></i> Timetables
                </a>
                
                <a href="/notes.html" class="flex items-center gap-3 px-3.5 py-2.5 rounded-2xl text-sm transition-all active:scale-[0.98] ${navItemClass('notes')}">
                    <i class="fas fa-book-open w-5 text-center ${navIconClass('notes')}"></i> Study Notes
                </a>

                <a href="/pyq.html" class="flex items-center gap-3 px-3.5 py-2.5 rounded-2xl text-sm transition-all active:scale-[0.98] ${navItemClass('pyq')}">
                    <i class="fas fa-file-alt w-5 text-center ${navIconClass('pyq')}"></i> Previous Papers
                </a>

                <p class="px-3 pt-4 pb-1.5 text-[10px] font-extrabold uppercase tracking-wider text-slate-400">Community & Updates</p>

                <a href="/doubts.html" class="flex items-center gap-3 px-3.5 py-2.5 rounded-2xl text-sm transition-all active:scale-[0.98] ${navItemClass('qa')}">
                    <i class="fas fa-comments w-5 text-center ${navIconClass('qa')}"></i> Q&A Hub
                </a>
                
                <a href="/updates.html" class="flex items-center gap-3 px-3.5 py-2.5 rounded-2xl text-sm transition-all active:scale-[0.98] ${navItemClass('updates')}">
                    <i class="fas fa-bullhorn w-5 text-center ${navIconClass('updates')}"></i> Latest Updates
                </a>
                
                <a href="/blog/index.html" class="flex items-center gap-3 px-3.5 py-2.5 rounded-2xl text-sm transition-all active:scale-[0.98] ${navItemClass('blog')}">
                    <i class="fas fa-feather-alt w-5 text-center ${navIconClass('blog')}"></i> Blog
                </a>

                <a href="/status.html" class="flex items-center gap-3 px-3.5 py-2.5 rounded-2xl text-sm transition-all active:scale-[0.98] ${navItemClass('status')}">
                    <i class="fas fa-server w-5 text-center ${navIconClass('status')}"></i> Server Status
                </a>

                <a href="/about.html" class="flex items-center gap-3 px-3.5 py-2.5 rounded-2xl text-sm transition-all active:scale-[0.98] ${navItemClass('about')}">
                    <i class="fas fa-info-circle w-5 text-center ${navIconClass('about')}"></i> About
                </a>
            </nav>
        </div>

        <div id="menu-overlay" style="visibility: hidden;" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 opacity-0 pointer-events-none will-change-[opacity]"></div>

        <!-- EXACT BRAND HEADER (Font, Size, Alignment Locked 1:1) -->
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
                    <a href="/notes.html" class="text-sm px-4 py-2 rounded-full flex items-center gap-2 transition-all active:scale-95 ${activePage === 'notes' ? 'font-bold text-indigo-700 bg-indigo-50 border border-indigo-100 shadow-sm' : 'font-bold text-slate-600 hover:text-indigo-600 hover:bg-slate-100'}">
                        <i class="fas fa-book-open text-[10px]"></i> Study Notes
                    </a>
                    
                    <a href="/pyq.html" class="text-sm px-4 py-2 rounded-full flex items-center gap-2 transition-all active:scale-95 ${activePage === 'pyq' ? 'font-bold text-indigo-700 bg-indigo-50 border border-indigo-100 shadow-sm' : 'font-bold text-slate-600 hover:text-indigo-600 hover:bg-slate-100'}">
                        <i class="fas fa-file-alt text-[10px]"></i> PYQs
                    </a>

                    <a href="/doubts.html" class="text-sm px-4 py-2 rounded-full flex items-center gap-2 transition-all active:scale-95 ${activePage === 'qa' ? 'font-bold text-indigo-700 bg-indigo-50 border border-indigo-100 shadow-sm' : 'font-bold text-slate-600 hover:text-indigo-600 hover:bg-slate-100'}">
                        <i class="fas fa-comments text-[10px]"></i> Q&A
                    </a>
                    
                    <div class="w-px h-5 bg-slate-200 mx-1"></div>
                    
                    <a href="/updates.html" class="text-sm px-4 py-2 rounded-full flex items-center gap-2 transition-all active:scale-95 ${activePage === 'updates' ? 'font-bold text-white bg-indigo-600 shadow-md' : 'font-bold text-slate-600 bg-slate-100 hover:bg-indigo-600 hover:text-white'}">
                        <i class="fas fa-bullhorn text-[10px]"></i> Notice Board
                    </a>

                    <!-- Desktop Theme Toggle -->
                    <button class="theme-toggle-btn w-9 h-9 ml-1 rounded-full flex items-center justify-center bg-slate-100 text-slate-600 hover:bg-slate-200 border border-slate-200 transition-all active:scale-95 shadow-inner focus:outline-none" aria-label="Toggle Theme">
                        <i class="fas fa-moon text-[13px]"></i>
                    </button>
                </div>
                
                <div class="lg:hidden flex items-center gap-2">
                    <!-- Mobile Theme Toggle -->
                    <button class="theme-toggle-btn w-10 h-10 flex items-center justify-center bg-slate-100 text-slate-600 rounded-full border border-slate-200 shadow-sm transition-all active:scale-95 focus:outline-none" aria-label="Toggle Theme">
                        <i class="fas fa-moon text-[14px]"></i>
                    </button>
                    <a href="/updates.html" aria-label="Notifications" class="w-10 h-10 flex items-center justify-center bg-indigo-50 text-indigo-600 rounded-full border border-indigo-100 shadow-sm transition-all active:scale-95">
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
            btn.innerHTML = isDark 
                ? '<i class="fas fa-sun text-[14px] text-amber-400"></i>' 
                : '<i class="fas fa-moon text-[14px] text-slate-600"></i>';
        });
    }
    
    updateThemeIcons();
    
    themeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            document.documentElement.classList.toggle('dark');
            const isDark = document.documentElement.classList.contains('dark');
            localStorage.setItem('kt_theme', isDark ? 'dark' : 'light');
            updateThemeIcons();
            window.KTUFlow.toast(isDark ? 'Dark Theme enabled' : 'Light Theme enabled', isDark ? 'success' : 'amber');
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

            menu.style.transition = 'transform 0.32s cubic-bezier(0.22, 1, 0.36, 1)';
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
            }, 320);
        }
    }

    openBtn?.addEventListener('click', () => setMenuState(true));
    closeBtn?.addEventListener('click', () => setMenuState(false));
    overlay.addEventListener('click', () => setMenuState(false));

    // Touch Swipe-Left to Close Mobile Drawer
    let touchStartX = 0;
    menu.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });
    menu.addEventListener('touchend', (e) => {
        const touchEndX = e.changedTouches[0].screenX;
        if (touchStartX - touchEndX > 50) {
            setMenuState(false);
        }
    }, { passive: true });

    window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !menu.classList.contains('-translate-x-full')) {
            setMenuState(false);
        }
    });
}

// ==============================================================================
// 4. GLOBAL AD INJECTOR STRICTLY FOR NOTE PAGES
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
        testImage.decode().then(renderAd).catch(() => {});
    } else {
        testImage.onload = renderAd;
    }
}

// ==============================================================================
// 5. AUTHENTIC LIQUID GLASS WHATSAPP CHANNEL PROMPT
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
                 
                <div class="absolute -bottom-6 -left-6 w-36 h-36 bg-sky-500/25 blur-[40px] rounded-full pointer-events-none"></div>
                <div class="absolute -top-6 -right-6 w-36 h-36 bg-emerald-500/20 blur-[40px] rounded-full pointer-events-none"></div>
                <div class="absolute bottom-4 right-12 w-28 h-28 bg-emerald-400/20 blur-[35px] rounded-full pointer-events-none"></div>

                <div class="relative z-10 flex flex-col gap-3.5 sm:gap-4">
                    <div class="flex items-start justify-between gap-3">
                        <div class="flex items-center gap-3.5">
                            <div class="w-12 h-12 rounded-2xl bg-[#0f2c25]/90 border border-emerald-400/60 flex items-center justify-center text-emerald-400 text-2xl shadow-inner shrink-0">
                                <i class="fab fa-whatsapp"></i>
                            </div>
                            <div>
                                <h3 class="font-extrabold text-white text-base sm:text-lg tracking-tight leading-snug">Follow WhatsApp Channel</h3>
                            </div>
                        </div>
                        
                        <button id="ktu-wa-close-btn" aria-label="Close" class="text-slate-400 hover:text-white transition-colors p-1 rounded-full hover:bg-white/10 focus:outline-none shrink-0">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
                            </svg>
                        </button>
                    </div>

                    <p class="text-slate-300 text-xs sm:text-sm font-medium leading-relaxed pl-0.5">
                        Follow our channel for latest <strong class="text-sky-300 font-bold">KTU Updates</strong>, alerts & verified <strong class="text-emerald-300 font-bold">Study Notes</strong>.
                    </p>

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
// 6. SAFE AUTO-INIT
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
