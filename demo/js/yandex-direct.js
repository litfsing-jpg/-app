// ===== YANDEX DIRECT MOCK DATA =====
const yandexMockData = {
    // Статистика за последние 30 дней
    stats: {
        impressions: 245380,
        clicks: 8752,
        cost: 127450.50,
        ctr: 3.57,
        avgCpc: 14.56,
        conversions: 284,
        conversionRate: 3.24
    },

    // Дневная статистика для графика
    dailyStats: [
        { date: '2024-01-01', impressions: 8200, clicks: 295, cost: 4250 },
        { date: '2024-01-02', impressions: 8450, clicks: 310, cost: 4480 },
        { date: '2024-01-03', impressions: 7980, clicks: 285, cost: 4120 },
        { date: '2024-01-04', impressions: 8900, clicks: 330, cost: 4820 },
        { date: '2024-01-05', impressions: 9100, clicks: 345, cost: 5020 },
        { date: '2024-01-06', impressions: 8650, clicks: 315, cost: 4590 },
        { date: '2024-01-07', impressions: 8200, clicks: 290, cost: 4230 },
        { date: '2024-01-08', impressions: 8500, clicks: 305, cost: 4450 },
        { date: '2024-01-09', impressions: 8300, clicks: 298, cost: 4340 },
        { date: '2024-01-10', impressions: 8700, clicks: 320, cost: 4680 },
        { date: '2024-01-11', impressions: 9200, clicks: 350, cost: 5100 },
        { date: '2024-01-12', impressions: 8950, clicks: 340, cost: 4950 },
        { date: '2024-01-13', impressions: 8400, clicks: 300, cost: 4380 },
        { date: '2024-01-14', impressions: 8100, clicks: 285, cost: 4150 },
        { date: '2024-01-15', impressions: 8600, clicks: 310, cost: 4520 },
        { date: '2024-01-16', impressions: 8800, clicks: 325, cost: 4750 },
        { date: '2024-01-17', impressions: 8500, clicks: 305, cost: 4450 },
        { date: '2024-01-18', impressions: 8900, clicks: 330, cost: 4820 },
        { date: '2024-01-19', impressions: 9000, clicks: 340, cost: 4970 },
        { date: '2024-01-20', impressions: 8700, clicks: 315, cost: 4600 },
        { date: '2024-01-21', impressions: 8300, clicks: 295, cost: 4310 },
        { date: '2024-01-22', impressions: 8600, clicks: 310, cost: 4530 },
        { date: '2024-01-23', impressions: 8950, clicks: 335, cost: 4890 },
        { date: '2024-01-24', impressions: 9100, clicks: 345, cost: 5050 },
        { date: '2024-01-25', impressions: 8800, clicks: 325, cost: 4750 },
        { date: '2024-01-26', impressions: 8500, clicks: 305, cost: 4450 },
        { date: '2024-01-27', impressions: 8700, clicks: 320, cost: 4680 },
        { date: '2024-01-28', impressions: 8900, clicks: 335, cost: 4900 },
        { date: '2024-01-29', impressions: 9200, clicks: 350, cost: 5120 },
        { date: '2024-01-30', impressions: 8650, clicks: 315, cost: 4600 }
    ],

    // Кампании
    campaigns: [
        {
            id: 123456,
            name: 'Мастер Компания - Основная кампания',
            status: 'ON',
            impressions: 125480,
            clicks: 4520,
            ctr: 3.60,
            cost: 65870.25,
            avgCpc: 14.57,
            conversions: 145,
            conversionRate: 3.21
        },
        {
            id: 123457,
            name: 'Ретаргетинг - Возврат клиентов',
            status: 'ON',
            impressions: 45290,
            clicks: 1680,
            ctr: 3.71,
            cost: 24560.80,
            avgCpc: 14.62,
            conversions: 58,
            conversionRate: 3.45
        },
        {
            id: 123458,
            name: 'Поисковая реклама - Москва',
            status: 'ON',
            impressions: 52340,
            clicks: 1890,
            ctr: 3.61,
            cost: 27490.50,
            avgCpc: 14.55,
            conversions: 62,
            conversionRate: 3.28
        },
        {
            id: 123459,
            name: 'РСЯ - Широкая аудитория',
            status: 'SUSPENDED',
            impressions: 18270,
            clicks: 492,
            ctr: 2.69,
            cost: 7158.95,
            avgCpc: 14.55,
            conversions: 15,
            conversionRate: 3.05
        },
        {
            id: 123460,
            name: 'Брендовая кампания',
            status: 'ON',
            impressions: 4000,
            clicks: 170,
            ctr: 4.25,
            cost: 2370.00,
            avgCpc: 13.94,
            conversions: 4,
            conversionRate: 2.35
        }
    ]
};

