function loadNavigation(activePage, basePath = '', isBlog = false) {
    const navContainer = document.getElementById('navigation-container');
    if (!navContainer) return;

    // Determine the logo text based on whether it's a blog page
    const logoHtml = isBlog 
        ? `<span class="text-slate-800">Kerala <span class="text-indigo-600">Timetable</span> <span class="text-slate-300 font-light ml-1">| Blog</span></span>`
        : `<span class="text-slate-800">Kerala <span class="text-indigo-600">Timetable</span></span>`;

    const navHTML = `
        <header class="bg-white/80 backdrop-blur-md border-b border-slate-200/60 sticky top-0 z-50 shadow-sm">
            <div class="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
                
                <button id="mobile-menu-btn" class="md:hidden text-slate-500 hover:text-indigo-600 focus:outline-none p-2 -ml-2 rounded-lg hover:bg-slate-50 transition-colors">
                    <i class="fas fa-bars text-xl"></i>
                </button>

                <a href="${basePath}index.html" class="flex items-center gap-2 font-black text-xl tracking-tight hover:opacity-80 transition-opacity">
                    <div class="w-8 h-8 rounded-xl bg-indigo-600 text-white flex items-center justify-center shadow-md shadow-indigo-200">
                        <i class="far fa-calendar-alt text-sm"></i>
                    </div>
                    ${logoHtml}
                </a>

                <nav class="hidden md:flex items-center gap-8 text-sm font-bold text-slate-500">
                    <a href="${basePath}index.html" class="hover:text-indigo-600 transition-colors ${activePage === 'home' ? 'text-indigo-600' : ''}">Home</a>
                    <a href="${basePath}status.html" class="hover:text-indigo-600 transition-colors ${activePage === 'status' ? 'text-indigo-600' : ''}">Server Status</a>
                    <a href="${basePath}updates.html" class="hover:text-indigo-600 transition-colors ${activePage === 'updates' ? 'text-indigo-600' : ''}">Notice Board</a>
                    <a href="${basePath}blog/index.html" class="hover:text-indigo-600 transition-colors ${activePage === 'blog' ? 'text-indigo-600' : ''}">Blog</a>
                    <a href="${basePath}about.html" class="hover:text-indigo-600 transition-colors ${activePage === 'about' ? 'text-indigo-600' : ''}">About</a>
                </nav>

                <a href="${basePath}updates.html" class="w-10 h-10 rounded-full bg-indigo-50 text-indigo-600 flex items-center justify-center hover:bg-indigo-100 transition-colors shadow-sm relative">
                    <i class="fas fa-bell"></i>
                    <span class="absolute top-2 right-2 w-2 h-2 bg-rose-500 rounded-full animate-pulse border border-white"></span>
                </a>
            </div>
        </header>

        <div id="mobile-menu-overlay" class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-[60] hidden opacity-0 transition-opacity duration-300"></div>

        <div id="mobile-menu-panel" class="fixed top-0 left-0 h-full w-4/5 max-w-sm bg-white z-[70] transform -translate-x-full transition-transform duration-300 shadow-2xl flex flex-col">
            
            <div class="h-16 px-4 flex items-center justify-between border-b border-slate-100">
                <div class="flex items-center gap-2 font-black text-lg tracking-tight">
                    <div class="w-7 h-7 rounded-lg bg-indigo-600 text-white flex items-center justify-center shadow-md">
                        <i class="far fa-calendar-alt text-xs"></i>
                    </div>
                    <span class="text-slate-800">Menu</span>
                </div>
                <button id="close-menu-btn" class="w-8 h-8 rounded-full bg-slate-50 text-slate-500 flex items-center justify-center hover:bg-rose-50 hover:text-rose-500 transition-colors">
                    <i class="fas fa-times"></i>
                </button>
            </div>

            <nav class="flex-grow overflow-y-auto p-4 space-y-2">
                <a href="${basePath}index.html" class="flex items-center px-4 py-3 rounded-xl ${activePage === 'home' ? 'bg-indigo-50 text-indigo-600 font-bold' : 'text-slate-600 hover:bg-slate-50 hover:text-indigo-600 font-medium'} transition-all">
                    <i class="fas fa-home w-6 text-center mr-2 text-lg"></i> Home
                </a>
                <a href="${basePath}status.html" class="flex items-center px-4 py-3 rounded-xl ${activePage === 'status' ? 'bg-indigo-50 text-indigo-600 font-bold' : 'text-slate-600 hover:bg-slate-50 hover:text-indigo-600 font-medium'} transition-all">
                    <i class="fas fa-server w-6 text-center mr-2 text-lg"></i> Server Status
                </a>
                <a href="${basePath}updates.html" class="flex items-center px-4 py-3 rounded-xl ${activePage === 'updates' ? 'bg-indigo-50 text-indigo-600 font-bold' : 'text-slate-600 hover:bg-slate-50 hover:text-indigo-600 font-medium'} transition-all">
                    <i class="fas fa-bullhorn w-6 text-center mr-2 text-lg"></i> Notice Board
                </a>
                <a href="${basePath}blog/index.html" class="flex items-center px-4 py-3 rounded-xl ${activePage === 'blog' ? 'bg-indigo-50 text-indigo-600 font-bold' : 'text-slate-600 hover:bg-slate-50 hover:text-indigo-600 font-medium'} transition-all">
                    <i class="fas fa-book-open w-6 text-center mr-2 text-lg"></i> Blog
                </a>
                <a href="${basePath}about.html" class="flex items-center px-4 py-3 rounded-xl ${activePage === 'about' ? 'bg-indigo-50 text-indigo-600 font-bold' : 'text-slate-600 hover:bg-slate-50 hover:text-indigo-600 font-medium'} transition-all">
                    <i class="fas fa-info-circle w-6 text-center mr-2 text-lg"></i> About
                </a>
            </nav>

            <div class="p-4 border-t border-slate-100 bg-slate-50/50">
                <p class="text-xs font-bold text-slate-400 text-center uppercase tracking-wider mb-2">Developed for KTU Students</p>
                <div class="flex justify-center gap-3">
                    <a href="#" class="w-8 h-8 rounded-full bg-white border border-slate-200 text-slate-400 flex items-center justify-center hover:text-indigo-600 hover:border-indigo-200 transition-colors shadow-sm"><i class="fab fa-instagram"></i></a>
                    <a href="#" class="w-8 h-8 rounded-full bg-white border border-slate-200 text-slate-400 flex items-center justify-center hover:text-indigo-600 hover:border-indigo-200 transition-colors shadow-sm"><i class="fab fa-telegram-plane"></i></a>
                </div>
            </div>
        </div>
    `;

    navContainer.innerHTML = navHTML;

    // Mobile Menu Toggle Logic
    const menuBtn = document.getElementById('mobile-menu-btn');
    const closeBtn = document.getElementById('close-menu-btn');
    const overlay = document.getElementById('mobile-menu-overlay');
    const panel = document.getElementById('mobile-menu-panel');

    function openMenu() {
        overlay.classList.remove('hidden');
        // Small delay to allow display:block to apply before animating opacity
        setTimeout(() => {
            overlay.classList.remove('opacity-0');
            panel.classList.remove('-translate-x-full');
        }, 10);
        document.body.style.overflow = 'hidden'; // Prevent scrolling
    }

    function closeMenu() {
        overlay.classList.add('opacity-0');
        panel.classList.add('-translate-x-full');
        setTimeout(() => {
            overlay.classList.add('hidden');
        }, 300); // Wait for transition to finish
        document.body.style.overflow = ''; // Restore scrolling
    }

    menuBtn.addEventListener('click', openMenu);
    closeBtn.addEventListener('click', closeMenu);
    overlay.addEventListener('click', closeMenu);
}
