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

        setBottomDockActive(isActive) {
            bottomDockActive = isActive;
            const waPopup = document.getElementById('ktu-wa-popup');
            if (waPopup) {
                waPopup.style.bottom = isActive ? '5.5rem' : '1.25rem';
            }
            if (isActive && window.KTULiquidGlass && typeof window.KTULiquidGlass.refreshDocks === 'function') {
                window.KTULiquidGlass.refreshDocks();
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
                iconEl.innerHTML = getDotStageIcon(lastState);
                capsule.style.pointerEvents = 'none';
                capsule.style.width = '38px';

                capsuleCollapseTimeout = setTimeout(() => {
                    capsule.classList.remove('capsule-dot');
                }, 620);
                return;
            }

            capsule.setAttribute('data-last-state', state);
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

            textEl.classList.remove('capsule-marquee-active');
            textEl.style.removeProperty('--marquee-duration');
            viewportEl.classList.remove('capsule-viewport-mask');

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

            let holdDuration = state === 'alert' ? 22000 : 2800;

            if (shouldMarquee) {
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

                const oneLoopPx = Math.max(singleCopyWidth + 48, 180);
                const loopSeconds = Math.max(5.5, Math.min(oneLoopPx / 52, 14.0));
                textEl.style.setProperty('--marquee-duration', `${loopSeconds.toFixed(2)}s`);
            }

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

                capsule.onclick = (e) => {
                    if (e.target.closest('#capsule-open-btn') || e.target.closest('#capsule-close-btn')) return;

                    if (!capsule.classList.contains('capsule-paused')) {
                        clearTimeout(capsuleHideTimeout);
                        capsule.classList.add('capsule-paused');

                        if (actionsEl) {
                            actionsEl.classList.remove('hidden');
                            actionsEl.classList.add('flex');
                        }

                        const pausedMaxWidth = Math.min(window.innerWidth - 20, 415);
                        const newWidth = Math.min(targetWidth + 84, pausedMaxWidth);
                        capsule.style.width = `${newWidth}px`;

                        capsuleHideTimeout = setTimeout(() => {
                            this.capsule('hide');
                        }, 15000);
                    } else {
                        window.location.href = targetRedirectUrl;
                    }
                };
            } else {
                capsule.style.pointerEvents = 'none';
                capsule.style.cursor = 'default';
            }

            if (!isAlreadyOpen) {
                capsule.style.width = '38px';
                viewportEl.classList.add('hidden');
                iconEl.innerHTML = getDotStageIcon(state);
                void capsule.offsetWidth;
                capsule.classList.add('capsule-dot');

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

                    if (notices.length === 0 && Array.isArray(window.KTU_NOTICES) && window.KTU_NOTICES.length > 0) {
                        notices = window.KTU_NOTICES.map((n, i) => ({ id: `local-${i}`, ...n }));
                    }

                    if (notices.length === 0) return;

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

            setTimeout(showLatestNoticeAlert, 12000);
        }
    };

    engine.initPreloader();
    engine.initScheduler();
    return engine;
})();

window.triggerCapsule = function(state, message, actionUrl = null) {
    window.KTUFlow.capsule(state, message, actionUrl);
};
window.showToast = function(message, type = 'info') {
    window.KTUFlow.toast(message, type);
};

