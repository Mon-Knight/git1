/**
 * AI World Engine - Export Center JS
 * Handles export actions for both Web (browser download) and Desktop (file save) modes.
 * v1.7.8
 */

(function () {
    'use strict';

    var isDesktop = typeof window.pywebview !== 'undefined';

    // Update mode indicator on load
    var indicator = document.getElementById('export-mode-indicator');
    if (indicator) {
        indicator.textContent = isDesktop ? '选择保存位置 (桌面模式)' : '浏览器下载';
    }

    /**
     * Show result message in the result area.
     */
    function showResult(ok, message, details) {
        var el = document.getElementById('export-result');
        if (!el) return;
        el.style.display = 'block';
        el.style.background = ok ? 'rgba(0,212,170,0.08)' : 'rgba(255,100,100,0.1)';
        el.style.borderColor = ok ? 'var(--color-accent)' : '#ff6464';
        var html = '<strong>' + (ok ? '✅ 导出成功' : '❌ 导出失败') + '</strong>';
        html += '<p style="margin-top:0.5rem">' + message + '</p>';
        if (details) {
            html += '<p style="font-size:0.8rem;color:var(--color-text-muted);margin-top:0.25rem">' + details + '</p>';
        }
        el.innerHTML = html;
    }

    /**
     * Set button loading state.
     */
    function setLoading(btnId, loading) {
        var btn = document.getElementById(btnId);
        if (btn) {
            btn.disabled = loading;
            btn.textContent = loading ? '导出中...' : btn.getAttribute('data-original') || btn.textContent;
            if (!loading) {
                btn.setAttribute('data-original', btn.textContent);
            }
        }
    }

    /**
     * Handle desktop save flow: choose path, then POST to backend.
     */
    function desktopSave(exportUrl, defaultFilename, btnId) {
        setLoading(btnId, true);
        try {
            window.pywebview.api.choose_save_path(defaultFilename).then(function (result) {
                if (!result || result.cancelled) {
                    setLoading(btnId, false);
                    showResult(false, '已取消保存。', '');
                    return;
                }
                if (!result.ok) {
                    setLoading(btnId, false);
                    showResult(false, '选择路径失败：' + (result.error || '未知错误'), '');
                    return;
                }

                // Send to backend with save path
                var formData = new URLSearchParams();
                formData.append('save_path', result.path);

                var url = exportUrl + (exportUrl.includes('?') ? '&' : '?') + 'desktop_mode=1';
                fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: formData.toString()
                })
                .then(function (resp) {
                    setLoading(btnId, false);
                    if (!resp.ok) {
                        return resp.json().then(function (d) {
                            showResult(false, '导出失败', d.error || d.detail || 'HTTP ' + resp.status);
                        });
                    }
                    return resp.json().then(function (d) {
                        showResult(true, '已保存到：' + result.path, '文件类型：' + (d.export_type || 'JSON'));
                    });
                })
                .catch(function (err) {
                    setLoading(btnId, false);
                    showResult(false, '导出请求失败', err.message);
                });
            }).catch(function (err) {
                setLoading(btnId, false);
                showResult(false, '文件对话框错误', err.message || String(err));
            });
        } catch (e) {
            setLoading(btnId, false);
            showResult(false, '桌面模式不可用，请使用浏览器下载', e.message);
        }
    }

    /**
     * Web mode: trigger browser download via invisible link.
     */
    function webDownload(url, btnId) {
        setLoading(btnId, true);
        var a = document.createElement('a');
        a.href = url;
        a.download = '';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        setTimeout(function () {
            setLoading(btnId, false);
            showResult(true, '文件已开始下载。', '如未自动下载，请检查浏览器设置。');
        }, 500);
    }

    // ── Export functions ──

    window.exportWorld = function () {
        var select = document.getElementById('world-select');
        var worldId = select ? select.value : '';
        if (!worldId) {
            showResult(false, '请先选择一个世界。', '');
            return;
        }
        var url = '/worlds/' + worldId + '/export.json';
        if (isDesktop) {
            var worldName = select.options[select.selectedIndex].text;
            var filename = 'AIWorldEngine_world_' + worldName.replace(/[^a-zA-Z0-9\u4e00-\u9fff_-]/g, '_') + '.json';
            desktopSave(url, filename, 'btn-export-world');
        } else {
            webDownload(url, 'btn-export-world');
        }
    };

    window.exportBackup = function () {
        var url = '/data/export/backup';
        if (isDesktop) {
            var filename = 'AIWorldEngine_backup_' + new Date().toISOString().slice(0,10).replace(/-/g,'') + '.json';
            desktopSave(url, filename, 'btn-export-backup');
        } else {
            webDownload(url, 'btn-export-backup');
        }
    };

    window.exportAssets = function () {
        var select = document.getElementById('asset-world-select');
        var worldId = select ? select.value : '';
        if (!worldId) {
            showResult(false, '请先选择一个世界。', '');
            return;
        }
        var url = '/worlds/' + worldId + '/context/export';
        if (isDesktop) {
            var worldName = select.options[select.selectedIndex].text;
            var filename = 'AIWorldEngine_assets_' + worldName.replace(/[^a-zA-Z0-9\u4e00-\u9fff_-]/g, '_') + '.json';
            desktopSave(url, filename, 'btn-export-assets');
        } else {
            webDownload(url, 'btn-export-assets');
        }
    };

})();
