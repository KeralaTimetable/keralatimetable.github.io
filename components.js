function loadNavigation(activePage = '', basePath = '', isSubdir = false) {
    const navHtml = `
    <header class="bg-white/80 backdrop-blur-md border-b border-slate-200 sticky top-0 z-50 transition-all duration-300">
        <div class="max-w-5xl mx-auto px-4">
            <div class="flex items-center justify-between h-16 md:h-20">
                
                <a href="${basePath}index.html" class="flex items-center gap-3 group">
                    <div class="w-10 h-10 bg-gradient-to-br from-indigo-600 to-emerald-500 rounded-xl flex items-center justify-center text-white font-black text-lg shadow-sm group-hover:shadow-md group-hover:scale-105 transition-all duration-300">
                        KT
                    </div>
                    <span class="font-extrabold text-slate-800 text-lg md:text-xl tracking-tight group-hover:text-indigo-600 transition-colors">Kerala Timetable</span>
                </a>

                <nav class="hidden md:flex items-center gap-8">
                    <a href="${basePath}index.html" class="text-sm font-bold ${activePage === 'home' ? 'text-indigo-600' : 'text-slate-500 hover:text-indigo-600'} transition-colors">Home</a>
                    
                    <a href="${basePath}timetable.html" class="text-sm font-bold ${activePage === 'timetable' ? 'text-indigo-600' : 'text-slate-500 hover:text-indigo-600'} transition-colors">Timetables</a>
                    
                    <a href="${basePath}notes.html" class="text-sm font-bold ${activePage === 'notes' ? 'text-indigo-600' : 'text-slate-500 hover:text-indigo-600'} transition-colors">Study Notes</a>
                    
                    <a href="${basePath}updates.html" class="text-sm font-bold ${activePage === 'updates' ? 'text-indigo-600' : 'text-slate-500 hover:text-indigo-600'} transition-colors">Updates</a>
                    <a href="${basePath}status.html" class="text-sm font-bold flex items-center gap-1.5 ${activePage === 'status' ? 'text-indigo-600' : 'text-slate-500 hover:text-indigo-600'} transition-colors">
                        <span class="relative flex h-2 w-2">
                          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                          <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                        </span>
                        Status
                    </a>
                </nav>

                <button id="mobile-menu-btn" class="md:hidden w-10 h-10 flex items-center justify-center text-slate-500 hover:bg-slate-100 hover:text-indigo-600 rounded-lg transition-colors focus:outline-none">
                    <i class="fas fa-bars text-xl"></i>
                </button>
            </div>
        </div>

        <div id="mobile-menu" class="hidden md:hidden bg-white border-t border-slate-100 absolute w-full shadow-[0_20px_25px_-5px_rgba(0,0,0,0.1)]">
            <div class="flex flex-col px-6 py-4 space-y-4">
                <a href="${basePath}index.html" class="text-base font-bold flex items-center gap-3 ${activePage === 'home' ? 'text-indigo-600' : 'text-slate-600 hover:text-indigo-600'} transition-colors">
                    <i class="fas fa-home w-5 text-center"></i> Home
                </a>
                
                <a href="${basePath}timetable.html" class="text-base font-bold flex items-center gap-3 ${activePage === 'timetable' ? 'text-indigo-600' : 'text-slate-600 hover:text-indigo-600'} transition-colors">
                    <i class="fas fa-calendar-day w-5 text-center"></i> Timetables
                </a>

                <a href="${basePath}notes.html" class="text-base font-bold flex items-center gap-3 ${activePage === 'notes' ? 'text-indigo-600' : 'text-slate-600 hover:text-indigo-600'} transition-colors">
                    <i class="fas fa-book-open w-5 text-center"></i> Study Notes
                </a>

                <a href="${basePath}updates.html" class="text-base font-bold flex items-center gap-3 ${activePage === 'updates' ? 'text-indigo-600' : 'text-slate-600 hover:text-indigo-600'} transition-colors">
                    <i class="fas fa-bullhorn w-5 text-center"></i> Notice Board
                </a>
                
                <a href="${basePath}status.html" class="text-base font-bold flex items-center gap-3 ${activePage === 'status' ? 'text-indigo-600' : 'text-slate-600 hover:text-indigo-600'} transition-colors">
                    <div class="w-5 flex justify-center">
                        <span class="relative flex h-2.5 w-2.5">
                            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                            <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                        </span>
                    </div>
                    Server Status
                </a>
            </div>
        </div>
    </header>
    `;

    // Inject into the page
    const container = document.getElementById('navigation-container');
    if (container) {
        container.innerHTML = navHtml;
    }

    // Mobile Menu Toggle Logic
    const btn = document.getElementById('mobile-menu-btn');
    const menu = document.getElementById('mobile-menu');
    const icon = btn ? btn.querySelector('i') : null;

    if (btn && menu && icon) {
        btn.addEventListener('click', () => {
            menu.classList.toggle('hidden');
            if (menu.classList.contains('hidden')) {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            } else {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
            }
        });
    }
}