// ==============================================================================
// 1. OPENBLAST EXACT LIQUID GLASS ENGINE (Gy + $y + tb ResizeObserver Port)
//    - Exact Circular Cross-Section Profile: g = 1 - Math.sqrt(1 - h*h)
//    - Exact 1:1 Pixel-Matched userSpaceOnUse SVG Filter per Pill/Dock
// ==============================================================================
window.KTULiquidGlass = (function() {
    const SVG_NS = 'http://www.w3.org/2000/svg';
    let svgRoot = null;
    const filterCache = new Map();
    const observedElements = new WeakMap();
    const dockUpdaters = new Set();
    let filterCounter = 0;

    function isChromiumEngine() {
        if (navigator.userAgentData?.brands?.some(b => b.brand === 'Chromium' || b.brand === 'Google Chrome' || b.brand === 'Microsoft Edge')) {
            return true;
        }
        const ua = navigator.userAgent || '';
        return /Chrome|CriOS|Edg|OPR|Brave/i.test(ua) && !/Firefox|FxiOS/i.test(ua);
    }

    // OpenBlast's exact Gy(width, height, radius, bevel) Circular Lens Normal Map Generator
    function generateNormalMapBytes(e, t, n, r) {
        const i = new Uint8ClampedArray(e * t * 4);
        const a = e / 2;
        const o = t / 2;
        const s = Math.max(0, Math.min(n, a, o));
        const c = Math.max(1, Math.min(r, a, o));

        for (let y = 0; y < t; y++) {
            for (let x = 0; x < e; x++) {
                const rDx = x + 0.5 - a;
                const lDy = y + 0.5 - o;
                const u = Math.abs(rDx) - (a - s);
                const d = Math.abs(lDy) - (o - s);
                let f, p = 0, m = 0;

                if (u > 0 && d > 0) {
                    const dist = Math.hypot(u, d);
                    f = s - dist;
                    p = (u / dist) * Math.sign(rDx);
                    m = (d / dist) * Math.sign(lDy);
                } else if (u > d) {
                    f = s - u;
                    p = Math.sign(rDx);
                } else {
                    f = s - d;
                    m = Math.sign(lDy);
                }

                const h = Math.min(1, Math.max(0, 1 - f / c));
                // Exact circular meniscus equation from OpenBlast:
                const g = 1 - Math.sqrt(1 - h * h);
                const idx = (y * e + x) * 4;
                i[idx]     = Math.round(128 - p * g * 127);
                i[idx + 1] = Math.round(128 - m * g * 127);
                i[idx + 2] = 128;
                i[idx + 3] = 255;
            }
        }
        return i;
    }

    function ensureSvgRoot() {
        if (svgRoot?.isConnected) return svgRoot;
        svgRoot = document.createElementNS(SVG_NS, 'svg');
        svgRoot.setAttribute('width', '0');
        svgRoot.setAttribute('height', '0');
        svgRoot.setAttribute('aria-hidden', 'true');
        svgRoot.style.position = 'absolute';
        svgRoot.style.pointerEvents = 'none';
        svgRoot.style.zIndex = '-9999';
        document.body.append(svgRoot);
        return svgRoot;
    }

    function createNormalMapDataURL(w, h, r, bevel) {
        const canvas = document.createElement('canvas');
        canvas.width = w;
        canvas.height = h;
        const ctx = canvas.getContext('2d');
        if (!ctx) return '';
        ctx.putImageData(new ImageData(generateNormalMapBytes(w, h, r, bevel), w, h), 0, 0);
        return canvas.toDataURL();
    }

    function createSvgNode(tag, attrs) {
        const el = document.createElementNS(SVG_NS, tag);
        for (const [k, v] of Object.entries(attrs)) {
            el.setAttribute(k, String(v));
        }
        return el;
    }

    function acquireLiquidFilter(w, h, radius, bevel, depth) {
        const key = `${w}x${h}r${radius}b${bevel}d${depth}`;
        const existing = filterCache.get(key);
        if (existing) {
            existing.users++;
            return key;
        }

        const id = `ot-liquid-${filterCounter++}`;
        const box = { x: 0, y: 0, width: w, height: h };
        const filterNode = createSvgNode('filter', {
            id,
            ...box,
            filterUnits: 'userSpaceOnUse',
            primitiveUnits: 'userSpaceOnUse',
            'color-interpolation-filters': 'sRGB'
        });

        const feImg = createSvgNode('feImage', {
            ...box,
            result: 'map',
            preserveAspectRatio: 'none'
        });
        feImg.setAttribute('href', createNormalMapDataURL(w, h, radius, bevel));
        filterNode.append(feImg);

        filterNode.append(
            createSvgNode('feDisplacementMap', {
                in: 'SourceGraphic',
                in2: 'map',
                scale: depth * 2,
                xChannelSelector: 'R',
                yChannelSelector: 'G'
            })
        );

        ensureSvgRoot().append(filterNode);
        filterCache.set(key, { id, node: filterNode, users: 1 });
        return key;
    }

    function releaseLiquidFilter(key) {
        const entry = filterCache.get(key);
        if (!entry) return;
        if (--entry.users <= 0) {
            entry.node.remove();
            filterCache.delete(key);
        }
    }

    function attachLiquidPill(el, bevel = 22, depth = 22) {
        if (!el || observedElements.has(el)) return;
        el.classList.add('glass-pill');

        if (!isChromiumEngine()) return;

        let activeKey = null;
        const updateLens = () => {
            const w = Math.round(el.offsetWidth);
            const h = Math.round(el.offsetHeight);
            if (!w || !h || w > 1400 || h > 260) return;

            const rawRadius = Number.parseFloat(getComputedStyle(el).borderTopLeftRadius) || 22;
            const r = Math.round(Math.min(rawRadius, w / 2, h / 2));
            const nextKey = acquireLiquidFilter(w, h, r, bevel, depth);
            if (activeKey && activeKey !== nextKey) releaseLiquidFilter(activeKey);
            activeKey = nextKey;

            const filterEntry = filterCache.get(nextKey);
            if (filterEntry) {
                el.style.setProperty('--liquid-filter', `url(#${filterEntry.id})`);
                el.dataset.liquid = '';
            }
        };

        updateLens();
        const ro = new ResizeObserver(updateLens);
        ro.observe(el);

        // For bottom popup docks that start hidden (opacity: 0, scale(0.92)),
        // watch class changes (.dock-active) so Chromium re-binds the backdrop-filter texture!
        if (el.id === 'floating-merge-dock' || el.id === 'floating-points-dock') {
            dockUpdaters.add(updateLens);
            const mo = new MutationObserver(() => {
                if (el.classList.contains('dock-active')) {
                    requestAnimationFrame(updateLens);
                    setTimeout(updateLens, 120);
                }
            });
            mo.observe(el, { attributes: true, attributeFilter: ['class'] });
        }

        observedElements.set(el, { ro, getKey: () => activeKey });
    }

    function refreshDocks() {
        dockUpdaters.forEach(fn => {
            requestAnimationFrame(fn);
            setTimeout(fn, 120);
        });
    }

    function scanAndAttachAllPills() {
        if (!document.body) return;

        // 1. Primary Floating Docks & Search Pill (bevel = 18, depth = 20 — exact match with Top Header!)
        const dockSelectors = [
            '#floating-merge-dock',
            '#floating-points-dock',
            '#search-wrapper > div',
            '#ktu-wa-popup'
        ];
        dockSelectors.forEach(sel => {
            document.querySelectorAll(sel).forEach(el => attachLiquidPill(el, 18, 20));
        });

        // 2. Sticky Top Header (Slightly rounded rectangular bar: bevel = 18, depth = 20)
        document.querySelectorAll('header.kt-frosted-header').forEach(el => attachLiquidPill(el, 18, 20));

        // 3. Segmented Tab Switchers & Pill Controls (bevel = 16, depth = 18)
        const pillSelectors = [
            '#search-card > div.grid.grid-cols-2',
            '#scheme-filters',
            '#group-detail-view > div.inner-glass.sticky'
        ];
        pillSelectors.forEach(sel => {
            document.querySelectorAll(sel).forEach(el => attachLiquidPill(el, 16, 18));
        });
    }

    return {
        attachLiquidPill,
        scanAndAttachAllPills,
        refreshDocks
    };
})();