// ===== YANDEX DIRECT FUNCTIONS =====

function initYandexDirect() {
    // Проверяем есть ли токен (для демо всегда показываем данные)
    const hasToken = true; // В реальности: localStorage.getItem('yandex_direct_token')

    if (hasToken) {
        loadYandexData();
        initYandexChart();
        initYandexControls();
    } else {
        showYandexSetupNotice();
    }
}

async function loadYandexData() {
    // API URL - автоматически определяем backend
    // Для локальной разработки используем FastAPI backend
    // Для Vercel production используем serverless functions
    const isLocalDev = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    const API_BASE_URL = isLocalDev ? 'http://localhost:8000/api/yandex-direct' : '/api';

    try {
        // Показываем индикатор загрузки
        showLoadingIndicator();

        // Загружаем реальные данные из API
        const [statsResponse, campaignsResponse] = await Promise.all([
            fetch(`${API_BASE_URL}/stats`),
            fetch(`${API_BASE_URL}/campaigns`)
        ]);

        if (statsResponse.ok && campaignsResponse.ok) {
            const statsData = await statsResponse.json();
            const campaignsData = await campaignsResponse.json();

            // Проверяем формат ответа (разные для local и Vercel)
            let stats, campaigns;

            if (statsData.success) {
                // Vercel serverless format
                stats = {
                    impressions: statsData.stats.total_impressions || 0,
                    clicks: statsData.stats.total_clicks || 0,
                    cost: statsData.stats.total_cost || 0,
                    ctr: statsData.stats.avg_ctr || 0,
                    avgCpc: statsData.stats.avg_cpc || 0,
                    conversions: statsData.stats.total_conversions || 0,
                    conversionRate: statsData.stats.conversion_rate || 0
                };
            } else {
                // FastAPI format (local development)
                stats = {
                    impressions: statsData.total_impressions || 0,
                    clicks: statsData.total_clicks || 0,
                    cost: statsData.total_cost || 0,
                    ctr: statsData.avg_ctr || 0,
                    avgCpc: statsData.avg_cpc || 0,
                    conversions: statsData.total_conversions || 0,
                    conversionRate: statsData.conversion_rate || 0
                };
            }

            // Преобразуем кампании из Yandex Direct формата
            const campaignsArray = campaignsData.success ? campaignsData.campaigns : campaignsData.campaigns || [];
            campaigns = campaignsArray.map(c => ({
                id: c.Id,
                name: c.Name,
                status: c.Status,
                impressions: c.Statistics?.Impressions || 0,
                clicks: c.Statistics?.Clicks || 0,
                ctr: c.Statistics?.Ctr || 0,
                cost: c.Statistics?.Cost || 0,
                avgCpc: c.Statistics?.AvgCpc || 0,
                conversions: c.Statistics?.Conversions || 0,
                conversionRate: c.Statistics?.ConversionRate || 0
            }));

            updateYandexStats(stats);
            updateYandexTable(campaigns);
            hideLoadingIndicator();

            console.log(`✅ Данные загружены из Yandex Direct API (${isLocalDev ? 'Local' : 'Vercel'})`);
            return;
        }

        // Если API не отвечает, используем mock данные
        throw new Error('API не доступен');

    } catch (error) {
        console.warn('⚠️ Не удалось загрузить данные из API, используются демо-данные:', error.message);
        hideLoadingIndicator();

        // Fallback к mock данным
        updateYandexStats(yandexMockData.stats);
        updateYandexTable(yandexMockData.campaigns);
    }
}

