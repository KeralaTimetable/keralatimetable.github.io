// ==============================================================================
// 0. FLOW CORE ENGINE (All 5 Pillars: Memory, Cache, Preloader, Scheduler, Capsule)
// ==============================================================================
window.KTUFlow = (function() {
    const PROFILE_KEY = 'ktu_flow_profile_v2';
    const RECENT_KEY = 'ktu_flow_recent_v2';
    const CATALOG_CACHE_KEY = 'ktu_flow_catalog_cache_v2';
    const FIREBASE_NOTICES_URL = 'https://keralatimetable-5e155-default-rtdb.asia-southeast1.firebasedatabase.app/ktu_notices.json';

    let memoryCatalog = null;
    let prefetchedUrls = new Set();
    let capsuleHideTimeout = null;
    let capsuleExpandTimeout = null;
    let capsuleCollapseTimeout = null;
    let bottomDockActive = false;

    // Ensure #coloros-live-capsule is pre-mounted in DOM at scale(0) so the first
    // Stage-1 dot pop-in transition never gets skipped
    function ensureCapsuleMounted() {
        let capsule = document.getElementById('coloros-live-capsule');
        if (!capsule && document.body) {
            capsule = document.createElement('div');
            capsule.id = 'coloros-live-capsule';
            document.body.appendChild(capsule);
        }
        if (capsule && !capsule.querySelector('#capsule-actions')) {
            capsule.innerHTML = `
                <div id="capsule-inner" class="h-full px-3 flex items-center justify-center gap-2 whitespace-nowrap text-xs font-extrabold text-white overflow-hidden">
                    <span id="capsule-icon" class="flex items-center justify-center shrink-0 z-10"></span>
                    <div id="capsule-text-viewport" class="hidden overflow-hidden flex-1 flex items-center min-w-0">
                        <span id="capsule-text" class="tracking-tight text-white inline-flex items-center whitespace-nowrap"></span>
                    </div>
                    <div id="capsule-actions" class="hidden items-center gap-1.5 shrink-0 pl-1.5 z-10">
                        <a id="capsule-open-btn" href="/updates.html" class="px-2.5 py-1 rounded-full bg-indigo-500 hover:bg-indigo-400 active:scale-95 text-[10px] font-black text-white flex items-center gap-1 shadow-sm transition-all">
                            <span>Open</span>
                            <i class="fas fa-arrow-up-right-from-square text-[8px]"></i>
                        </a>
                        <button type="button" id="capsule-close-btn" aria-label="Dismiss alert" class="w-5 h-5 rounded-full bg-white/15 hover:bg-white/25 text-white/80 hover:text-white flex items-center justify-center text-[10px] transition-colors">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
            `;
        }
        return capsule;
    }

    // Small center circle shown inside the 38px black circle during incoming/outgoing dot stages
    function getDotStageIcon(state) {
        if (state === 'alert' || state === 'error') {
            return '<span class="w-3 h-3 rounded-full bg-rose-500 shadow-[0_0_10px_#f43f5e] animate-pulse"></span>';
        }
        if (state === 'success') {
            return '<span class="w-3 h-3 rounded-full bg-emerald-400 shadow-[0_0_10px_#34d399]"></span>';
        }
        if (state === 'amber') {
            return '<span class="w-3 h-3 rounded-full bg-amber-400 shadow-[0_0_10px_#fbbf24]"></span>';
        }
        return '<span class="w-3 h-3 rounded-full bg-sky-400 shadow-[0_0_10px_#38bdf8] animate-pulse"></span>';
    }

    // Full icon/badge shown only AFTER the black circle starts expanding bilaterally
    function getExpandedStageIcon(state) {
        if (state === 'loading') {
            return '<i class="fas fa-circle-notch fa-spin text-sky-400 text-xs"></i>';
        }
        if (state === 'success') {
            return '<i class="fas fa-check-circle text-emerald-400 text-xs"></i>';
        }
        if (state === 'error') {
            return '<i class="fas fa-exclamation-circle text-rose-400 text-xs"></i>';
        }
        if (state === 'amber') {
            return '<span class="w-2.5 h-2.5 rounded-full bg-amber-400"></span>';
        }
        if (state === 'alert') {
            return '<span class="px-1.5 py-0.5 rounded-full bg-rose-500 text-[9px] font-black uppercase tracking-wider text-white flex items-center gap-1 shadow-sm"><span class="w-1.5 h-1.5 rounded-full bg-white animate-ping"></span>ALERT:</span>';
        }
        return '<span class="w-2.5 h-2.5 rounded-full bg-sky-400 animate-pulse"></span>';
    }

    const engine = {
        ensureCapsuleMounted,

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

        // 4. Predictive Link Preloader & Idle Catalog Warmup
        initPreloader() {
            const prefetchPage = (href) => {
                if (!href || !href.startsWith('/') || prefetchedUrls.has(href) || href === window.location.pathname) return;
                prefetchedUrls.add(href);
                const link = document.createElement('link');
                link.rel = 'prefetch';
                link.href = href;
                document.head.appendChild(link);
            };

            document.addEventListener('mouseover', (e) => {
                const a = e.target.closest('a');
                if (a && a.getAttribute('href')) prefetchPage(a.getAttribute('href'));
            }, { passive: true });

            document.addEventListener('touchstart', (e) => {
                const a = e.target.closest('a');
                if (a && a.getAttribute('href')) prefetchPage(a.getAttribute('href'));
            }, { passive: true });

            const warmUp = () => { this.getCatalog().catch(() => {}); };
            if ('requestIdleCallback' in window) {
                requestIdleCallback(warmUp, { timeout: 2500 });
            } else {
                setTimeout(warmUp, 1500);
            }
        },

        // 5. Smart Frame & Battery Scheduler
        isPaused: false,
        isInputFocused: false,
        initScheduler() {
            document.addEventListener('visibilitychange', () => {
                this.isPaused = document.hidden;
                document.documentElement.classList.toggle('ktu-tab-paused', document.hidden);
            });
            document.addEventListener('focusin', (e) => {
                if (['INPUT', 'SELECT', 'TEXTAREA'].includes(e.target.tagName)) {
                    this.isInputFocused = true;
                }
            });
            document.addEventListener('focusout', () => {
                this.isInputFocused = false;
            });
        },

        // 6. Bottom UI Collision Manager & Interactive ColorOS Dot-to-Sides Capsule
        setBottomDockActive(isActive) {
            bottomDockActive = isActive;
            const waPopup = document.getElementById('ktu-wa-popup');
            if (waPopup) {
                waPopup.style.bottom = isActive ? '5.5rem' : '1.25rem';
            }
        },

        capsule(state = 'idle', message = '', actionUrl = null) {
            const capsule = ensureCapsuleMounted();
            if (!capsule) return;

            const inner = capsule.querySelector('#capsule-inner');
            const iconEl = capsule.querySelector('#capsule-icon');
            const viewportEl = capsule.querySelector('#capsule-text-viewport');
            const textEl = capsule.querySelector('#capsule-text');
            const actionsEl = capsule.querySelector('#capsule-actions');
            const openBtn = capsule.querySelector('#capsule-open-btn');
            const closeBtn = capsule.querySelector('#capsule-close-btn');
            if (!inner || !iconEl || !textEl || !viewportEl) return;

            clearTimeout(capsuleHideTimeout);
            clearTimeout(capsuleExpandTimeout);
            clearTimeout(capsuleCollapseTimeout);

            // STAGE 3 (GOING ANIMATION):
            // Swap badge back to small center circle & hide text, retract both sides into 38px black circle, then scale down
            if (state === 'hide' || state === 'idle') {
                const lastState = capsule.getAttribute('data-last-state') || 'alert';
                capsule.classList.remove('capsule-expanded', 'capsule-paused');
                inner.classList.remove('capsule-shimmer-bg');
                textEl.classList.remove('capsule-marquee-active');
                viewportEl.classList.remove('capsule-viewport-mask');
                viewportEl.classList.add('hidden');
                if (actionsEl) {
                    actionsEl.classList.add('hidden');
                    actionsEl.classList.remove('flex');
                }
                // Show only the small glowing circle inside the shrinking black circle!
                iconEl.innerHTML = getDotStageIcon(lastState);
                capsule.style.pointerEvents = 'none';
                capsule.style.width = '38px';

                // Wait for sides to retract into the 38px circle, hold briefly, then scale down
                capsuleCollapseTimeout = setTimeout(() => {
                    capsule.classList.remove('capsule-dot');
                }, 620);
                return;
            }

            capsule.setAttribute('data-last-state', state);

            // Reset interactive state before new message
            capsule.classList.remove('capsule-paused');
            if (actionsEl) {
                actionsEl.classList.add('hidden');
                actionsEl.classList.remove('flex');
            }
            capsule.onpointerdown = null;
            capsule.onclick = null;

            if (state === 'loading') {
                inner.classList.add('capsule-shimmer-bg');
            } else {
                inner.classList.remove('capsule-shimmer-bg');
            }

            const isAlreadyOpen = capsule.classList.contains('capsule-expanded');

            // Reset marquee before measuring natural single-copy width
            textEl.classList.remove('capsule-marquee-active');
            textEl.style.removeProperty('--marquee-duration');
            viewportEl.classList.remove('capsule-viewport-mask');

            // Measure single-copy width first
            const prevWidth = capsule.style.width;
            iconEl.innerHTML = getExpandedStageIcon(state);
            textEl.textContent = message;
            viewportEl.classList.remove('hidden');
            capsule.style.width = 'auto';

            const maxCapsuleWidth = Math.min(window.innerWidth - 24, 340);
            const singleCopyWidth = textEl.scrollWidth;
            const naturalWidth = Math.max(capsule.scrollWidth + 10, 145);
            const targetWidth = state === 'alert' ? Math.min(naturalWidth, 305) : Math.min(naturalWidth, maxCapsuleWidth);

            const iconWidth = iconEl.offsetWidth || 56;
            const availableTextViewport = targetWidth - iconWidth - 28;
            const overflowPx = singleCopyWidth - availableTextViewport;
            const shouldMarquee = state === 'alert' || overflowPx > 4;

            // Hold duration: 22 seconds (22000ms) for alerts
            let holdDuration = state === 'alert' ? 22000 : 2800;

            if (shouldMarquee) {
                // Build seamless 2-copy track so it scrolls continuously to the left like a TV news ticker
                // without ever bouncing back to the right!
                textEl.innerHTML = '';
                const copy1 = document.createElement('span');
                copy1.className = 'pr-10';
                copy1.textContent = `${message}   •   `;
                const copy2 = document.createElement('span');
                copy2.className = 'pr-10';
                copy2.setAttribute('aria-hidden', 'true');
                copy2.textContent = `${message}   •   `;
                textEl.appendChild(copy1);
                textEl.appendChild(copy2);

                // Consistent news-ticker speed (~55px per second)
                const oneLoopPx = Math.max(singleCopyWidth + 48, 180);
                const loopSeconds = Math.max(5.5, Math.min(oneLoopPx / 52, 14.0));
                textEl.style.setProperty('--marquee-duration', `${loopSeconds.toFixed(2)}s`);
            }

            // Interactive Touch / Click Handler for Alert Capsule:
            // Touching stops the running text, cancels auto-hide, and reveals the "Open" button to redirect to updates.html
            const targetRedirectUrl = actionUrl || (state === 'alert' ? '/updates.html' : null);
            if (targetRedirectUrl) {
                capsule.style.pointerEvents = 'auto';
                capsule.style.cursor = 'pointer';
                if (openBtn) openBtn.href = targetRedirectUrl;

                if (closeBtn) {
                    closeBtn.onclick = (e) => {
                        e.stopPropagation();
                        this.capsule('hide');
                    };
                }

                // First touch/click pauses the running text and shows the "Open" button
                capsule.onclick = (e) => {
                    if (e.target.closest('#capsule-open-btn') || e.target.closest('#capsule-close-btn')) return;

                    if (!capsule.classList.contains('capsule-paused')) {
                        // Stop running effect & cancel auto-hide timer
                        clearTimeout(capsuleHideTimeout);
                        capsule.classList.add('capsule-paused');

                        if (actionsEl) {
                            actionsEl.classList.remove('hidden');
                            actionsEl.classList.add('flex');
                        }

                        // Expand capsule slightly to fit the "Open" button comfortably
                        const pausedMaxWidth = Math.min(window.innerWidth - 20, 415);
                        const newWidth = Math.min(targetWidth + 84, pausedMaxWidth);
                        capsule.style.width = `${newWidth}px`;

                        // Keep open for 15 more seconds after touch if user doesn't click Open
                        capsuleHideTimeout = setTimeout(() => {
                            this.capsule('hide');
                        }, 15000);
                    } else {
                        // If already paused and tapped again, redirect directly to updates.html
                        window.location.href = targetRedirectUrl;
                    }
                };
            } else {
                capsule.style.pointerEvents = 'none';
                capsule.style.cursor = 'default';
            }

            if (!isAlreadyOpen) {
                // STAGE 1 (INCOMING DOT):
                // Hide text and show ONLY the small red circle inside the 38px black circle!
                capsule.style.width = '38px';
                viewportEl.classList.add('hidden');
                iconEl.innerHTML = getDotStageIcon(state);
                void capsule.offsetWidth;
                capsule.classList.add('capsule-dot');

                // Hold as a pure black circle with the small red center circle for 480ms
                // so the incoming dot animation is clearly visible before expanding!
                capsuleExpandTimeout = setTimeout(() => {
                    iconEl.innerHTML = getExpandedStageIcon(state);
                    viewportEl.classList.remove('hidden');
                    if (shouldMarquee) {
                        viewportEl.classList.add('capsule-viewport-mask');
                    }
                    void capsule.offsetWidth;
                    capsule.style.width = `${targetWidth}px`;
                    capsule.classList.add('capsule-expanded');
                    if (shouldMarquee) {
                        textEl.classList.add('capsule-marquee-active');
                    }
                }, 480);
            } else {
                iconEl.innerHTML = getExpandedStageIcon(state);
                viewportEl.classList.remove('hidden');
                if (shouldMarquee) {
                    viewportEl.classList.add('capsule-viewport-mask');
                }
                capsule.style.width = prevWidth;
                void capsule.offsetWidth;
                capsule.style.width = `${targetWidth}px`;
                if (shouldMarquee) {
                    textEl.classList.add('capsule-marquee-active');
                }
            }

            if (state !== 'loading') {
                capsuleHideTimeout = setTimeout(() => {
                    this.capsule('hide');
                }, holdDuration);
            }
        },

        // 7. Global Notification (Routes through the ColorOS Live Capsule)
        toast(message, type = 'info', actionUrl = null) {
            const stateMap = {
                error: 'error',
                amber: 'amber',
                alert: 'alert',
                info: 'info',
                success: 'success'
            };
            this.capsule(stateMap[type] || 'info', message, actionUrl);
        },

        // 8. Global Live Notice Alert (Appears 12s after EVERY page load/reload for ALL users, runs for 22s)
        initNoticeWatcher() {
            if (this._noticeWatcherStarted) return;
            this._noticeWatcherStarted = true;

            const showLatestNoticeAlert = async () => {
                if (this.isInputFocused) {
                    setTimeout(showLatestNoticeAlert, 4000);
                    return;
                }

                try {
                    const res = await fetch(FIREBASE_NOTICES_URL, { cache: 'no-store' });
                    let notices = [];

                    if (res.ok) {
                        const data = await res.json();
                        if (data && typeof data === 'object') {
                            notices = Object.keys(data).map(id => ({ id, ...data[id] }));
                        }
                    }

                    // Fallback to local window.KTU_NOTICES if Firebase is empty
                    if (notices.length === 0 && Array.isArray(window.KTU_NOTICES) && window.KTU_NOTICES.length > 0) {
                        notices = window.KTU_NOTICES.map((n, i) => ({ id: `local-${i}`, ...n }));
                    }

                    if (notices.length === 0) return;

                    // Sort newest first by updatedAt / createdAt / date
                    notices.sort((a, b) => {
                        const tA = new Date(a.updatedAt || a.createdAt || a.date).getTime() || 0;
                        const tB = new Date(b.updatedAt || b.createdAt || b.date).getTime() || 0;
                        return tB - tA;
                    });

                    const latest = notices[0];
                    if (latest && latest.title) {
                        const redirectUrl = `/updates.html?id=${encodeURIComponent(latest.id)}`;
                        this.capsule('alert', latest.title, redirectUrl);
                    }
                } catch (e) {}
            };

            // Appears 12 seconds after every page load / reload for all users
            setTimeout(showLatestNoticeAlert, 12000);
        },

        // 9. Hugging Face Space SSE Connector for Real-Time Pulse & Merge Progress
        initLiveStream(hfSpaceUrl) {
            if (!hfSpaceUrl || this._sseSource || typeof EventSource === 'undefined') return;

            const connect = () => {
                const profile = this.getProfile();
                const params = new URLSearchParams({
                    scheme: profile.scheme || 'ALL',
                    branch: profile.branch || 'ALL',
                    sem: profile.sem || 'ALL'
                });

                const es = new EventSource(`${hfSpaceUrl.replace(/\/$/, '')}/api/capsule/stream?${params.toString()}`);
                this._sseSource = es;

                es.onmessage = (event) => {
                    if (this.isPaused || this.isInputFocused) return;
                    try {
                        const data = JSON.parse(event.data);
                        if (data && data.message) {
                            this.capsule(data.state || 'info', data.message, data.url || null);
                        }
                    } catch (e) {}
                };

                es.onerror = () => {
                    es.close();
                    this._sseSource = null;
                    setTimeout(connect, 25000);
                };
            };

            window.addEventListener('ktu:profile-updated', () => {
                if (this._sseSource) {
                    this._sseSource.close();
                    this._sseSource = null;
                    connect();
                }
            });

            setTimeout(connect, 2000);
        }
    };

    engine.initPreloader();
    engine.initScheduler();
    return engine;
})();

