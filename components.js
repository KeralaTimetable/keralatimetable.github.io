// ==============================================================================
// 0. AUTO DARK THEME ENGINE & CSS INJECTION
// ==============================================================================
(function initTheme() {
    const savedTheme = localStorage.getItem('kt_theme') || 'light';
    if (savedTheme === 'dark') {
        document.documentElement.classList.add('dark');
    }
    
    // Dynamically inject deep-dark glassmorphism CSS overrides for all pages
    if (!document.getElementById('kt-dark-theme-styles')) {
        const style = document.createElement('style');
        style.id = 'kt-dark-theme-styles';
        style.innerHTML = `
            /* Beautiful Dark Mode Overrides for Glassmorphism & Tailwind */
            html.dark body {
                background-color: #020617 !important;
                background-image: 
                    radial-gradient(at 0% 0%, rgba(30, 27, 75, 0.85) 0px, transparent 50%),
                    radial-gradient(at 100% 0%, rgba(15, 23, 42, 0.95) 0px, transparent 50%),
                    radial-gradient(at 100% 100%, rgba(23, 37, 84, 0.75) 0px, transparent 50%),
                    radial-gradient(at 0% 100%, rgba(49, 46, 129, 0.65) 0px, transparent 50%) !important;
                color: #f8fafc !important;
            }
            
            /* Text Color Conversions */
            html.dark .text-slate-900 { color: #f8fafc !important; }
            html.dark .text-slate-800 { color: #f1f5f9 !important; }
            html.dark .text-slate-700 { color: #e2e8f0 !important; }
            html.dark .text-slate-600 { color: #cbd5e1 !important; }
            html.dark .text-slate-500 { color: #94a3b8 !important; }
            html.dark .text-slate-400 { color: #64748b !important; }
            
            /* Background Conversions */
            html.dark .bg-white { background-color: rgba(15, 23, 42, 0.7) !important; border-color: rgba(255,255,255,0.08) !important; }
            html.dark .bg-white\\/60, html.dark .bg-white\\/70, html.dark .bg-white\\/80, html.dark .bg-white\\/90 { 
                background-color: rgba(15, 23, 42, 0.75) !important; 
                border-color: rgba(255,255,255,0.08) !important; 
            }
            html.dark .bg-slate-50 { background-color: rgba(15, 23, 42, 0.5) !important; }
            html.dark .bg-slate-100 { background-color: rgba(30, 41, 59, 0.7) !important; }
            
            /* Border Conversions */
            html.dark .border-slate-100, html.dark .border-slate-200 { border-color: rgba(255,255,255,0.1) !important; }
            html.dark .border-white { border-color: rgba(255,255,255,0.1) !important; }
            
            /* Premium Glass Panels in Dark Mode */
            html.dark .glass-panel, html.dark .real-glass {
                background: rgba(15, 23, 42, 0.6) !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5) !important;
            }
            html.dark .glass-panel-hover:hover {
                background: rgba(30, 41, 59, 0.8) !important;
                border: 1px solid rgba(255, 255, 255, 0.18) !important;
            }
            html.dark .glass-folder {
                background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.5) 100%) !important;
                border-color: rgba(255,255,255,0.12) !important;
                box-shadow: inset 0 0 20px rgba(255,255,255,0.05), 0 10px 30px rgba(0,0,0,0.4) !important;
            }
            
            /* Compact Cards */
            html.dark .hybrid-card, html.dark .inner-glass {
                background: rgba(15, 23, 42, 0.5) !important;
                border: 1px solid rgba(255, 255, 255, 0.08) !important;
            }
            html.dark .hybrid-card:hover {
                background: rgba(30, 41, 59, 0.85) !important;
                border-color: rgba(255, 255, 255, 0.2) !important;
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.45) !important;
            }
            
            /* Inputs and Forms */
            html.dark input, html.dark select, html.dark textarea, html.dark .glass-input {
                color: #f8fafc !important;
                background-color: rgba(30, 41, 59, 0.6) !important;
                border-color: rgba(255,255,255,0.15) !important;
            }
            html.dark input:focus, html.dark select:focus {
                background-color: rgba(15, 23, 42, 0.9) !important;
            }
            
            /* Mobile Navigation Drawer */
            html.dark #mobile-menu { background-color: #020617 !important; border-color: #1e293b !important; }
            html.dark #mobile-menu .bg-slate-50 { background-color: #0f172a !important; border-bottom-color: #1e293b !important; }
            html.dark #mobile-menu a { color: #cbd5e1 !important; }
            html.dark #mobile-menu a:hover { background-color: rgba(30, 41, 59, 0.7) !important; color: #f8fafc !important; }
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
            </nav>
        </div>

        <div id="menu-overlay" style="visibility: hidden;" class="fixed inset-0 bg-slate-900/20 backdrop-blur-sm z-50 opacity-0 pointer-events-none will-change-[opacity]"></div>

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
    
    // Theme Toggle Logic Execution
    const themeBtns = document.querySelectorAll('.theme-toggle-btn');
    
    function updateThemeIcons() {
        const isDark = document.documentElement.classList.contains('dark');
        themeBtns.forEach(btn => {
            btn.innerHTML = isDark ? '<i class="fas fa-sun text-[14px] text-amber-400"></i>' : '<i class="fas fa-moon text-[14px] text-slate-600"></i>';
            if(isDark) {
                btn.classList.remove('bg-slate-100', 'text-slate-600', 'border-slate-200');
                btn.classList.add('bg-slate-800', 'border-slate-700', 'text-amber-400');
            } else {
                btn.classList.remove('bg-slate-800', 'border-slate-700', 'text-amber-400');
                btn.classList.add('bg-slate-100', 'text-slate-600', 'border-slate-200');
            }
        });
    }
    
    updateThemeIcons();
    
    themeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            document.documentElement.classList.toggle('dark');
            const isDark = document.documentElement.classList.contains('dark');
            localStorage.setItem('kt_theme', isDark ? 'dark' : 'light');
            updateThemeIcons();
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
// 4. KTU WHATSAPP CHANNEL PROMO MINI POP-UP
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
            <div id="ktu-wa-popup" class="fixed bottom-4 right-4 sm:bottom-6 sm:right-6 z-50 w-[calc(100%-2rem)] sm:w-88 max-w-sm bg-white/95 backdrop-blur-md border border-slate-200 shadow-2xl rounded-2xl p-4 transition-all duration-300 ease-out transform translate-y-10 opacity-0 will-change-transform dark:bg-slate-900/95 dark:border-slate-700">
                <button id="ktu-wa-close-btn" aria-label="Close" class="absolute top-3 right-3 text-slate-400 hover:text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-800 dark:hover:text-slate-300 p-1.5 rounded-full transition-colors focus:outline-none">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                </button>

                <div class="flex items-start gap-3.5 pr-6">
                    <div class="w-10 h-10 rounded-xl bg-emerald-50 dark:bg-emerald-900/40 border border-emerald-100 dark:border-emerald-800 flex items-center justify-center shrink-0 shadow-sm text-emerald-600 dark:text-emerald-400">
                        <svg class="w-6 h-6 fill-current" viewBox="0 0 24 24">
                            <path d="M12.04 2c-5.46 0-9.91 4.45-9.91 9.91 0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38c1.45.79 3.08 1.21 4.74 1.21 5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.816 9.816 0 0012.04 2zm0 18.06c-1.48 0-2.93-.4-4.2-1.15l-.3-.18-3.12.82.83-3.04-.2-.31a8.106 8.106 0 01-1.24-4.29c0-4.5 3.66-8.16 8.16-8.16 2.18 0 4.23.85 5.77 2.39 1.54 1.54 2.39 3.59 2.39 5.77 0 4.5-3.66 8.16-8.16 8.16zm4.47-6.11c-.24-.12-1.45-.71-1.68-.79-.22-.08-.39-.12-.55.12-.17.24-.63.79-.77.95-.14.16-.28.18-.52.06-.24-.12-1.03-.38-1.96-1.21-.72-.65-1.21-1.45-1.36-1.69-.14-.24-.02-.37.1-.49.11-.11.24-.28.37-.43.12-.14.16-.24.24-.4.08-.16.04-.3-.02-.43-.06-.12-.55-1.33-.76-1.82-.2-.48-.41-.41-.56-.42-.14-.01-.31-.01-.48-.01-.17 0-.45.06-.68.32-.24.25-.9.88-.9 2.15 0 1.27.93 2.5 1.06 2.67.13.18 1.82 2.78 4.41 3.9 0.62.27 1.1.43 1.48.55.62.2 1.19.17 1.63.11.5-.08 1.45-.59 1.66-1.17.2-.57.2-1.07.14-1.17-.06-.11-.22-.17-.46-.29z"/>
                        </svg>
                    </div>

                    <div>
                        <h3 class="text-sm font-bold text-slate-900 dark:text-slate-100 leading-tight">Follow WhatsApp Channel</h3>
                        <p class="text-xs text-slate-500 dark:text-slate-400 mt-1 leading-relaxed">
                            Follow our channel for latest <b>KTU Updates</b>, alerts & verified <b>Study Notes</b>.
                        </p>
                    </div>
                </div>

                <div class="mt-3.5 flex items-center gap-2">
                    <button id="ktu-wa-later-btn" class="flex-1 py-2 px-3 text-xs font-semibold text-slate-600 hover:text-slate-800 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700 rounded-xl transition-colors">
                        Maybe Later
                    </button>
                    <a id="ktu-wa-follow-btn" href="${CHANNEL_URL}" target="_blank" rel="noopener noreferrer" class="flex-1 py-2 px-3 text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 shadow-sm hover:shadow rounded-xl text-center transition-all flex items-center justify-center gap-1.5">
                        Follow Channel
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3"/>
                        </svg>
                    </a>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', popupHTML);

        const popup = document.getElementById('ktu-wa-popup');
        const closeBtn = document.getElementById('ktu-wa-close-btn');
        const laterBtn = document.getElementById('ktu-wa-later-btn');
        const followBtn = document.getElementById('ktu-wa-follow-btn');

        requestAnimationFrame(() => {
            popup.classList.remove('translate-y-10', 'opacity-0');
        });

        function dismissPopup(days) {
            const expireDate = Date.now() + days * 24 * 60 * 60 * 1000;
            localStorage.setItem(STORAGE_KEY, expireDate.toString());

            popup.classList.add('translate-y-10', 'opacity-0');
            setTimeout(() => {
                popup.remove();
            }, 300);
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