function updateYandexStats(stats) {
    document.getElementById('ydImpressions').textContent = formatNumber(stats.impressions);
    document.getElementById('ydClicks').textContent = formatNumber(stats.clicks);
    document.getElementById('ydCost').textContent = formatNumber(stats.cost) + ' ₽';
    document.getElementById('ydCtr').textContent = stats.ctr + '%';

    // Добавляем изменения (для демо случайные)
    const changes = {
        impressions: '+12.5%',
        clicks: '+8.3%',
        cost: '+15.2%',
        ctr: '-1.2%'
    };

    updateStatChange('ydImpressionsChange', changes.impressions);
    updateStatChange('ydClicksChange', changes.clicks);
    updateStatChange('ydCostChange', changes.cost);
    updateStatChange('ydCtrChange', changes.ctr);
}

function updateStatChange(elementId, changeText) {
    const element = document.getElementById(elementId);
    if (!element) return;

    const isPositive = changeText.startsWith('+');
    const isNegative = changeText.startsWith('-');

    element.className = 'stat-change';
    if (isPositive) {
        element.classList.add('positive');
        element.innerHTML = `<i class="fas fa-arrow-up"></i> ${changeText}`;
    } else if (isNegative) {
        element.classList.add('negative');
        element.innerHTML = `<i class="fas fa-arrow-down"></i> ${changeText}`;
    } else {
        element.innerHTML = `<i class="fas fa-minus"></i> ${changeText}`;
    }
}

function updateYandexTable(campaigns) {
    const tbody = document.getElementById('yandexTableBody');
    if (!tbody) return;

    tbody.innerHTML = campaigns.map(campaign => `
        <tr>
            <td>${campaign.id}</td>
            <td><strong>${campaign.name}</strong></td>
            <td><span class="status-badge ${getStatusClass(campaign.status)}">${getStatusText(campaign.status)}</span></td>
            <td>${formatNumber(campaign.impressions)}</td>
            <td>${formatNumber(campaign.clicks)}</td>
            <td>${campaign.ctr}%</td>
            <td>${formatNumber(campaign.cost)} ₽</td>
            <td>${campaign.avgCpc} ₽</td>
            <td>${campaign.conversions}</td>
            <td>${campaign.conversionRate}%</td>
        </tr>
    `).join('');
}

function getStatusClass(status) {
    const statusMap = {
        'ON': 'active',
        'OFF': 'stopped',
        'SUSPENDED': 'paused'
    };
    return statusMap[status] || 'stopped';
}

function getStatusText(status) {
    const textMap = {
        'ON': 'Активна',
        'OFF': 'Остановлена',
        'SUSPENDED': 'Приостановлена'
    };
    return textMap[status] || status;
}

function initYandexChart() {
    const ctx = document.getElementById('yandexChart');
    if (!ctx) return;

    const dailyData = yandexMockData.dailyStats;

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: dailyData.map(d => formatDate(d.date)),
            datasets: [
                {
                    label: 'Показы',
                    data: dailyData.map(d => d.impressions),
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    yAxisID: 'y',
                    tension: 0.4
                },
                {
                    label: 'Клики',
                    data: dailyData.map(d => d.clicks),
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    yAxisID: 'y',
                    tension: 0.4
                },
                {
                    label: 'Расход (₽)',
                    data: dailyData.map(d => d.cost),
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    yAxisID: 'y1',
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    labels: {
                        color: '#94a3b8'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += formatNumber(context.parsed.y);
                                if (context.dataset.label.includes('Расход')) {
                                    label += ' ₽';
                                }
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    ticks: {
                        color: '#94a3b8'
                    },
                    grid: {
                        color: '#334155'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    ticks: {
                        color: '#94a3b8',
                        callback: function(value) {
                            return value + ' ₽';
                        }
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                },
                x: {
                    ticks: {
                        color: '#94a3b8'
                    },
                    grid: {
                        color: '#334155'
                    }
                }
            }
        }
    });
}

