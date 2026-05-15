/**
 * AI World Engine - Sidebar JS
 * Handles sidebar group expand/collapse, active state detection,
 * and settings category navigation.
 * v2.0.1 — 小说工程核心化：支持多独立分组展开/折叠
 */

(function () {
    'use strict';

    /**
     * Toggle a sidebar group expand/collapse.
     * v2.0.1: Supports all sidebar groups (小说工程, 世界设定, 创作资产, AI 推演, 质量检查, 设置).
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
     * v2.0.1: On load — auto-expand the correct sidebar group based on current URL.
     */
    (function () {
        var path = window.location.pathname;
        var hash = window.location.hash;

        // Determine which group to expand based on path
        var expandNav = null;
        if (/^\/worlds\/\d+\/novel/.test(path)) expandNav = 'novel';
        else if (/^\/worlds\/\d+\/context/.test(path)) expandNav = 'assets';
        else if (/^\/worlds\/\d+\/simulation/.test(path) || /^\/worlds\/\d+\/records/.test(path) || /^\/worlds\/\d+\/branches/.test(path)) expandNav = 'simulation';
        else if (/^\/worlds\/\d+\/checks/.test(path)) expandNav = 'checks';
        else if (/^\/worlds/.test(path)) expandNav = 'worlds';
        else if (/^\/settings/.test(path)) expandNav = 'settings';

        if (expandNav) {
            var groups = document.querySelectorAll('.sidebar-group');
            groups.forEach(function (group) {
                var toggle = group.querySelector('.sidebar-group-toggle');
                if (toggle && toggle.getAttribute('data-nav') === expandNav) {
                    var subnav = group.querySelector('.sidebar-subnav');
                    if (subnav) subnav.classList.remove('collapsed');
                    var arrow = group.querySelector('.sidebar-arrow');
                    if (arrow) arrow.classList.add('open');
                }
            });
        }

        // Settings page: show correct category section
        if (/^\/settings/.test(path) && hash) {
            var catName = hash.replace('#', '');
            if (catName && typeof showSettingsCategory === 'function') {
                setTimeout(function () {
                    showSettingsCategory(catName);
                }, 0);
            }
        }
})();
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
