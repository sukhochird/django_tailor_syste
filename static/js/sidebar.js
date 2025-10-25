// Sidebar toggle functionality
document.addEventListener('DOMContentLoaded', function () {
    const sidebarCollapseBtn = document.getElementById('sidebarCollapseBtn');
    const sidebarHeaderToggle = document.getElementById('sidebarHeaderToggle');
    const sidebar = document.getElementById('sidebar');
    let sidebarExpanded = true;

    // Function to toggle sidebar
    function toggleSidebar() {
        if (sidebarExpanded) {
            sidebar.classList.remove('sidebar-expanded');
            sidebar.classList.add('sidebar-collapsed');
        } else {
            sidebar.classList.remove('sidebar-collapsed');
            sidebar.classList.add('sidebar-expanded');
        }
        sidebarExpanded = !sidebarExpanded;

        // Update header chevron
        if (sidebarHeaderToggle) {
            const headerChevron = sidebarHeaderToggle.querySelector('.sidebar-chevron');
            if (headerChevron) {
                if (!sidebarExpanded) {
                    headerChevron.style.transform = 'rotate(0deg)';
                } else {
                    headerChevron.style.transform = 'rotate(180deg)';
                }
            }
        }

        lucide.createIcons(); // Reinitialize icons
    }

    // Toggle sidebar from footer collapse button
    if (sidebarCollapseBtn) {
        sidebarCollapseBtn.addEventListener('click', toggleSidebar);
    }

    // Toggle sidebar from header collapse button
    if (sidebarHeaderToggle) {
        sidebarHeaderToggle.addEventListener('click', toggleSidebar);
    }

    // Mobile toggle button
    const sidebarMobileToggle = document.getElementById('sidebarMobileToggle');
    if (sidebarMobileToggle) {
        sidebarMobileToggle.addEventListener('click', function () {
            if (sidebarExpanded) {
                sidebar.classList.remove('sidebar-collapsed');
                sidebar.classList.add('sidebar-expanded');
            } else {
                sidebar.classList.add('sidebar-expanded');
                sidebar.classList.remove('sidebar-collapsed');
            }
            sidebarExpanded = true;
        });
    }

    // Close sidebar on mobile when clicking outside
    document.addEventListener('click', function (event) {
        if (window.innerWidth < 768 && sidebarExpanded) {
            if (!sidebar.contains(event.target)) {
                sidebar.classList.add('sidebar-collapsed');
                sidebar.classList.remove('sidebar-expanded');
                sidebarExpanded = false;
            }
        }
    });

    // Handle window resize
    window.addEventListener('resize', function () {
        if (window.innerWidth < 768 && sidebarExpanded) {
            sidebar.classList.add('sidebar-collapsed');
            sidebar.classList.remove('sidebar-expanded');
            sidebarExpanded = false;
        }
    });

    // Initialize sidebar state based on screen size
    if (window.innerWidth < 768) {
        sidebar.classList.add('sidebar-collapsed');
        sidebar.classList.remove('sidebar-expanded');
        sidebarExpanded = false;
    }
});