function initYandexControls() {
    // Кнопка обновления
    const refreshBtn = document.getElementById('refreshYandexBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            refreshBtn.innerHTML = '<i class="fas fa-sync fa-spin"></i> Обновляем...';
            refreshBtn.disabled = true;

            setTimeout(() => {
                loadYandexData();
                refreshBtn.innerHTML = '<i class="fas fa-sync"></i> Обновить';
                refreshBtn.disabled = false;
            }, 1500);
        });
    }

    // Кнопка экспорта
    const exportBtn = document.getElementById('exportYandexBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportYandexData);
    }

    // Поиск
    const searchInput = document.getElementById('ydSearchInput');
    if (searchInput) {
        searchInput.addEventListener('input', filterYandexTable);
    }

    // Фильтр по статусу
    const statusFilter = document.getElementById('ydStatusFilter');
    if (statusFilter) {
        statusFilter.addEventListener('change', filterYandexTable);
    }

    // Фильтр периода
    const timeFilter = document.getElementById('ydTimeFilter');
    if (timeFilter) {
        timeFilter.addEventListener('change', function() {
            // В реальности здесь будет запрос новых данных
            console.log('Изменён период:', this.value);
        });
    }
}

function filterYandexTable() {
    const searchTerm = document.getElementById('ydSearchInput').value.toLowerCase();
    const statusFilter = document.getElementById('ydStatusFilter').value;

    let filtered = yandexMockData.campaigns;

    // Фильтр по поиску
    if (searchTerm) {
        filtered = filtered.filter(c =>
            c.name.toLowerCase().includes(searchTerm) ||
            c.id.toString().includes(searchTerm)
        );
    }

    // Фильтр по статусу
    if (statusFilter !== 'all') {
        filtered = filtered.filter(c => c.status === statusFilter);
    }

    updateYandexTable(filtered);
}

function exportYandexData() {
    // Создаём CSV
    const campaigns = yandexMockData.campaigns;

    const headers = ['ID', 'Название', 'Статус', 'Показы', 'Клики', 'CTR', 'Расход', 'Ср. CPC', 'Конверсии', 'CR'];
    const rows = campaigns.map(c => [
        c.id,
        c.name,
        getStatusText(c.status),
        c.impressions,
        c.clicks,
        c.ctr,
        c.cost,
        c.avgCpc,
        c.conversions,
        c.conversionRate
    ]);

    let csvContent = headers.join(',') + '\n';
    rows.forEach(row => {
        csvContent += row.join(',') + '\n';
    });

    // Скачиваем файл
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    link.setAttribute('href', url);
    link.setAttribute('download', 'yandex_direct_report_' + new Date().toISOString().split('T')[0] + '.csv');
    link.style.visibility = 'hidden';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    alert('Отчёт экспортирован успешно!');
}

function showYandexSetupNotice() {
    const setupNotice = document.getElementById('ydSetupNotice');
    const table = document.querySelector('.yandex-campaigns-card');
    const chart = document.querySelector('.yandex-chart');
    const stats = document.querySelector('.yandex-stats-grid');

    if (setupNotice) setupNotice.style.display = 'block';
    if (table) table.style.display = 'none';
    if (chart) chart.style.display = 'none';
    if (stats) stats.style.display = 'none';

    // Кнопка подключения
    const connectBtn = document.getElementById('connectYandexBtn');
    if (connectBtn) {
        connectBtn.addEventListener('click', () => {
            alert('В реальной версии откроется окно настройки токена Яндекс.Директ');
        });
    }
}

// ===== HELPER FUNCTIONS =====

function formatNumber(num) {
    return new Intl.NumberFormat('ru-RU').format(num);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' });
}

function showLoadingIndicator() {
    const statsGrid = document.querySelector('.yandex-stats-grid');
    const table = document.querySelector('.yandex-campaigns-card');

    if (statsGrid) {
        statsGrid.style.opacity = '0.5';
        statsGrid.style.pointerEvents = 'none';
    }
    if (table) {
        table.style.opacity = '0.5';
        table.style.pointerEvents = 'none';
    }
}

function hideLoadingIndicator() {
    const statsGrid = document.querySelector('.yandex-stats-grid');
    const table = document.querySelector('.yandex-campaigns-card');

    if (statsGrid) {
        statsGrid.style.opacity = '1';
        statsGrid.style.pointerEvents = 'auto';
    }
    if (table) {
        table.style.opacity = '1';
        table.style.pointerEvents = 'auto';
    }
}

// ===== NAVIGATION UPDATE =====

// Обновляем навигацию чтобы она знала о странице Yandex Direct
const originalSwitchPage = switchPage;
window.switchPage = function(page) {
    originalSwitchPage(page);

    // Инициализируем Yandex Direct при переходе
    if (page === 'yandex-direct') {
        initYandexDirect();
    }
};
