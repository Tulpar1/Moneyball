/* ============================================
   MONEYBALL - JAVASCRIPT UTILITIES
   ============================================ */

document.addEventListener('DOMContentLoaded', function () {
    initSidebar();
    initTooltips();
});

// === Sidebar Toggle ===
function initSidebar() {
    const menuToggle = document.querySelector('.menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.overlay');

    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', function () {
            sidebar.classList.toggle('active');
            if (overlay) overlay.classList.toggle('active');
        });

        if (overlay) {
            overlay.addEventListener('click', function () {
                sidebar.classList.remove('active');
                overlay.classList.remove('active');
            });
        }
    }

    // Mark active nav item
    const currentPath = window.location.pathname;
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        const href = item.getAttribute('href');
        if (href && currentPath.startsWith(href) && href !== '/') {
            item.classList.add('active');
        } else if (href === '/' && currentPath === '/dashboard') {
            item.classList.add('active');
        }
    });
}

// === Initialize Tooltips (Bootstrap) ===
function initTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(el => {
        new bootstrap.Tooltip(el);
    });
}

// === Format Number with Commas ===
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// === Format Currency (EUR) ===
function formatCurrency(value) {
    if (value >= 1000000) {
        return '€' + (value / 1000000).toFixed(1) + 'M';
    } else if (value >= 1000) {
        return '€' + (value / 1000).toFixed(0) + 'K';
    }
    return '€' + formatNumber(value);
}

// === Chart.js Default Configuration ===
const darkChartDefaults = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            labels: {
                color: '#8b949e',
                font: {
                    family: 'Inter, sans-serif'
                }
            }
        }
    },
    scales: {
        x: {
            ticks: { color: '#8b949e' },
            grid: { color: '#30363d' }
        },
        y: {
            ticks: { color: '#8b949e' },
            grid: { color: '#30363d' }
        }
    }
};

// === Create Donut Chart ===
function createDonutChart(canvasId, data, labels, colors) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderColor: '#161b22',
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#8b949e',
                        padding: 16,
                        font: {
                            family: 'Inter, sans-serif',
                            size: 12
                        }
                    }
                }
            },
            cutout: '65%'
        }
    });
}

// === Create Bar Chart ===
function createBarChart(canvasId, data, labels, color) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: color || '#58a6ff',
                borderRadius: 4
            }]
        },
        options: {
            ...darkChartDefaults,
            plugins: {
                legend: { display: false }
            }
        }
    });
}

// === Create Line Chart ===
function createLineChart(canvasId, data, labels, color) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                borderColor: color || '#3fb950',
                backgroundColor: (color || '#3fb950') + '20',
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointBackgroundColor: color || '#3fb950'
            }]
        },
        options: {
            ...darkChartDefaults,
            plugins: {
                legend: { display: false }
            }
        }
    });
}

// === Animate Value Counter ===
function animateValue(element, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const value = Math.floor(progress * (end - start) + start);
        element.textContent = formatNumber(value);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

// === Confirm Delete ===
function confirmDelete(message) {
    return confirm(message || 'Bu öğeyi silmek istediğinize emin misiniz?');
}
