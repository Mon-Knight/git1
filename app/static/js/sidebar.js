/**
 * AI World Engine - Sidebar JS
 * Handles sidebar group expand/collapse, active state detection,
 * and settings category navigation.
 * v1.7.11.1
 */

(function () {
    'use strict';

    /**
     * Toggle a sidebar group expand/collapse.
     * Supports both "世界项目" and "设置" groups.
     */
    window.toggleSidebarGroup = function (event) {
        event.preventDefault();
        var toggle = event.currentTarget;
        var group = toggle.closest('.sidebar-group');
        if (!group) return;

        var subnav = group.querySelector('.sidebar-subnav');
        var arrow = toggle.querySelector('.sidebar-arrow');

        if (!subnav) return;

        var isCollapsed = subnav.classList.contains('collapsed');
        if (isCollapsed) {
            subnav.classList.remove('collapsed');
            if (arrow) arrow.classList.add('open');
        } else {
            subnav.classList.add('collapsed');
            if (arrow) arrow.classList.remove('open');
        }
    };

    /**
     * Handle settings category click from sidebar.
     * Shows the corresponding section and hides others.
     */
    window.showSettingsCategory = function (catName, event) {
        if (event) event.preventDefault();

        // Update sidebar active state
        var settingsLinks = document.querySelectorAll('.sidebar-sublink[data-nav="settings"]');
        settingsLinks.forEach(function (link) {
            link.classList.remove('active');
        });
        // Find the clicked link and activate it
        if (event && event.currentTarget) {
            event.currentTarget.classList.add('active');
        } else {
            // Find by data attribute fallback
            var targetLink = document.querySelector('.sidebar-sublink[onclick*="' + catName + '"]');
            if (targetLink) targetLink.classList.add('active');
        }

        // Show/hide sections in settings page
        var sections = document.querySelectorAll('.settings-cat-section');
        var found = false;
        sections.forEach(function (section) {
            if (section.getAttribute('data-settings-cat') === catName) {
                section.style.display = '';
                found = true;
            } else {
                section.style.display = 'none';
            }
        });

        // If no sections found (not on settings page), navigate to settings
        if (!found && catName) {
            window.location.href = '/settings/ai#' + catName;
            return;
        }

        // Update URL hash without reload
        if (window.history && window.history.replaceState) {
            var newHash = catName === 'ai' ? '' : '#' + catName;
            var newUrl = window.location.pathname + newHash;
            window.history.replaceState(null, '', newUrl);
        }

        // Scroll to top of content
        var mainContent = document.querySelector('.main-content');
        if (mainContent) {
            mainContent.scrollTop = 0;
        }
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    /**
     * On load: auto-expand correct groups and show settings category.
     */
    (function () {
        var path = window.location.pathname;
        var hash = window.location.hash;

        // World-related paths: ensure world group expanded
        if (/^\/worlds/.test(path)) {
            var worldSubnav = document.querySelector('.sidebar-group .sidebar-subnav');
            if (worldSubnav) {
                worldSubnav.classList.remove('collapsed');
            }
            var worldArrow = document.querySelector('.sidebar-group .sidebar-arrow');
            if (worldArrow) {
                worldArrow.classList.add('open');
            }
        }

        // Settings page: ensure settings group expanded and show correct category
        if (/^\/settings/.test(path)) {
            var settingsGroups = document.querySelectorAll('.sidebar-group');
            settingsGroups.forEach(function (group) {
                var toggle = group.querySelector('.sidebar-group-toggle');
                if (toggle && toggle.getAttribute('data-nav') === 'settings') {
                    var subnav = group.querySelector('.sidebar-subnav');
                    if (subnav) subnav.classList.remove('collapsed');
                    var arrow = group.querySelector('.sidebar-arrow');
                    if (arrow) arrow.classList.add('open');
                }
            });

            // Determine which category to show from hash
            var catName = 'ai'; // default
            if (hash) {
                var hashCat = hash.replace('#', '');
                var validCats = ['ai', 'display', 'desktop', 'storage', 'export', 'diagnostics', 'about'];
                if (validCats.indexOf(hashCat) !== -1) {
                    catName = hashCat;
                }
            }
            // Show the correct category on load
            var sections = document.querySelectorAll('.settings-cat-section');
            var hasSections = sections.length > 0;
            if (hasSections) {
                sections.forEach(function (section) {
                    if (section.getAttribute('data-settings-cat') === catName) {
                        section.style.display = '';
                    } else {
                        section.style.display = 'none';
                    }
                });
                // Highlight correct sidebar link
                var settingsLinks = document.querySelectorAll('.sidebar-sublink[data-nav="settings"]');
                settingsLinks.forEach(function (link) {
                    link.classList.remove('active');
                });
                var targetLink = document.querySelector('.sidebar-sublink[onclick*="' + catName + '"]');
                if (targetLink) targetLink.classList.add('active');
            }
        }
    })();
})();
