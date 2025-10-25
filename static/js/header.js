// Header functionality
document.addEventListener('DOMContentLoaded', function () {
    // Quick Actions dropdown functionality
    const quickActionsBtn = document.getElementById('quickActionsBtn');
    const quickActionsMenu = document.getElementById('quickActionsMenu');
    let quickActionsOpen = false;

    // Toggle quick actions dropdown
    if (quickActionsBtn) {
        quickActionsBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            if (quickActionsOpen) {
                quickActionsMenu.classList.add('hidden');
            } else {
                quickActionsMenu.classList.remove('hidden');
            }
            quickActionsOpen = !quickActionsOpen;
        });
    }

    // Close quick actions dropdown when clicking outside
    document.addEventListener('click', function (event) {
        if (quickActionsOpen && quickActionsBtn && quickActionsMenu) {
            if (!quickActionsBtn.contains(event.target) && !quickActionsMenu.contains(event.target)) {
                quickActionsMenu.classList.add('hidden');
                quickActionsOpen = false;
            }
        }
    });

    // Dark mode toggle
    const darkModeToggle = document.getElementById('darkModeToggle');

    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function () {
            document.documentElement.classList.toggle('dark');

            // Update icon
            const icon = darkModeToggle.querySelector('i');
            if (document.documentElement.classList.contains('dark')) {
                icon.setAttribute('data-lucide', 'sun');
            } else {
                icon.setAttribute('data-lucide', 'moon');
            }
            lucide.createIcons();

            // Save preference
            const isDark = document.documentElement.classList.contains('dark');
            localStorage.setItem('darkMode', isDark);
        });

        // Load saved preference
        const savedDarkMode = localStorage.getItem('darkMode');
        if (savedDarkMode === 'true') {
            document.documentElement.classList.add('dark');
            const icon = darkModeToggle.querySelector('i');
            icon.setAttribute('data-lucide', 'sun');
            lucide.createIcons();
        }
    }
});