// ==============================================================================
// 2. OPENBLAST LIQUID GLASS CSS + 120FPS DARK MODE ENGINE
// ==============================================================================
(function initTheme() {
    const savedTheme = localStorage.getItem('kt_theme') || 'light';
    if (savedTheme === 'dark') {
        document.documentElement.classList.add('dark');
    } else {
        document.documentElement.classList.remove('dark');
    }

    function mountDarkStyles() {
        let style = document.getElementById('kt-dark-theme-styles');
        if (!style) {
            style = document.createElement('style');
            style.id = 'kt-dark-theme-styles';
        }
        style.innerHTML = `
            /* ==================================================================
               0. OPENBLAST EXACT .glass-pill[data-liquid] ARCHITECTURE
               ================================================================== */
            :root {
                --glassMaterialBackground: rgba(248, 250, 252, 0.62);
                --glassMaterialShadowColor: rgba(15, 23, 42, 0.10);
                --glassMaterialInnerStroke: #fff;
                --glassMaterialInnerStrokeAlpha: 0.5;
            }
            html.dark {
                --glassMaterialBackground: rgba(24, 30, 46, 0.68);
                --glassMaterialShadowColor: rgba(0, 0, 0, 0.55);
                --glassMaterialInnerStroke: #fff;
                --glassMaterialInnerStrokeAlpha: 0.24;
            }

            .glass-pill {
                isolation: isolate;
                position: relative;
            }
            /* Preserve fixed/sticky positioning on docks & headers */
            #floating-merge-dock.glass-pill,
            #floating-points-dock.glass-pill,
            #ktu-wa-popup.glass-pill {
                position: fixed !important;
            }
            #group-detail-view > div.inner-glass.sticky.glass-pill {
                position: sticky !important;
            }

            .glass-pill::before,
            .glass-pill::after {
                content: "";
                border-radius: inherit;
                pointer-events: none;
                position: absolute;
                inset: 0;
            }

            /* Fallback when [data-liquid] is not active (e.g., iOS Safari) */
            .glass-pill::before {
                z-index: -1;
                background-color: var(--glassMaterialBackground);
                -webkit-backdrop-filter: saturate(1.85) blur(22px);
                backdrop-filter: saturate(1.85) blur(22px);
                box-shadow: 0 12px 36px var(--glassMaterialShadowColor);
                background-image: linear-gradient(180deg, rgba(255, 255, 255, 0.32) 0%, rgba(255, 255, 255, 0) 55%);
            }
            .glass-pill::after {
                z-index: 2;
                box-shadow:
                    inset 1.5px 1.5px 0 -0.5px #fffffff2,
                    inset -1.5px -1.5px 0 -0.5px #fff9,
                    inset 0 0 0 0.5px #00000014,
                    inset 0 0 14px #fff3;
            }
            html.dark .glass-pill::after {
                box-shadow:
                    inset 1.5px 1.5px 0 -0.5px #fff9,
                    inset -1.5px -1.5px 0 -0.5px #ffffff4d,
                    inset 0 0 14px #ffffff12;
            }

            /* OPENBLAST EXACT LIQUID FILTER RULE (Used by Top Bar — Untouched 100%!) */
            .glass-pill[data-liquid] {
                background: transparent !important;
                backdrop-filter: none !important;
                -webkit-backdrop-filter: none !important;
                border-color: transparent !important;
            }
            .glass-pill[data-liquid]::before {
                z-index: -1;
                -webkit-backdrop-filter: var(--liquid-filter) blur(5px) saturate(1.8) brightness(1.04) !important;
                backdrop-filter: var(--liquid-filter) blur(5px) saturate(1.8) brightness(1.04) !important;
                background-color: rgba(255, 255, 255, 0.36) !important;
                background-image: linear-gradient(180deg, rgba(255, 255, 255, 0.28) 0%, rgba(255, 255, 255, 0) 48%) !important;
                box-shadow: 0 12px 36px var(--glassMaterialShadowColor) !important;
            }
            html.dark .glass-pill[data-liquid]::before {
                background-color: rgba(15, 23, 42, 0.48) !important;
                background-image: linear-gradient(180deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0) 48%) !important;
            }
            .glass-pill[data-liquid]::after {
                content: "";
                border-radius: inherit;
                pointer-events: none;
                opacity: 1;
                position: absolute;
                inset: 0;
                z-index: 2;
                box-shadow:
                    inset 1.5px 1.5px 0 -0.5px #fffffff2,
                    inset -1.5px -1.5px 0 -0.5px #fff9,
                    inset 0 0 0 0.5px #00000014,
                    inset 0 0 14px #fff3 !important;
            }
            html.dark .glass-pill[data-liquid]::after {
                box-shadow:
                    inset 1.5px 1.5px 0 -0.5px #fff9,
                    inset -1.5px -1.5px 0 -0.5px #ffffff4d,
                    inset 0 0 14px #ffffff12 !important;
            }

            /* ==================================================================
               FIX FOR BOTTOM POPUP DOCKS (#floating-merge-dock & #floating-points-dock):
               Chromium drops ::before backdrop-filter on elements that transition
               from opacity:0 + offscreen translate3d() with will-change:transform,opacity.
               Applying the exact Top Bar backdrop-filter & specular rim DIRECTLY onto the
               dock element guarantees 100% identical blur + refraction physics!
               ================================================================== */
            #floating-merge-dock,
            #floating-points-dock,
            #floating-merge-dock.glass-pill[data-liquid],
            #floating-points-dock.glass-pill[data-liquid] {
                will-change: auto !important;
                isolation: auto !important;
                border-radius: 22px !important;
                border: none !important;
                background-color: rgba(255, 255, 255, 0.36) !important;
                background-image: linear-gradient(180deg, rgba(255, 255, 255, 0.28) 0%, rgba(255, 255, 255, 0) 48%) !important;
                -webkit-backdrop-filter: var(--liquid-filter, ) blur(5px) saturate(1.8) brightness(1.04) !important;
                backdrop-filter: var(--liquid-filter, ) blur(5px) saturate(1.8) brightness(1.04) !important;
                box-shadow:
                    inset 1.5px 1.5px 0 -0.5px #fffffff2,
                    inset -1.5px -1.5px 0 -0.5px #fff9,
                    inset 0 0 0 0.5px #00000014,
                    inset 0 0 14px #fff3,
                    0 14px 40px rgba(15, 23, 42, 0.16) !important;
            }
            #floating-merge-dock::before,
            #floating-points-dock::before,
            #floating-merge-dock.glass-pill[data-liquid]::before,
            #floating-points-dock.glass-pill[data-liquid]::before {
                display: none !important;
            }
            html.dark #floating-merge-dock,
            html.dark #floating-points-dock,
            html.dark #floating-merge-dock.glass-pill[data-liquid],
            html.dark #floating-points-dock.glass-pill[data-liquid] {
                background-color: rgba(15, 23, 42, 0.48) !important;
                background-image: linear-gradient(180deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0) 48%) !important;
                box-shadow:
                    inset 1.5px 1.5px 0 -0.5px #fff9,
                    inset -1.5px -1.5px 0 -0.5px #ffffff4d,
                    inset 0 0 14px #ffffff12,
                    0 20px 44px rgba(0, 0, 0, 0.65) !important;
            }

            /* ==================================================================
               1. SLEEK SINGLE-LINE ROUNDED RECTANGULAR LIQUID GLASS TOP HEADER
               ================================================================== */
            /* Never apply transform or will-change on #navigation-container */
            #navigation-container {
                position: sticky !important;
                top: 0 !important;
                z-index: 50 !important;
                width: 100%;
                padding: 6px 8px 0 8px !important;
                background: transparent !important;
            }
            @media (min-width: 640px) {
                #navigation-container {
                    padding: 8px 16px 0 16px !important;
                }
            }

            header.kt-frosted-header {
                max-width: 72rem !important;
                margin-left: auto !important;
                margin-right: auto !important;
                border-radius: 18px !important;
                border: none !important;
            }
            @media (min-width: 640px) {
                header.kt-frosted-header {
                    border-radius: 22px !important;
                }
            }

            /* Full-Screen Mobile Drawer (Mounted on document.body) */
            #mobile-menu {
                position: fixed !important;
                top: 0 !important;
                bottom: 0 !important;
                left: 0 !important;
                height: 100vh !important;
                height: 100dvh !important;
                max-height: 100dvh !important;
                background: rgba(255, 255, 255, 0.78) !important;
                backdrop-filter: saturate(190%) blur(32px) !important;
                -webkit-backdrop-filter: saturate(190%) blur(32px) !important;
                border-right: 1px solid rgba(255, 255, 255, 0.85) !important;
                box-shadow:
                    inset -1.5px 0 0 -0.5px #fffffff2,
                    20px 0 50px rgba(15, 23, 42, 0.18) !important;
            }
            #menu-overlay {
                position: fixed !important;
                inset: 0 !important;
                width: 100vw !important;
                height: 100vh !important;
                height: 100dvh !important;
            }
            #mobile-menu .drawer-header {
                background: rgba(255, 255, 255, 0.45) !important;
                border-bottom: 1px solid rgba(15, 23, 42, 0.07) !important;
            }
            #mobile-menu .nav-section-label { color: #475569 !important; letter-spacing: 0.08em; }
            #mobile-menu a.drawer-link-inactive { color: #0f172a !important; }
            #mobile-menu a.drawer-link-inactive:hover { background: rgba(255, 255, 255, 0.65) !important; color: #4338ca !important; }
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
            }
            #mobile-menu a.drawer-link-active .drawer-icon-box {
                background: #4f46e5;
                border-color: #4f46e5;
                color: #ffffff;
            }

            /* ==================== FLUID MOBILE MENU TEXT & ICON ENTRY ANIMATIONS ==================== */
            #mobile-menu .drawer-brand-wrap {
                opacity: 0;
                transform: translate3d(-12px, 0, 0);
                transition:
                    opacity 0.36s cubic-bezier(0.22, 1, 0.36, 1) 0.04s,
                    transform 0.48s cubic-bezier(0.22, 1.15, 0.36, 1) 0.04s;
                will-change: transform, opacity;
            }
            #mobile-menu.drawer-is-open .drawer-brand-wrap {
                opacity: 1;
                transform: translate3d(0, 0, 0);
            }

            #mobile-menu .drawer-anim-item {
                opacity: 0;
                transform: translate3d(-18px, 6px, 0) scale(0.96);
                transition:
                    opacity 0.2s ease,
                    transform 0.24s ease,
                    background-color 0.2s ease,
                    color 0.2s ease,
                    border-color 0.2s ease,
                    box-shadow 0.2s ease;
                will-change: transform, opacity;
            }
            #mobile-menu.drawer-is-open .drawer-anim-item {
                opacity: 1;
                transform: translate3d(0, 0, 0) scale(1);
                transition:
                    opacity 0.42s cubic-bezier(0.22, 1, 0.36, 1) calc(var(--stagger, 0) * 32ms + 65ms),
                    transform 0.54s cubic-bezier(0.22, 1.15, 0.36, 1) calc(var(--stagger, 0) * 32ms + 65ms),
                    background-color 0.2s ease,
                    color 0.2s ease,
                    border-color 0.2s ease,
                    box-shadow 0.2s ease;
            }

            #mobile-menu a.drawer-anim-item .drawer-icon-box {
                transform: scale(0.75) rotate(-8deg);
                opacity: 0;
                transition:
                    transform 0.2s ease,
                    opacity 0.18s ease,
                    background-color 0.2s ease,
                    border-color 0.2s ease,
                    color 0.2s ease;
                will-change: transform, opacity;
            }
            #mobile-menu.drawer-is-open a.drawer-anim-item .drawer-icon-box {
                transform: scale(1) rotate(0deg);
                opacity: 1;
                transition:
                    transform 0.56s cubic-bezier(0.22, 1.35, 0.36, 1) calc(var(--stagger, 0) * 32ms + 85ms),
                    opacity 0.36s ease calc(var(--stagger, 0) * 32ms + 85ms),
                    background-color 0.2s ease,
                    border-color 0.2s ease,
                    color 0.2s ease;
            }

            #mobile-menu a.drawer-anim-item .drawer-item-text {
                display: inline-block;
                opacity: 0;
                transform: translate3d(-12px, 0, 0);
                transition:
                    transform 0.2s ease,
                    opacity 0.18s ease;
                will-change: transform, opacity;
            }
            #mobile-menu.drawer-is-open a.drawer-anim-item .drawer-item-text {
                opacity: 1;
                transform: translate3d(0, 0, 0);
                transition:
                    transform 0.58s cubic-bezier(0.19, 1, 0.22, 1) calc(var(--stagger, 0) * 32ms + 105ms),
                    opacity 0.42s cubic-bezier(0.19, 1, 0.22, 1) calc(var(--stagger, 0) * 32ms + 105ms);
            }

            #mobile-menu.drawer-is-open a.drawer-anim-item:hover .drawer-item-text,
            #mobile-menu.drawer-is-open a.drawer-anim-item:active .drawer-item-text {
                transform: translate3d(4px, 0, 0);
                transition: transform 0.24s cubic-bezier(0.22, 1, 0.36, 1);
            }
            #mobile-menu.drawer-is-open a.drawer-anim-item:hover .drawer-icon-box {
                transform: scale(1.08);
                transition: transform 0.24s cubic-bezier(0.22, 1.25, 0.36, 1);
            }

            @media (prefers-reduced-motion: reduce) {
                #mobile-menu .drawer-brand-wrap,
                #mobile-menu .drawer-anim-item,
                #mobile-menu a.drawer-anim-item .drawer-icon-box,
                #mobile-menu a.drawer-anim-item .drawer-item-text {
                    transition: none !important;
                    transform: none !important;
                    opacity: 1 !important;
                }
            }

            /* ==================== COLOROS DOT-TO-CAPSULE + NEWS TICKER ==================== */
            #coloros-live-capsule,
            #ktu-live-capsule {
                position: fixed;
                top: 5.4rem;
                left: 50%;
                z-index: 65;
                height: 38px;
                width: 38px;
                border-radius: 9999px;
                transform: translate3d(-50%, -6px, 0) scale(0);
                opacity: 0;
                pointer-events: none;
                overflow: hidden;
                background: rgba(18, 18, 22, 0.85) !important;
                backdrop-filter: blur(16px) saturate(190%) !important;
                -webkit-backdrop-filter: blur(16px) saturate(190%) !important;
                border: 1px solid rgba(255, 255, 255, 0.18) !important;
                color: #ffffff !important;
                box-shadow:
                    inset 1.5px 1.5px 0 -0.5px #fff9,
                    inset -1.5px -1.5px 0 -0.5px #ffffff4d,
                    0 16px 36px -8px rgba(0, 0, 0, 0.5) !important;
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
            #capsule-text { opacity: 0; transition: opacity 0.28s ease 0.14s; }
            #coloros-live-capsule.capsule-expanded #capsule-text,
            #ktu-live-capsule.capsule-expanded #capsule-text { opacity: 1; }

            .capsule-viewport-mask {
                -webkit-mask-image: linear-gradient(to right, transparent 0%, black 5%, black 93%, transparent 100%);
                mask-image: linear-gradient(to right, transparent 0%, black 5%, black 93%, transparent 100%);
            }

            @keyframes capsuleNewsTickerLeft {
                0% { transform: translate3d(0, 0, 0); }
                100% { transform: translate3d(-50%, 0, 0); }
            }
            #coloros-live-capsule.capsule-expanded #capsule-text.capsule-marquee-active {
                animation: capsuleNewsTickerLeft var(--marquee-duration, 8s) linear 0.45s infinite;
                will-change: transform;
            }
            #coloros-live-capsule.capsule-paused #capsule-text.capsule-marquee-active {
                animation-play-state: paused !important;
            }

            @keyframes capsule-shimmer {
                0% { background-position: -200% 0; }
                100% { background-position: 200% 0; }
            }
            .capsule-shimmer-bg {
                background-image: linear-gradient(90deg, transparent 0%, rgba(96, 165, 250, 0.22) 50%, transparent 100%);
                background-size: 200% 100%;
                animation: capsule-shimmer 1.8s cubic-bezier(0.4, 0, 0.6, 1) infinite;
            }

            html.ktu-tab-paused *,
            html.ktu-tab-paused *::before,
            html.ktu-tab-paused *::after {
                animation-play-state: paused !important;
            }

            /* ==================================================================
               A. LIGHT MODE: OPENBLAST SPECULAR RIM ON CARDS (.real-glass, .result-glass, etc.)
               ================================================================== */
            html:not(.dark) .real-glass,
            html:not(.dark) .glass-panel {
                background-color: rgba(255, 255, 255, 0.56) !important;
                background-image: linear-gradient(180deg, rgba(255, 255, 255, 0.35) 0%, rgba(255, 255, 255, 0) 50%) !important;
                -webkit-backdrop-filter: saturate(190%) blur(26px) !important;
                backdrop-filter: saturate(190%) blur(26px) !important;
                border: none !important;
                box-shadow:
                    inset 1.5px 1.5px 0 -0.5px #fffffff2,
                    inset -1.5px -1.5px 0 -0.5px #fff9,
                    inset 0 0 0 0.5px #00000014,
                    inset 0 0 14px #fff3,
                    0 14px 44px var(--glassMaterialShadowColor) !important;
            }

            html:not(.dark) .result-glass,
            html:not(.dark) .hybrid-card,
            html:not(.dark) .branch-card {
                background-color: rgba(255, 255, 255, 0.64) !important;
                background-image: linear-gradient(180deg, rgba(255, 255, 255, 0.38) 0%, rgba(255, 255, 255, 0) 55%) !important;
                -webkit-backdrop-filter: saturate(190%) blur(18px) !important;
                backdrop-filter: saturate(190%) blur(18px) !important;
                border: none !important;
                box-shadow:
                    inset 1.5px 1.5px 0 -0.5px #fffffff2,
                    inset -1.5px -1.5px 0 -0.5px #fff9,
                    inset 0 0 0 0.5px #00000014,
                    inset 0 0 14px #fff3,
                    0 10px 28px -6px rgba(15, 23, 42, 0.08) !important;
                transition:
                    transform 0.34s cubic-bezier(0.22, 1, 0.36, 1),
                    box-shadow 0.28s ease,
                    background-color 0.22s ease !important;
            }

            html:not(.dark) .result-glass:hover,
            html:not(.dark) .hybrid-card:hover,
            html:not(.dark) .branch-card:hover,
            html:not(.dark) .glass-panel-hover:hover {
                transform: translate3d(0, -4px, 0) scale(1.012) !important;
                background-color: rgba(255, 255, 255, 0.86) !important;
                box-shadow:
                    inset 1.5px 1.5px 0 -0.5px #ffffff,
                    inset -1.5px -1.5px 0 -0.5px #fff,
                    inset 0 0 0 1px rgba(79, 70, 229, 0.35),
                    0 18px 36px -8px rgba(79, 70, 229, 0.14) !important;
            }

            /* OpenBlast ot-press tactile scale physics */
            .result-glass:active,
            .hybrid-card:active,
            .branch-card:active,
            .group-select-card:active {
                transform: scale(0.96) !important;
                transition-duration: 80ms !important;
            }

            html:not(.dark) .inner-glass {
                background-color: rgba(255, 255, 255, 0.52) !important;
                border: none !important;
                box-shadow:
                    inset 1.5px 1.5px 0 -0.5px #fffffff2,
                    inset -1.5px -1.5px 0 -0.5px #fff9,
                    inset 0 0 0 0.5px #00000014,
                    inset 0 0 14px #fff3 !important;
            }

            /* ==================================================================
               B. 120FPS DARK MODE ENGINE (OpenBlast Dark Specular Rim + Zero Lag)
               ================================================================== */
            html.dark,
            html.dark body,
            html.dark body.bg-mesh,
            html.dark .bg-mesh {
                background-color: #060913 !important;
                background-image: 
                    radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.14) 0px, transparent 48%),
                    radial-gradient(at 100% 0%, rgba(16, 185, 129, 0.09) 0px, transparent 48%),
                    radial-gradient(at 50% 100%, rgba(99, 102, 241, 0.10) 0px, transparent 55%) !important;
                background-attachment: scroll !important;
                color: #f1f5f9 !important;
            }

            html.dark #mouse-orb-1,
            html.dark #mouse-orb-2,
            html.dark .ambient-orb,
            html.dark .ambient-orb-1,
            html.dark .ambient-orb-2,
            html.dark .ambient-orb-delayed,
            html.dark .orb-pulse {
                mix-blend-mode: normal !important;
                filter: none !important;
                -webkit-filter: none !important;
                animation: none !important;
                background: radial-gradient(circle, rgba(79, 70, 229, 0.10) 0%, transparent 65%) !important;
                opacity: 0.3 !important;
            }

            html.dark .text-transparent {
                color: transparent !important;
                -webkit-text-fill-color: transparent !important;
            }

            html.dark .text-slate-900:not(.text-transparent) { color: #ffffff !important; }
            html.dark .text-slate-800:not(.text-transparent) { color: #f1f5f9 !important; }
            html.dark .text-slate-700:not(.text-transparent) { color: #e2e8f0 !important; }
            html.dark .text-slate-600:not(.text-transparent) { color: #cbd5e1 !important; }
            html.dark .text-slate-500:not(.text-transparent) { color: #94a3b8 !important; }
            html.dark .text-slate-400:not(.text-transparent) { color: #94a3b8 !important; }

            html.dark .real-glass,
            html.dark .glass-panel {
                background: linear-gradient(145deg, rgba(22, 28, 46, 0.88) 0%, rgba(12, 16, 28, 0.92) 100%) !important;
                backdrop-filter: none !important;
                -webkit-backdrop-filter: none !important;
                border: none !important;
                box-shadow:
                    inset 1.5px 1.5px 0 -0.5px #ffffff40,
                    inset -1.5px -1.5px 0 -0.5px #ffffff1f,
                    inset 0 0 14px #ffffff0a,
                    0 16px 40px -8px rgba(0, 0, 0, 0.65) !important;
            }

            html.dark .result-glass,
            html.dark .hybrid-card,
            html.dark .timetable-card,
            html.dark .notice-card,
            html.dark .branch-card {
                background: linear-gradient(145deg, rgba(24, 32, 52, 0.88) 0%, rgba(13, 19, 34, 0.94) 100%) !important;
                backdrop-filter: none !important;
                -webkit-backdrop-filter: none !important;
                border: none !important;
                box-shadow:
                    inset 1.5px 1.5px 0 -0.5px #ffffff38,
                    inset -1.5px -1.5px 0 -0.5px #ffffff1a,
                    inset 0 0 14px #ffffff08,
                    0 10px 26px -6px rgba(0, 0, 0, 0.55) !important;
            }
            html.dark .result-glass:hover,
            html.dark .hybrid-card:hover,
            html.dark .timetable-card:hover,
            html.dark .notice-card:hover,
            html.dark .branch-card:hover,
            html.dark .glass-panel-hover:hover {
                background: linear-gradient(145deg, rgba(30, 40, 66, 0.94) 0%, rgba(17, 25, 44, 0.98) 100%) !important;
                box-shadow:
                    inset 1.5px 1.5px 0 -0.5px #ffffff66,
                    inset -1.5px -1.5px 0 -0.5px #6366f166,
                    0 16px 32px -6px rgba(0, 0, 0, 0.72) !important;
            }

            html.dark .timetable-card > div.pointer-events-none {
                color: #ffffff !important;
                opacity: 0.04 !important;
            }
            html.dark .timetable-card div[class*="bg-amber-50"] {
                background: rgba(245, 158, 11, 0.10) !important;
                border-top: 1px solid rgba(251, 191, 36, 0.22) !important;
            }
            html.dark .timetable-card .countdown-target {
                color: #fbbf24 !important;
            }

            html.dark .inner-glass {
                background: rgba(15, 22, 38, 0.82) !important;
                backdrop-filter: none !important;
                -webkit-backdrop-filter: none !important;
                border: none !important;
                box-shadow:
                    inset 1.5px 1.5px 0 -0.5px #ffffff2e,
                    inset -1.5px -1.5px 0 -0.5px #ffffff14 !important;
            }
            html.dark .glass-input,
            html.dark select.custom-select,
            html.dark #filter-panel select {
                background-color: rgba(9, 14, 26, 0.92) !important;
                backdrop-filter: none !important;
                -webkit-backdrop-filter: none !important;
                border: 1.5px solid rgba(255, 255, 255, 0.14) !important;
                color: #f8fafc !important;
            }
            html.dark .glass-input:focus {
                background-color: rgba(15, 23, 42, 0.98) !important;
                border-color: #6366f1 !important;
                box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.2) !important;
            }
            html.dark .glass-input:disabled {
                background-color: rgba(15, 23, 42, 0.4) !important;
                color: #475569 !important;
                border-color: rgba(255, 255, 255, 0.05) !important;
            }
            html.dark select option {
                background-color: #0f172a !important;
                color: #f8fafc !important;
            }

            html.dark div[class*="bg-slate-200"] {
                background-color: rgba(8, 12, 22, 0.85) !important;
                border-color: rgba(255, 255, 255, 0.11) !important;
            }
            html.dark div[class*="bg-slate-200"] > button.bg-white {
                background: linear-gradient(135deg, rgba(37, 99, 235, 0.34), rgba(79, 70, 229, 0.34)) !important;
                color: #93c5fd !important;
                border: 1px solid rgba(96, 165, 250, 0.45) !important;
                box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.2), 0 4px 12px rgba(0, 0, 0, 0.35) !important;
            }
            html.dark div[class*="bg-slate-200"] > button:not(.bg-white) {
                color: #94a3b8 !important;
            }
            html.dark div[class*="bg-slate-200"] > button:not(.bg-white):hover {
                color: #f1f5f9 !important;
                background-color: rgba(255, 255, 255, 0.06) !important;
            }

            html.dark a[class*="bg-white"],
            html.dark button[class*="bg-white"],
            html.dark .result-glass button.bg-white,
            html.dark .inner-glass button.bg-white,
            html.dark #btn-prev,
            html.dark #btn-next,
            html.dark #chevron-trigger,
            html.dark button[class*="bg-slate-100"],
            html.dark span[class*="bg-slate-100"],
            html.dark div[class*="bg-slate-100"] {
                background-color: rgba(24, 34, 53, 0.88) !important;
                border-color: rgba(255, 255, 255, 0.16) !important;
                color: #f1f5f9 !important;
            }
            html.dark a[class*="bg-white"]:hover,
            html.dark button[class*="bg-white"]:hover,
            html.dark .result-glass button.bg-white:hover,
            html.dark #chevron-trigger:hover {
                background-color: #4f46e5 !important;
                border-color: #6366f1 !important;
                color: #ffffff !important;
            }
            html.dark span[class*="bg-white/"],
            html.dark div[class*="bg-white/"] {
                background-color: rgba(15, 23, 42, 0.82) !important;
                border-color: rgba(255, 255, 255, 0.14) !important;
                color: #e2e8f0 !important;
            }

            html.dark [class*="bg-indigo-50"],
            html.dark [class*="bg-indigo-100"] {
                background-color: rgba(79, 70, 229, 0.22) !important;
                border-color: rgba(99, 102, 241, 0.42) !important;
                color: #c7d2fe !important;
            }
            html.dark #new-timetable-banner > div {
                background: linear-gradient(135deg, rgba(23, 31, 56, 0.96) 0%, rgba(14, 20, 38, 0.98) 100%) !important;
                border-color: rgba(99, 102, 241, 0.45) !important;
            }
            html.dark [class*="bg-blue-50"],
            html.dark [class*="bg-blue-100"] {
                background-color: rgba(37, 99, 235, 0.22) !important;
                border-color: rgba(59, 130, 246, 0.42) !important;
                color: #bae6fd !important;
            }
            html.dark [class*="bg-emerald-50"],
            html.dark [class*="bg-emerald-100"] {
                background-color: rgba(16, 185, 129, 0.20) !important;
                border-color: rgba(52, 211, 153, 0.42) !important;
                color: #6ee7b7 !important;
            }
            html.dark [class*="bg-amber-50"],
            html.dark [class*="bg-amber-100"],
            html.dark [class*="bg-orange-100"] {
                background-color: rgba(245, 158, 11, 0.20) !important;
                border-color: rgba(251, 191, 36, 0.42) !important;
                color: #fde68a !important;
            }
            html.dark [class*="bg-purple-50"] {
                background-color: rgba(147, 51, 234, 0.22) !important;
                border-color: rgba(168, 85, 247, 0.42) !important;
                color: #e9d5ff !important;
            }
            html.dark [class*="bg-red-50"],
            html.dark [class*="bg-rose-50"],
            html.dark [class*="bg-rose-100"] {
                background-color: rgba(225, 29, 72, 0.22) !important;
                border-color: rgba(244, 63, 94, 0.42) !important;
                color: #fecdd3 !important;
            }

            html.dark .glass-folder {
                background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.75) 100%) !important;
                border-color: rgba(255, 255, 255, 0.16) !important;
            }
            html.dark .glass-folder div[class*="bg-white"] {
                background: rgba(15, 23, 42, 0.9) !important;
                border-color: rgba(255, 255, 255, 0.15) !important;
            }

            html.dark .hybrid-card .bg-white {
                background-color: rgba(255, 255, 255, 0.07) !important;
                border-color: rgba(255, 255, 255, 0.12) !important;
                color: #cbd5e1 !important;
            }
            html.dark .hybrid-card:hover .bg-white {
                background-color: #4f46e5 !important;
                border-color: #6366f1 !important;
                color: #ffffff !important;
            }

            html.dark footer {
                background-color: rgba(6, 9, 19, 0.90) !important;
                border-top-color: rgba(255, 255, 255, 0.08) !important;
            }
            html.dark #notice-modal-content,
            html.dark #editorModal > div {
                background: rgba(15, 23, 42, 0.96) !important;
                border: 1px solid rgba(255, 255, 255, 0.15) !important;
            }

            html.dark #mobile-menu {
                background: linear-gradient(165deg, rgba(15, 23, 42, 0.88) 0%, rgba(7, 11, 20, 0.92) 100%) !important;
                backdrop-filter: blur(28px) saturate(200%) !important;
                -webkit-backdrop-filter: blur(28px) saturate(200%) !important;
                border-right: 1px solid rgba(255, 255, 255, 0.16) !important;
            }
            html.dark #mobile-menu .drawer-header {
                background: rgba(7, 11, 20, 0.55) !important;
                border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
            }
            html.dark #mobile-menu .nav-section-label { color: #94a3b8 !important; }
            html.dark #mobile-menu a.drawer-link-inactive { color: #f1f5f9 !important; text-shadow: none; }
            html.dark #mobile-menu a.drawer-link-inactive:hover { background: rgba(255, 255, 255, 0.08) !important; color: #ffffff !important; }
            html.dark #mobile-menu a.drawer-link-active {
                background: rgba(79, 70, 229, 0.28) !important;
                color: #a5b4fc !important;
                border: 1px solid rgba(99, 102, 241, 0.45) !important;
            }
            html.dark #mobile-menu .drawer-icon-box {
                background: rgba(255, 255, 255, 0.08);
                border-color: rgba(255, 255, 255, 0.12);
                color: #cbd5e1;
            }
            html.dark #mobile-menu a.drawer-link-active .drawer-icon-box {
                background: #4f46e5;
                border-color: #6366f1;
                color: #ffffff;
            }
            html.dark .theme-toggle-btn,
            html.dark header a[aria-label="Notifications"] {
                background-color: rgba(255, 255, 255, 0.08) !important;
                border-color: rgba(255, 255, 255, 0.14) !important;
                color: #f1f5f9 !important;
            }
            html.dark .theme-toggle-btn:hover,
            html.dark header a[aria-label="Notifications"]:hover {
                background-color: rgba(255, 255, 255, 0.16) !important;
            }
        `;
        document.head.appendChild(style);
    }

    mountDarkStyles();
})();

