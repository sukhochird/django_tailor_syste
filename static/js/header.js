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

    // Fullscreen toggle
    const fullscreenToggle = document.getElementById('fullscreenToggle');

    if (fullscreenToggle) {
        // Check if fullscreen is supported
        const isFullscreenSupported = document.fullscreenEnabled ||
            document.webkitFullscreenEnabled ||
            document.mozFullScreenEnabled ||
            document.msFullscreenEnabled;

        if (!isFullscreenSupported) {
            fullscreenToggle.style.display = 'none';
        } else {
            fullscreenToggle.addEventListener('click', function (e) {
                e.preventDefault();

                const isFullscreen = document.fullscreenElement ||
                    document.webkitFullscreenElement ||
                    document.mozFullScreenElement ||
                    document.msFullscreenElement;

                console.log('Fullscreen toggle clicked. Current state:', isFullscreen ? 'fullscreen' : 'normal');

                if (!isFullscreen) {
                    // Enter fullscreen mode
                    console.log('Entering fullscreen...');
                    const elem = document.documentElement;

                    const enterFullscreen = elem.requestFullscreen ||
                        elem.webkitRequestFullscreen ||
                        elem.mozRequestFullScreen ||
                        elem.msRequestFullscreen;

                    if (enterFullscreen) {
                        enterFullscreen.call(elem).then(() => {
                            console.log('Successfully entered fullscreen');
                        }).catch(err => {
                            console.error('Error entering fullscreen:', err);
                        });
                    }
                } else {
                    // Exit fullscreen mode
                    console.log('Exiting fullscreen...');

                    const exitFullscreen = document.exitFullscreen ||
                        document.webkitExitFullscreen ||
                        document.mozCancelFullScreen ||
                        document.msExitFullscreen;

                    if (exitFullscreen) {
                        exitFullscreen.call(document).then(() => {
                            console.log('Successfully exited fullscreen');
                        }).catch(err => {
                            console.error('Error exiting fullscreen:', err);
                        });
                    }
                }
            });

            // Listen for fullscreen changes (e.g., ESC key)
            const fullscreenEvents = ['fullscreenchange', 'webkitfullscreenchange', 'mozfullscreenchange', 'MSFullscreenChange'];

            fullscreenEvents.forEach(event => {
                document.addEventListener(event, function () {
                    const icon = fullscreenToggle.querySelector('i');
                    const isFullscreen = document.fullscreenElement ||
                        document.webkitFullscreenElement ||
                        document.mozFullScreenElement ||
                        document.msFullscreenElement;

                    console.log('Fullscreen state changed:', isFullscreen ? 'FULLSCREEN' : 'NORMAL');

                    if (isFullscreen) {
                        console.log('Changing icon to minimize');
                        icon.setAttribute('data-lucide', 'minimize');
                        fullscreenToggle.setAttribute('title', 'Fullscreen-ээс гарах');
                    } else {
                        console.log('Changing icon to maximize');
                        icon.setAttribute('data-lucide', 'maximize');
                        fullscreenToggle.setAttribute('title', 'Fullscreen');
                    }
                    lucide.createIcons();
                });
            });
        }
    }

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

