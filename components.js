// --- Google Analytics 4 (GA4) Live Tracking ---
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
// ----------------------------------------------

function loadNavigation(activePage, basePath = '', isBlog = false) { 
    const container = document.getElementById('navigation-container');
    if (!container) return;

    const logoExtension = isBlog ? ' <span class="text-slate-400 font-medium ml-1">| Blog</span>' : '';

    const navHTML = `
        <div id="mobile-menu" aria-hidden="true" class="fixed inset-y-0 left-0 w-64 bg-white shadow-2xl transform -translate-x-full z-[60] flex flex-col border-r border-slate-100 will-change-transform">
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
                    <i class="fas fa-file-alt w-5 text-center ${activePage === 'pyq' ? 'text-indigo-600' : 'text-slate-400'}"></i> Previous Year Questions Papers
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

        <div id="menu-overlay" class="fixed inset-0 bg-slate-900/20 backdrop-blur-sm z-50 opacity-0 pointer-events-none will-change-[opacity]"></div>

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
                        <i class="fas fa-file-alt text-[10px]"></i> PYQ Papers
                    </a>

                    <a href="/timetable.html" class="text-sm px-4 py-2 rounded-full flex items-center gap-2 transition-colors ${activePage === 'timetable' ? 'font-bold text-indigo-700 bg-indigo-50 border border-indigo-100 shadow-sm' : 'font-bold text-slate-600 hover:text-indigo-600 hover:bg-slate-100'}">
                        <i class="fas fa-calendar-day text-[10px]"></i> Timetables
                    </a>
                    
                    <div class="w-px h-5 bg-slate-200 mx-1"></div>
                    
                    <a href="/status.html" class="text-sm px-4 py-2 rounded-full flex items-center gap-2 transition-colors ${activePage === 'status' ? 'font-bold text-slate-800 bg-white border border-slate-200 shadow-sm' : 'font-bold text-slate-600 bg-slate-100 hover:bg-slate-200'}">
                        <span class="relative flex h-2 w-2">
                          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                          <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                        </span>
                        Status
                    </a>
                    <a href="/updates.html" class="text-sm px-4 py-2 rounded-full flex items-center gap-2 transition-colors ${activePage === 'updates' ? 'font-bold text-white bg-indigo-600 shadow-md' : 'font-bold text-slate-600 bg-slate-100 hover:bg-indigo-600 hover:text-white'}">
                        <i class="fas fa-bullhorn text-[10px]"></i> Notice Board
                    </a>
                    <a href="/blog/index.html" class="text-sm px-4 py-2 rounded-full flex items-center gap-2 transition-colors ${activePage === 'blog' ? 'font-bold text-white bg-indigo-600 shadow-md' : 'font-bold text-slate-600 bg-slate-100 hover:bg-indigo-600 hover:text-white'}">
                        <i class="fas fa-feather-alt text-[10px]"></i> Blog
                    </a>
                </div>
                
                <div class="lg:hidden">
                    <a href="/updates.html" aria-label="Notifications" class="w-10 h-10 flex items-center justify-center bg-indigo-50 text-indigo-600 rounded-full border border-indigo-100 shadow-sm">
                       <i class="fas fa-bell"></i>
                    </a>
                </div>
            </div>
        </header>
    `;

    container.innerHTML = navHTML;
    
    const openBtn = document.getElementById('open-menu-btn');
    const closeBtn = document.getElementById('close-menu-btn');
    const menu = document.getElementById('mobile-menu');
    const overlay = document.getElementById('menu-overlay');

    if (!menu || !overlay) return;

    // Use requestAnimationFrame so animations don't stutter or flash on mount
    requestAnimationFrame(() => {
        menu.classList.add('transition-transform', 'duration-300', 'ease-in-out');
        overlay.classList.add('transition-opacity', 'duration-300');
    });

    function setMenuState(isOpen) {
        if (isOpen) {
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
        }
    }

    openBtn?.addEventListener('click', () => setMenuState(true));
    closeBtn?.addEventListener('click', () => setMenuState(false));
    overlay.addEventListener('click', () => setMenuState(false));

    // Close on Escape key for better keyboard navigation
    window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !menu.classList.contains('-translate-x-full')) {
            setMenuState(false);
        }
    });
}

// ----------------------------------------------
// GLOBAL AD INJECTOR STRICTLY FOR NOTE PAGES
// ----------------------------------------------
function injectGlobalAd() {
    // Avoid double injection
    if (document.getElementById('global-note-ad')) return;

    // Strict URL check on pathname only (ignores query params/hashes)
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

    // Pre-decode the image off-thread to avoid frame drop when inserting
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

// Safely execute whether script loads before or after DOMContentLoaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectGlobalAd);
} else {
    injectGlobalAd();
}