// Expose global helpers matching pyq.html so any page can call triggerCapsule() or showToast() directly
window.triggerCapsule = function(state, message, actionUrl = null) {
    window.KTUFlow.capsule(state, message, actionUrl);
};
window.showToast = function(message, type = 'info') {
    window.KTUFlow.toast(message, type);
};

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
               0. STICKY FROSTED TOP BAR, MOBILE DRAWER & COLOROS LIVE CAPSULE
               ================================================================== */
            #navigation-container {
                position: sticky !important;
                top: 0 !important;
                z-index: 50 !important;
                width: 100%;
            }

            /* See-through Frosted Glass Top Bar */
            header.kt-frosted-header {
                background: rgba(255, 255, 255, 0.56) !important;
                backdrop-filter: blur(24px) saturate(200%) !important;
                -webkit-backdrop-filter: blur(24px) saturate(200%) !important;
                border-bottom: 1px solid rgba(255, 255, 255, 0.75) !important;
                box-shadow: 0 4px 24px -4px rgba(15, 23, 42, 0.05), inset 0 -1px 0 0 rgba(15, 23, 42, 0.06) !important;
            }

            html.dark header.kt-frosted-header {
                background: rgba(7, 11, 20, 0.58) !important;
                backdrop-filter: blur(24px) saturate(200%) !important;
                -webkit-backdrop-filter: blur(24px) saturate(200%) !important;
                border-bottom: 1px solid rgba(255, 255, 255, 0.09) !important;
                box-shadow: 0 4px 28px -4px rgba(0, 0, 0, 0.45), inset 0 -1px 0 0 rgba(255, 255, 255, 0.06) !important;
            }

            /* Mobile Menu: Translucent Frosted Glass + High Contrast Readability */
            #mobile-menu {
                background: linear-gradient(165deg, rgba(255, 255, 255, 0.84) 0%, rgba(248, 250, 252, 0.76) 100%) !important;
                backdrop-filter: blur(32px) saturate(200%) !important;
                -webkit-backdrop-filter: blur(32px) saturate(200%) !important;
                border-right: 1px solid rgba(255, 255, 255, 0.85) !important;
                box-shadow: 20px 0 50px rgba(15, 23, 42, 0.18), inset -1px 0 0 rgba(15, 23, 42, 0.06) !important;
            }
            #mobile-menu .drawer-header {
                background: rgba(255, 255, 255, 0.55) !important;
                border-bottom: 1px solid rgba(15, 23, 42, 0.07) !important;
            }
            #mobile-menu .nav-section-label {
                color: #475569 !important;
                letter-spacing: 0.08em;
            }
            #mobile-menu a.drawer-link-inactive {
                color: #0f172a !important;
                text-shadow: 0 1px 1px rgba(255, 255, 255, 0.75);
            }
            #mobile-menu a.drawer-link-inactive:hover {
                background: rgba(255, 255, 255, 0.65) !important;
                color: #4338ca !important;
            }
            #mobile-menu a.drawer-link-active {
                background: rgba(255, 255, 255, 0.92) !important;
                color: #4338ca !important;
                border: 1px solid rgba(99, 102, 241, 0.25) !important;
                box-shadow: 0 4px 14px -2px rgba(79, 70, 229, 0.12) !important;
            }
            #mobile-menu .drawer-icon-box {
                background: rgba(255, 255, 255, 0.82);
                border: 1px solid rgba(15, 23, 42, 0.08);
                color: #334155;
                box-shadow: 0 2px 5px rgba(15, 23, 42, 0.04);
            }
            #mobile-menu a.drawer-link-active .drawer-icon-box {
                background: #4f46e5;
                border-color: #4f46e5;
                color: #ffffff;
                box-shadow: 0 4px 10px rgba(79, 70, 229, 0.3);
            }

            /* ==================== COLOROS DOT-TO-CAPSULE + NEWS CHANNEL LEFT TICKER ==================== */
            #coloros-live-capsule,
            #ktu-live-capsule {
                position: fixed;
                top: 5.4rem; /* Safe breathing gap below the sticky header */
                left: 50%;
                z-index: 65;
                height: 38px;
                width: 38px;
                border-radius: 9999px;
                transform: translate3d(-50%, -6px, 0) scale(0);
                opacity: 0;
                pointer-events: none;
                overflow: hidden;
                background: rgba(11, 15, 25, 0.95) !important;
                backdrop-filter: blur(28px) saturate(200%) !important;
                -webkit-backdrop-filter: blur(28px) saturate(200%) !important;
                border: 1px solid rgba(255, 255, 255, 0.16) !important;
                color: #ffffff !important;
                box-shadow: 
                    0 18px 40px -8px rgba(0, 0, 0, 0.5),
                    0 4px 14px -2px rgba(37, 99, 235, 0.22),
                    inset 0 1px 0 0 rgba(255, 255, 255, 0.22) !important;
                /* Slower, clearly visible dot pop-in (0.46s) and bilateral width expansion (0.68s) */
                transition: 
                    width 0.68s cubic-bezier(0.16, 1.12, 0.3, 1),
                    transform 0.46s cubic-bezier(0.22, 1.35, 0.36, 1),
                    opacity 0.32s ease;
                will-change: width, transform, opacity;
            }
            #coloros-live-capsule.capsule-dot,
            #ktu-live-capsule.capsule-dot {
                transform: translate3d(-50%, 0, 0) scale(1);
                opacity: 1;
            }
            #capsule-text {
                opacity: 0;
                transition: opacity 0.28s ease 0.14s;
            }
            #coloros-live-capsule.capsule-expanded #capsule-text,
            #ktu-live-capsule.capsule-expanded #capsule-text {
                opacity: 1;
            }

            /* Soft edge fade mask when running text ticker is active */
            .capsule-viewport-mask {
                -webkit-mask-image: linear-gradient(to right, transparent 0%, black 5%, black 93%, transparent 100%);
                mask-image: linear-gradient(to right, transparent 0%, black 5%, black 93%, transparent 100%);
            }

            /* Continuous News-Channel Left Ticker (Never moves back to right!) */
            @keyframes capsuleNewsTickerLeft {
                0% { transform: translate3d(0, 0, 0); }
                100% { transform: translate3d(-50%, 0, 0); }
            }
            #coloros-live-capsule.capsule-expanded #capsule-text.capsule-marquee-active {
                animation: capsuleNewsTickerLeft var(--marquee-duration, 8s) linear 0.45s infinite;
                will-change: transform;
            }
            /* Freeze running text immediately when user touches/clicks the capsule */
            #coloros-live-capsule.capsule-paused #capsule-text.capsule-marquee-active {
                animation-play-state: paused !important;
            }

            @keyframes capsule-shimmer {
                0% { background-position: -200% 0; }
                100% { background-position: 200% 0; }
            }
            .capsule-shimmer-bg {
                background-image: linear-gradient(
                    90deg,
                    transparent 0%,
                    rgba(96, 165, 250, 0.22) 50%,
                    transparent 100%
                );
                background-size: 200% 100%;
                animation: capsule-shimmer 1.8s cubic-bezier(0.4, 0, 0.6, 1) infinite;
            }

            /* Pause background orb animations when browser tab is inactive */
            html.ktu-tab-paused *,
            html.ktu-tab-paused *::before,
            html.ktu-tab-paused *::after {
                animation-play-state: paused !important;
            }

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
               B. DARK MODE ENGINE (Unified across index, notes, pyq & updates)
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

            /* 4. Ambient Parallax Orbs */
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

            /* 6. Inputs & Dropdowns */
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
            html.dark div[class*="bg-white/80"],
            html.dark div[class*="bg-white/60"],
            html.dark .glass-panel.bg-white\\/95 {
                background: rgba(15, 23, 42, 0.72) !important;
                border-color: rgba(255, 255, 255, 0.12) !important;
                box-shadow: inset 0 1px 1px rgba(255,255,255,0.1), 0 12px 36px rgba(0, 0, 0, 0.5) !important;
            }
            html.dark div[class*="focus-within:border-black"]:focus-within,
            html.dark div[class*="focus-within:border-indigo-600"]:focus-within {
                border-color: #368067 !important;
            }

            /* 14. Global Note Ad in Dark Mode */
            html.dark #global-note-ad {
                background-color: rgba(255, 255, 255, 0.03) !important;
                border-color: rgba(255, 255, 255, 0.08) !important;
            }

            /* 15. Dark Mode Mobile Drawer & Theme Toggle Overrides */
            html.dark #mobile-menu {
                background: linear-gradient(165deg, rgba(15, 23, 42, 0.86) 0%, rgba(7, 11, 20, 0.82) 100%) !important;
                border-right: 1px solid rgba(255, 255, 255, 0.12) !important;
                box-shadow: 20px 0 50px rgba(0, 0, 0, 0.65) !important;
            }
            html.dark #mobile-menu .drawer-header {
                background: rgba(7, 11, 20, 0.55) !important;
                border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
            }
            html.dark #mobile-menu .nav-section-label {
                color: #94a3b8 !important;
            }
            html.dark #mobile-menu a.drawer-link-inactive {
                color: #f1f5f9 !important;
                text-shadow: none;
            }
            html.dark #mobile-menu a.drawer-link-inactive:hover {
                background: rgba(255, 255, 255, 0.08) !important;
                color: #ffffff !important;
            }
            html.dark #mobile-menu a.drawer-link-active {
                background: rgba(79, 70, 229, 0.22) !important;
                color: #a5b4fc !important;
                border: 1px solid rgba(99, 102, 241, 0.4) !important;
            }
            html.dark #mobile-menu .drawer-icon-box {
                background: rgba(255, 255, 255, 0.08);
                border-color: rgba(255, 255, 255, 0.1);
                color: #cbd5e1;
            }
            html.dark #mobile-menu a.drawer-link-active .drawer-icon-box {
                background: #4f46e5;
                border-color: #6366f1;
                color: #ffffff;
            }
            html.dark .theme-toggle-btn {
                background-color: rgba(255, 255, 255, 0.08) !important;
                border-color: rgba(255, 255, 255, 0.14) !important;
                color: #f1f5f9 !important;
            }
            html.dark .theme-toggle-btn:hover {
                background-color: rgba(255, 255, 255, 0.16) !important;
            }

            /* 16. UPDATES.HTML Liquid Glass & Dark Mode Overrides */
            html.dark .notice-card {
                background: linear-gradient(135deg, rgba(15, 23, 42, 0.78) 0%, rgba(15, 23, 42, 0.62) 100%) !important;
                border: 1px solid rgba(255, 255, 255, 0.09) !important;
                border-top: 1px solid rgba(255, 255, 255, 0.18) !important;
                box-shadow: 0 12px 30px -4px rgba(0, 0, 0, 0.45) !important;
            }
            html.dark .notice-card:hover {
                background: linear-gradient(135deg, rgba(30, 41, 59, 0.88) 0%, rgba(15, 23, 42, 0.82) 100%) !important;
                border-color: rgba(99, 102, 241, 0.5) !important;
                box-shadow: 0 18px 38px -6px rgba(0, 0, 0, 0.65), 0 0 20px -4px rgba(99, 102, 241, 0.2) !important;
            }
            html.dark .filter-btn:not(.active) {
                background: rgba(15, 23, 42, 0.65) !important;
                border-color: rgba(255, 255, 255, 0.1) !important;
                color: #cbd5e1 !important;
            }
            html.dark .filter-btn:not(.active):hover {
                background: rgba(30, 41, 59, 0.85) !important;
                border-color: rgba(99, 102, 241, 0.4) !important;
                color: #ffffff !important;
            }
            html.dark #notice-modal-content,
            html.dark #editorModal > div {
                background: rgba(15, 23, 42, 0.92) !important;
                border: 1px solid rgba(255, 255, 255, 0.15) !important;
                box-shadow: 0 25px 60px -10px rgba(0, 0, 0, 0.75) !important;
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
// 3. RESPONSIVE NAVIGATION LOADER (Exact Branding Lockup + High-Contrast Glass Drawer)
// ==============================================================================
function loadNavigation(activePage, basePath = '', isBlog = false) { 
    const container = document.getElementById('navigation-container');
    if (!container) return;

    if (window.KTUFlow && typeof window.KTUFlow.ensureCapsuleMounted === 'function') {
        window.KTUFlow.ensureCapsuleMounted();
    }

    container.classList.remove('relative');
    container.classList.add('sticky', 'top-0', 'z-50', 'w-full');

    const logoExtension = isBlog ? ' <span class="text-slate-400 font-medium ml-1">| Blog</span>' : '';

    const navItemClass = (key) => activePage === key
        ? 'drawer-link-active font-extrabold'
        : 'drawer-link-inactive font-bold border border-transparent';

    const navHTML = `
        <!-- High-Contrast See-Through Frosted Glass Mobile Drawer -->
        <div id="mobile-menu" aria-hidden="true" style="visibility: hidden;" 
             class="fixed inset-y-0 left-0 w-72 transform -translate-x-full z-[60] flex flex-col will-change-transform">
            
            <div class="drawer-header p-5 flex justify-between items-center">
                <div class="flex items-center gap-2">
                    <img src="/k.png" alt="Kerala Timetable Logo" class="w-6 h-6 object-contain shrink-0" width="24" height="24" />
                    <span class="text-base font-extrabold text-slate-900 tracking-tight leading-none">Kerala <span class="text-indigo-600">Timetable</span></span>
                </div>
                <button id="close-menu-btn" aria-label="Close menu" class="w-8 h-8 flex items-center justify-center text-slate-600 dark:text-slate-300 hover:text-rose-500 transition-all rounded-full bg-white/70 dark:bg-white/10 shadow-sm active:scale-95 focus:outline-none">
                    <i class="fas fa-times text-base"></i>
                </button>
            </div>
            
            <nav class="flex-grow py-4 px-3.5 flex flex-col gap-1.5 overflow-y-auto">
                <p class="nav-section-label px-3 pt-1 pb-1 text-[10px] font-extrabold uppercase">Academics</p>
                
                <a href="/index.html" class="flex items-center gap-3 px-3 py-2.5 rounded-2xl text-[15px] transition-all active:scale-[0.98] ${navItemClass('home')}">
                    <span class="drawer-icon-box w-8 h-8 rounded-xl flex items-center justify-center shrink-0">
                        <i class="fas fa-home text-xs"></i>
                    </span>
                    <span>Home</span>
                </a>
                
                <a href="/timetable.html" class="flex items-center gap-3 px-3 py-2.5 rounded-2xl text-[15px] transition-all active:scale-[0.98] ${navItemClass('timetable')}">
                    <span class="drawer-icon-box w-8 h-8 rounded-xl flex items-center justify-center shrink-0">
                        <i class="fas fa-calendar-day text-xs"></i>
                    </span>
                    <span>Timetables</span>
                </a>
                
                <a href="/notes.html" class="flex items-center gap-3 px-3 py-2.5 rounded-2xl text-[15px] transition-all active:scale-[0.98] ${navItemClass('notes')}">
                    <span class="drawer-icon-box w-8 h-8 rounded-xl flex items-center justify-center shrink-0">
                        <i class="fas fa-book-open text-xs"></i>
                    </span>
                    <span>Study Notes</span>
                </a>

                <a href="/pyq.html" class="flex items-center gap-3 px-3 py-2.5 rounded-2xl text-[15px] transition-all active:scale-[0.98] ${navItemClass('pyq')}">
                    <span class="drawer-icon-box w-8 h-8 rounded-xl flex items-center justify-center shrink-0">
                        <i class="fas fa-file-alt text-xs"></i>
                    </span>
                    <span>Previous Papers</span>
                </a>

                <p class="nav-section-label px-3 pt-4 pb-1 text-[10px] font-extrabold uppercase">Community & Updates</p>

                <a href="/doubts.html" class="flex items-center gap-3 px-3 py-2.5 rounded-2xl text-[15px] transition-all active:scale-[0.98] ${navItemClass('qa')}">
                    <span class="drawer-icon-box w-8 h-8 rounded-xl flex items-center justify-center shrink-0">
                        <i class="fas fa-comments text-xs"></i>
                    </span>
                    <span>Q&A Hub</span>
                </a>
                
                <a href="/updates.html" class="flex items-center gap-3 px-3 py-2.5 rounded-2xl text-[15px] transition-all active:scale-[0.98] ${navItemClass('updates')}">
                    <span class="drawer-icon-box w-8 h-8 rounded-xl flex items-center justify-center shrink-0">
                        <i class="fas fa-bullhorn text-xs"></i>
                    </span>
                    <span>Latest Updates</span>
                </a>
                
                <a href="/blog/index.html" class="flex items-center gap-3 px-3 py-2.5 rounded-2xl text-[15px] transition-all active:scale-[0.98] ${navItemClass('blog')}">
                    <span class="drawer-icon-box w-8 h-8 rounded-xl flex items-center justify-center shrink-0">
                        <i class="fas fa-feather-alt text-xs"></i>
                    </span>
                    <span>Blog</span>
                </a>

                <a href="/status.html" class="flex items-center gap-3 px-3 py-2.5 rounded-2xl text-[15px] transition-all active:scale-[0.98] ${navItemClass('status')}">
                    <span class="drawer-icon-box w-8 h-8 rounded-xl flex items-center justify-center shrink-0">
                        <i class="fas fa-server text-xs"></i>
                    </span>
                    <span>Server Status</span>
                </a>

                <a href="/about.html" class="flex items-center gap-3 px-3 py-2.5 rounded-2xl text-[15px] transition-all active:scale-[0.98] ${navItemClass('about')}">
                    <span class="drawer-icon-box w-8 h-8 rounded-xl flex items-center justify-center shrink-0">
                        <i class="fas fa-info-circle text-xs"></i>
                    </span>
                    <span>About</span>
                </a>
            </nav>
        </div>

        <div id="menu-overlay" style="visibility: hidden;" class="fixed inset-0 bg-slate-900/35 backdrop-blur-[2px] z-50 opacity-0 pointer-events-none will-change-[opacity]"></div>

        <!-- EXACT BRAND HEADER (Font, Size, Alignment Locked 1:1 + Sticky Frosted Glass) -->
        <header class="kt-frosted-header w-full z-40 transition-all duration-300">
            <div class="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex justify-between items-center">
                <div class="flex items-center gap-3">
                    <button id="open-menu-btn" aria-label="Open menu" class="p-2 -ml-2 text-slate-600 hover:text-indigo-600 hover:bg-white/60 dark:hover:bg-white/10 rounded-lg transition-colors focus:outline-none lg:hidden">
                        <i class="fas fa-bars text-xl"></i>
                    </button>
                    <a href="/index.html" class="flex items-center gap-2 hover:opacity-80 transition-opacity">
                        <img src="/k.png" alt="Kerala Timetable Logo" class="w-6 h-6 sm:w-7 sm:h-7 object-contain shrink-0" width="28" height="28" />
                        <h1 class="text-xl sm:text-2xl font-extrabold tracking-tight text-slate-900 leading-none">Kerala <span class="text-indigo-600">Timetable</span>${logoExtension}</h1>
                    </a>
                </div>

                <div class="hidden lg:flex gap-2 items-center">
                    <a href="/notes.html" class="text-sm px-4 py-2 rounded-full flex items-center gap-2 transition-all active:scale-95 ${activePage === 'notes' ? 'font-bold text-indigo-700 bg-indigo-50/85 border border-indigo-100 shadow-sm' : 'font-bold text-slate-600 hover:text-indigo-600 hover:bg-white/60 dark:hover:bg-white/10'}">
                        <i class="fas fa-book-open text-[10px]"></i> Study Notes
                    </a>
                    
                    <a href="/pyq.html" class="text-sm px-4 py-2 rounded-full flex items-center gap-2 transition-all active:scale-95 ${activePage === 'pyq' ? 'font-bold text-indigo-700 bg-indigo-50/85 border border-indigo-100 shadow-sm' : 'font-bold text-slate-600 hover:text-indigo-600 hover:bg-white/60 dark:hover:bg-white/10'}">
                        <i class="fas fa-file-alt text-[10px]"></i> PYQs
                    </a>

                    <a href="/doubts.html" class="text-sm px-4 py-2 rounded-full flex items-center gap-2 transition-all active:scale-95 ${activePage === 'qa' ? 'font-bold text-indigo-700 bg-indigo-50/85 border border-indigo-100 shadow-sm' : 'font-bold text-slate-600 hover:text-indigo-600 hover:bg-white/60 dark:hover:bg-white/10'}">
                        <i class="fas fa-comments text-[10px]"></i> Q&A
                    </a>
                    
                    <div class="w-px h-5 bg-slate-200 dark:bg-white/10 mx-1"></div>
                    
                    <a href="/updates.html" class="text-sm px-4 py-2 rounded-full flex items-center gap-2 transition-all active:scale-95 ${activePage === 'updates' ? 'font-bold text-white bg-indigo-600 shadow-md' : 'font-bold text-slate-600 bg-white/70 dark:bg-white/10 hover:bg-indigo-600 hover:text-white'}">
                        <i class="fas fa-bullhorn text-[10px]"></i> Notice Board
                    </a>

                    <!-- Desktop Theme Toggle -->
                    <button class="theme-toggle-btn w-9 h-9 ml-1 rounded-full flex items-center justify-center bg-slate-100/85 text-slate-600 hover:bg-slate-200 border border-slate-200 transition-all active:scale-95 shadow-inner focus:outline-none" aria-label="Toggle Theme">
                        <i class="fas fa-moon text-[13px]"></i>
                    </button>
                </div>
                
                <div class="lg:hidden flex items-center gap-2">
                    <!-- Mobile Theme Toggle -->
                    <button class="theme-toggle-btn w-10 h-10 flex items-center justify-center bg-slate-100/85 text-slate-600 rounded-full border border-slate-200 shadow-sm transition-all active:scale-95 focus:outline-none" aria-label="Toggle Theme">
                        <i class="fas fa-moon text-[14px]"></i>
                    </button>
                    <a href="/updates.html" aria-label="Notifications" class="w-10 h-10 flex items-center justify-center bg-indigo-50/85 dark:bg-indigo-500/15 text-indigo-600 dark:text-indigo-400 rounded-full border border-indigo-100 dark:border-indigo-400/25 shadow-sm transition-all active:scale-95">
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
            window.KTUFlow.capsule(isDark ? 'success' : 'amber', isDark ? 'Dark Theme enabled' : 'Light Theme enabled');
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
    if (window.KTUFlow && typeof window.KTUFlow.ensureCapsuleMounted === 'function') {
        window.KTUFlow.ensureCapsuleMounted();
    }
    if (window.KTUFlow && typeof window.KTUFlow.initNoticeWatcher === 'function') {
        window.KTUFlow.initNoticeWatcher();
    }
    injectGlobalAd();
    initWhatsAppPopup();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', runInitializers);
} else {
    runInitializers();
}
