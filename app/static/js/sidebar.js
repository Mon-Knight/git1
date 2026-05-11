/**
 * AI World Engine - Sidebar JS
 * Handles sidebar group expand/collapse and active state detection.
 * v1.7.8.1
 */

(function () {
    'use strict';

    /**
     * Toggle the sidebar "世界项目" group expand/collapse.
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
     * On load: ensure world pages have the group expanded.
     */
    (function () {
        var path = window.location.pathname;
        // World-related paths
        if (/^\/worlds/.test(path) && !/^\/worlds$/.test(path)) {
            // On a specific world page - ensure expanded
            var subnav = document.querySelector('.sidebar-subnav');
            if (subnav) {
                subnav.classList.remove('collapsed');
            }
            var arrow = document.querySelector('.sidebar-arrow');
            if (arrow) {
                arrow.classList.add('open');
            }
        }
    })();
})();