// ==============================================================================
// 3. GOOGLE ANALYTICS 4 (GA4) LIVE TRACKING
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
// 4. RESPONSIVE NAVIGATION LOADER (Mounts Full-Screen Drawer to document.body)
// ==============================================================================
function loadNavigation(activePage, basePath = '', isBlog = false) { 
    const container = document.getElementById('navigation-container');
    if (!container) return;

    if (window.KTUFlow && typeof window.KTUFlow.ensureCapsuleMounted === 'function') {
        window.KTUFlow.ensureCapsuleMounted();
    }

    container.classList.remove('relative');
    container.classList.add('sticky', 'top-0', 'z-50', 'w-full');

    const LIGHT_LOGO_SRC = '/k.png';
    const DARK_LOGO_SRC  = '/assets/k-logo-darktheme.png';

    const preloadDarkLogo = new Image();
    preloadDarkLogo.src = DARK_LOGO_SRC;

    const initialLogoSrc = document.documentElement.classList.contains('dark')
        ? DARK_LOGO_SRC
        : LIGHT_LOGO_SRC;

    const logoExtension = isBlog ? ' <span class="text-slate-400 font-medium ml-1">| Blog</span>' : '';

    const navItemClass = (key) => activePage === key
        ? 'drawer-link-active font-extrabold'
        : 'drawer-link-inactive font-bold border border-transparent';

    // Remove any existing drawer/overlay before mounting fresh ones directly onto document.body
    document.getElementById('mobile-menu')?.remove();
    document.getElementById('menu-overlay')?.remove();

    const drawerAndOverlayHTML = `
        <div id="mobile-menu" aria-hidden="true" style="visibility: hidden;" 
             class="fixed inset-y-0 left-0 w-72 transform -translate-x-full z-[80] flex flex-col will-change-transform">
            
            <div class="drawer-header p-5 flex justify-between items-center shrink-0">
                <div class="drawer-brand-wrap flex items-center gap-2">
                    <img src="${initialLogoSrc}" alt="Kerala Timetable Logo" class="kt-brand-logo w-6 h-6 object-contain shrink-0" width="24" height="24" />
                    <span class="text-base font-extrabold text-slate-900 tracking-tight leading-none whitespace-nowrap">Kerala <span class="text-indigo-600">Timetable</span></span>
                </div>
                <button id="close-menu-btn" aria-label="Close menu" class="w-8 h-8 flex items-center justify-center text-slate-600 dark:text-slate-300 hover:text-rose-500 transition-all rounded-full bg-white/70 dark:bg-white/10 shadow-sm active:scale-95 focus:outline-none">
                    <i class="fas fa-times text-base"></i>
                </button>
            </div>
            
            <nav class="flex-grow py-4 px-3.5 flex flex-col gap-1.5 overflow-y-auto overflow-x-hidden">
                <p style="--stagger: 0;" class="drawer-anim-item nav-section-label px-3 pt-1 pb-1 text-[10px] font-extrabold uppercase">Academics</p>
                
                <a href="/index.html" style="--stagger: 1;" class="drawer-anim-item flex items-center gap-3 px-3 py-2.5 rounded-2xl text-[15px] active:scale-[0.98] ${navItemClass('home')}">
                    <span class="drawer-icon-box w-8 h-8 rounded-xl flex items-center justify-center shrink-0"><i class="fas fa-home text-xs"></i></span>
                    <span class="drawer-item-text">Home</span>
                </a>
                
                <a href="/timetable.html" style="--stagger: 2;" class="drawer-anim-item flex items-center gap-3 px-3 py-2.5 rounded-2xl text-[15px] active:scale-[0.98] ${navItemClass('timetable')}">
                    <span class="drawer-icon-box w-8 h-8 rounded-xl flex items-center justify-center shrink-0"><i class="fas fa-calendar-day text-xs"></i></span>
                    <span class="drawer-item-text">Timetables</span>
                </a>
                
                <a href="/notes.html" style="--stagger: 3;" class="drawer-anim-item flex items-center gap-3 px-3 py-2.5 rounded-2xl text-[15px] active:scale-[0.98] ${navItemClass('notes')}">
                    <span class="drawer-icon-box w-8 h-8 rounded-xl flex items-center justify-center shrink-0"><i class="fas fa-book-open text-xs"></i></span>
                    <span class="drawer-item-text">Study Notes</span>
                </a>

                <a href="/pyq.html" style="--stagger: 4;" class="drawer-anim-item flex items-center gap-3 px-3 py-2.5 rounded-2xl text-[15px] active:scale-[0.98] ${navItemClass('pyq')}">
                    <span class="drawer-icon-box w-8 h-8 rounded-xl flex items-center justify-center shrink-0"><i class="fas fa-file-alt text-xs"></i></span>
                    <span class="drawer-item-text">Previous Papers</span>
                </a>

                <a href="/activitypoints.html" style="--stagger: 5;" class="drawer-anim-item flex items-center gap-3 px-3 py-2.5 rounded-2xl text-[15px] active:scale-[0.98] ${navItemClass('activity')}">
                    <span class="drawer-icon-box w-8 h-8 rounded-xl flex items-center justify-center shrink-0"><i class="fas fa-award text-xs"></i></span>
                    <span class="drawer-item-text">Activity Points</span>
                </a>

                <p style="--stagger: 6;" class="drawer-anim-item nav-section-label px-3 pt-4 pb-1 text-[10px] font-extrabold uppercase">Community & Updates</p>

                <a href="/doubts.html" style="--stagger: 7;" class="drawer-anim-item flex items-center gap-3 px-3 py-2.5 rounded-2xl text-[15px] active:scale-[0.98] ${navItemClass('qa')}">
                    <span class="drawer-icon-box w-8 h-8 rounded-xl flex items-center justify-center shrink-0"><i class="fas fa-comments text-xs"></i></span>
                    <span class="drawer-item-text">Q&A Hub</span>
                </a>
                
                <a href="/updates.html" style="--stagger: 8;" class="drawer-anim-item flex items-center gap-3 px-3 py-2.5 rounded-2xl text-[15px] active:scale-[0.98] ${navItemClass('updates')}">
                    <span class="drawer-icon-box w-8 h-8 rounded-xl flex items-center justify-center shrink-0"><i class="fas fa-bullhorn text-xs"></i></span>
                    <span class="drawer-item-text">Latest Updates</span>
                </a>
                
                <a href="/blog/index.html" style="--stagger: 9;" class="drawer-anim-item flex items-center gap-3 px-3 py-2.5 rounded-2xl text-[15px] active:scale-[0.98] ${navItemClass('blog')}">
                    <span class="drawer-icon-box w-8 h-8 rounded-xl flex items-center justify-center shrink-0"><i class="fas fa-feather-alt text-xs"></i></span>
                    <span class="drawer-item-text">Blog</span>
                </a>

                <a href="/status.html" style="--stagger: 10;" class="drawer-anim-item flex items-center gap-3 px-3 py-2.5 rounded-2xl text-[15px] active:scale-[0.98] ${navItemClass('status')}">
                    <span class="drawer-icon-box w-8 h-8 rounded-xl flex items-center justify-center shrink-0"><i class="fas fa-server text-xs"></i></span>
                    <span class="drawer-item-text">Server Status</span>
                </a>

                <a href="/contact-us.html" style="--stagger: 11;" class="drawer-anim-item flex items-center gap-3 px-3 py-2.5 rounded-2xl text-[15px] active:scale-[0.98] ${navItemClass('contact')}">
                    <span class="drawer-icon-box w-8 h-8 rounded-xl flex items-center justify-center shrink-0"><i class="fas fa-envelope text-xs"></i></span>
                    <span class="drawer-item-text">Contact Us</span>
                </a>

                <a href="/about.html" style="--stagger: 12;" class="drawer-anim-item flex items-center gap-3 px-3 py-2.5 rounded-2xl text-[15px] active:scale-[0.98] ${navItemClass('about')}">
                    <span class="drawer-icon-box w-8 h-8 rounded-xl flex items-center justify-center shrink-0"><i class="fas fa-info-circle text-xs"></i></span>
                    <span class="drawer-item-text">About</span>
                </a>
            </nav>
        </div>

        <div id="menu-overlay" style="visibility: hidden;" class="fixed inset-0 bg-slate-900/35 backdrop-blur-[2px] z-[75] opacity-0 pointer-events-none will-change-[opacity]"></div>
    `;

    document.body.insertAdjacentHTML('beforeend', drawerAndOverlayHTML);

    const headerHTML = `
        <header class="kt-frosted-header glass-pill w-full z-40 transition-all duration-300">
            <div class="max-w-6xl mx-auto px-3.5 sm:px-6 py-2.5 sm:py-3.5 flex justify-between items-center gap-2">
                <div class="flex items-center gap-2 sm:gap-3 min-w-0">
                    <button id="open-menu-btn" aria-label="Open menu" class="p-1.5 -ml-1 text-slate-600 hover:text-indigo-600 hover:bg-white/60 dark:hover:bg-white/10 rounded-lg transition-colors focus:outline-none lg:hidden shrink-0">
                        <i class="fas fa-bars text-lg sm:text-xl"></i>
                    </button>
                    <a href="/index.html" class="flex items-center gap-2 hover:opacity-80 transition-opacity min-w-0">
                        <img src="${initialLogoSrc}" alt="Kerala Timetable Logo" class="kt-brand-logo w-6 h-6 sm:w-7 sm:h-7 object-contain shrink-0" width="28" height="28" />
                        <h1 class="text-[18px] sm:text-2xl font-extrabold tracking-tight text-slate-900 leading-none whitespace-nowrap truncate">Kerala <span class="text-indigo-600">Timetable</span>${logoExtension}</h1>
                    </a>
                </div>

                <div class="hidden lg:flex gap-2 items-center shrink-0">
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

                    <button class="theme-toggle-btn w-9 h-9 ml-1 rounded-full flex items-center justify-center bg-slate-100/85 text-slate-600 hover:bg-slate-200 border border-slate-200 transition-all active:scale-95 shadow-inner focus:outline-none" aria-label="Toggle Theme">
                        <i class="fas fa-moon text-[13px]"></i>
                    </button>
                </div>
                
                <div class="lg:hidden flex items-center gap-1.5 shrink-0">
                    <button class="theme-toggle-btn w-9 h-9 flex items-center justify-center bg-slate-100/85 text-slate-600 rounded-full border border-slate-200 shadow-sm transition-all active:scale-95 focus:outline-none" aria-label="Toggle Theme">
                        <i class="fas fa-moon text-[13px]"></i>
                    </button>
                    <a href="/updates.html" aria-label="Notifications" class="w-9 h-9 flex items-center justify-center bg-slate-100/85 text-indigo-600 rounded-full border border-slate-200 shadow-sm transition-all active:scale-95">
                       <i class="fas fa-bell text-[13px]"></i>
                    </a>
                </div>
            </div>
        </header>
    `;

    container.innerHTML = headerHTML;

    // Attach OpenBlast 1:1 Liquid Glass Lens to Header & Page Docks
    if (window.KTULiquidGlass) {
        window.KTULiquidGlass.scanAndAttachAllPills();
    }
    
    const themeBtns = document.querySelectorAll('.theme-toggle-btn');
    
    function updateThemeIconsAndLogo() {
        const isDark = document.documentElement.classList.contains('dark');
        themeBtns.forEach(btn => {
            btn.innerHTML = isDark 
                ? '<i class="fas fa-sun text-[13px] text-amber-400"></i>' 
                : '<i class="fas fa-moon text-[13px] text-slate-600"></i>';
        });

        const targetLogo = isDark ? DARK_LOGO_SRC : LIGHT_LOGO_SRC;
        document.querySelectorAll('.kt-brand-logo').forEach(img => {
            if (img.getAttribute('src') !== targetLogo) {
                img.setAttribute('src', targetLogo);
            }
        });
    }
    
    updateThemeIconsAndLogo();
    
    themeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            document.documentElement.classList.toggle('dark');
            const isDark = document.documentElement.classList.contains('dark');
            localStorage.setItem('kt_theme', isDark ? 'dark' : 'light');
            updateThemeIconsAndLogo();
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

            menu.style.transition = 'transform 0.36s cubic-bezier(0.22, 1, 0.36, 1)';
            overlay.classList.add('transition-opacity', 'duration-300');

            void menu.offsetWidth;

            menu.classList.remove('-translate-x-full');
            menu.classList.add('drawer-is-open');
            menu.setAttribute('aria-hidden', 'false');
            overlay.classList.remove('opacity-0', 'pointer-events-none');
            overlay.classList.add('opacity-100', 'pointer-events-auto');
            document.body.style.overflow = 'hidden';
        } else {
            menu.classList.remove('drawer-is-open');
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
            }, 340);
        }
    }

    openBtn?.addEventListener('click', () => setMenuState(true));
    closeBtn?.addEventListener('click', () => setMenuState(false));
    overlay.addEventListener('click', () => setMenuState(false));

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
// 5. GLOBAL AD INJECTOR STRICTLY FOR NOTE PAGES
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
// 6. AUTHENTIC LIQUID GLASS WHATSAPP CHANNEL PROMPT
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
                    background: rgba(18, 24, 38, 0.86);
                    backdrop-filter: blur(20px) saturate(180%);
                    -webkit-backdrop-filter: blur(20px) saturate(180%);
                    border: 1px solid rgba(255, 255, 255, 0.16);
                    box-shadow: inset 1.5px 1.5px 0 -0.5px #fff9, inset -1.5px -1.5px 0 -0.5px #ffffff4d, 0 24px 48px -12px rgba(0, 0, 0, 0.65);
                 ">
                <div class="relative z-10 flex flex-col gap-3.5 sm:gap-4">
                    <div class="flex items-start justify-between gap-3">
                        <div class="flex items-center gap-3.5">
                            <div class="w-12 h-12 rounded-2xl bg-[#0f2c25] border border-emerald-400/60 flex items-center justify-center text-emerald-400 text-2xl shadow-inner shrink-0">
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
                        <button id="ktu-wa-later-btn" class="w-full py-3 px-4 rounded-full bg-white/10 hover:bg-white/15 text-slate-200 font-bold text-xs sm:text-sm transition-all border border-white/10 active:scale-95 text-center">
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
// 7. SAFE AUTO-INIT
// ==============================================================================
function runInitializers() {
    if (window.KTUFlow && typeof window.KTUFlow.ensureCapsuleMounted === 'function') {
        window.KTUFlow.ensureCapsuleMounted();
    }
    if (window.KTULiquidGlass && typeof window.KTULiquidGlass.scanAndAttachAllPills === 'function') {
        window.KTULiquidGlass.scanAndAttachAllPills();
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
