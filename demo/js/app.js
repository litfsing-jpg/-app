// ===== MOCK DATA =====
const mockData = {
    activities: [
        {
            icon: 'fa-video',
            iconBg: '#3b82f6',
            title: 'New video published on YouTube',
            meta: '@TechTalks • 2 hours ago',
            platform: 'youtube'
        },
        {
            icon: 'fa-heart',
            iconBg: '#ec4899',
            title: 'TikTok video reached 10K likes',
            meta: '@FinanceTips • 4 hours ago',
            platform: 'tiktok'
        },
        {
            icon: 'fa-twitter',
            iconBg: '#1da1f2',
            title: 'Twitter thread got 500 retweets',
            meta: '@BusinessGrowth • 6 hours ago',
            platform: 'twitter'
        },
        {
            icon: 'fa-dollar-sign',
            iconBg: '#10b981',
            title: 'New affiliate sale: $150',
            meta: 'Stripe • 8 hours ago',
            platform: 'stripe'
        },
        {
            icon: 'fa-users',
            iconBg: '#8b5cf6',
            title: 'LinkedIn post reached 5K views',
            meta: '@ProfessionalTips • 12 hours ago',
            platform: 'linkedin'
        }
    ],

    content: [
        {
            id: 1,
            title: '5 Ways to Boost Your Productivity',
            platform: 'YouTube',
            icon: 'fa-youtube',
            iconColor: '#ff0000',
            status: 'published',
            views: '12.5K',
            engagement: '8.2%',
            date: '2024-01-15'
        },
        {
            id: 2,
            title: 'Financial Freedom in 2024',
            platform: 'TikTok',
            icon: 'fa-tiktok',
            iconColor: '#000000',
            status: 'published',
            views: '45.2K',
            engagement: '12.5%',
            date: '2024-01-14'
        },
        {
            id: 3,
            title: 'Thread: How to Scale Your Business',
            platform: 'Twitter',
            icon: 'fa-twitter',
            iconColor: '#1da1f2',
            status: 'published',
            views: '8.9K',
            engagement: '6.7%',
            date: '2024-01-13'
        },
        {
            id: 4,
            title: 'Leadership Tips for 2024',
            platform: 'LinkedIn',
            icon: 'fa-linkedin',
            iconColor: '#0077b5',
            status: 'draft',
            views: '0',
            engagement: '0%',
            date: '2024-01-16'
        },
        {
            id: 5,
            title: 'Crypto Investment Guide',
            platform: 'YouTube',
            icon: 'fa-youtube',
            iconColor: '#ff0000',
            status: 'published',
            views: '28.3K',
            engagement: '9.8%',
            date: '2024-01-12'
        },
        {
            id: 6,
            title: 'Morning Routine Hacks',
            platform: 'TikTok',
            icon: 'fa-tiktok',
            iconColor: '#000000',
            status: 'published',
            views: '67.8K',
            engagement: '15.2%',
            date: '2024-01-11'
        }
    ],

    accounts: [
        {
            id: 1,
            username: '@TechTalks',
            platform: 'YouTube',
            icon: 'fa-youtube',
            iconColor: '#ff0000',
            followers: '125K',
            posts: 247,
            engagement: '8.5%',
            status: 'active'
        },
        {
            id: 2,
            username: '@FinanceTips',
            platform: 'TikTok',
            icon: 'fa-tiktok',
            iconColor: '#000000',
            followers: '89K',
            posts: 412,
            engagement: '12.3%',
            status: 'active'
        },
        {
            id: 3,
            username: '@BusinessGrowth',
            platform: 'Twitter',
            icon: 'fa-twitter',
            iconColor: '#1da1f2',
            followers: '45K',
            posts: 1203,
            engagement: '6.7%',
            status: 'active'
        },
        {
            id: 4,
            username: '@ProfessionalTips',
            platform: 'LinkedIn',
            icon: 'fa-linkedin',
            iconColor: '#0077b5',
            followers: '32K',
            posts: 189,
            engagement: '9.2%',
            status: 'active'
        },
        {
            id: 5,
            username: '@CryptoInsights',
            platform: 'YouTube',
            icon: 'fa-youtube',
            iconColor: '#ff0000',
            followers: '67K',
            posts: 156,
            engagement: '7.8%',
            status: 'active'
        },
        {
            id: 6,
            username: '@HealthyLife',
            platform: 'TikTok',
            icon: 'fa-tiktok',
            iconColor: '#000000',
            followers: '103K',
            posts: 523,
            engagement: '14.1%',
            status: 'inactive'
        }
    ],

    campaigns: [
        {
            id: 1,
            title: 'Q1 2024 Growth Campaign',
            description: 'Focus on YouTube and TikTok growth',
            startDate: '2024-01-01',
            endDate: '2024-03-31',
            budget: '$5,000',
            spent: '$3,240',
            conversions: 127,
            revenue: '$12,450',
            roi: '284%'
        },
        {
            id: 2,
            title: 'LinkedIn Professional Series',
            description: 'B2B content marketing campaign',
            startDate: '2024-01-15',
            endDate: '2024-02-28',
            budget: '$2,500',
            spent: '$1,680',
            conversions: 45,
            revenue: '$4,230',
            roi: '152%'
        },
        {
            id: 3,
            title: 'Twitter Engagement Boost',
            description: 'Increase Twitter presence and followers',
            startDate: '2024-01-10',
            endDate: '2024-02-10',
            budget: '$1,000',
            spent: '$780',
            conversions: 23,
            revenue: '$1,890',
            roi: '142%'
        }
    ],

    jarvisResponses: {
        'Show me today\'s performance': 'Based on today\'s data:\n\n📊 Views: 45,230 (+12% vs yesterday)\n💰 Revenue: $890\n📈 Engagement Rate: 9.2%\n🎯 Top Platform: TikTok (67% of traffic)\n\nYour TikTok video "Morning Routine Hacks" is performing exceptionally well with 15.2% engagement rate!',

        'Which platform is performing best?': 'TikTok is your top performer!\n\n🥇 TikTok: 103K followers, 14.1% avg engagement\n🥈 YouTube: 125K followers, 8.5% avg engagement\n🥉 LinkedIn: 32K followers, 9.2% avg engagement\n\nRecommendation: Double down on TikTok short-form content. Consider repurposing top TikTok content for YouTube Shorts.',

        'Generate content ideas': 'Here are 5 trending content ideas for your niches:\n\n1. 💼 "5 AI Tools Replacing Traditional Jobs in 2024"\n2. 💰 "How I Made $10K in Passive Income (Step-by-Step)"\n3. 🧠 "Psychology Tricks Used by Top CEOs"\n4. 📈 "Crypto Portfolio Strategy for Beginners"\n5. ⏰ "Morning Routine of Millionaires"\n\nThese topics are trending with high engagement rates in your niche.',

        'Show revenue breakdown': 'Revenue Breakdown (Last 30 Days):\n\n💵 Total: $12,450\n\nBy Source:\n🔗 Affiliate Sales: $8,920 (71.6%)\n💳 Course Sales: $2,340 (18.8%)\n🎯 Sponsored Content: $1,190 (9.6%)\n\nTop Performing Affiliate:\n"Financial Freedom Course" - $4,230 (47.4% of affiliate revenue)\n\nRecommendation: Create more content around financial education to boost this top performer!'
    }
};

// ===== GLOBAL STATE =====
let currentPage = 'overview';
let charts = {};

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function() {
    initNavigation();
    initMobileMenu();
    initCharts();
    populateActivities();
    populateContent();
    populateAccounts();
    populateCampaigns();
    initJarvis();
    initButtons();
});

// ===== NAVIGATION =====
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');

    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();

            // Update active state
            navItems.forEach(nav => nav.classList.remove('active'));
            this.classList.add('active');

            // Switch page
            const page = this.dataset.page;
            switchPage(page);
        });
    });
}

function switchPage(page) {
    currentPage = page;

    // Hide all pages
    const pages = document.querySelectorAll('.page');
    pages.forEach(p => p.classList.remove('active'));

    // Show selected page
    const selectedPage = document.getElementById(`${page}-page`);
    if (selectedPage) {
        selectedPage.classList.add('active');
    }

    // Update page title
    const titles = {
        'overview': 'Dashboard Overview',
        'content': 'Content Management',
        'accounts': 'Social Media Accounts',
        'analytics': 'Analytics Dashboard',
        'campaigns': 'Marketing Campaigns',
        'jarvis': 'Jarvis AI Assistant'
    };

    document.getElementById('pageTitle').textContent = titles[page] || 'Dashboard';
}

// ===== MOBILE MENU =====
function initMobileMenu() {
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const sidebar = document.querySelector('.sidebar');

    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            sidebar.classList.toggle('open');
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function(e) {
            if (window.innerWidth <= 768) {
                if (!sidebar.contains(e.target) && !mobileMenuBtn.contains(e.target)) {
                    sidebar.classList.remove('open');
                }
            }
        });
    }
}

// ===== CHARTS =====
function initCharts() {
    // Revenue Chart
    const revenueCtx = document.getElementById('revenueChart');
    if (revenueCtx) {
        charts.revenue = new Chart(revenueCtx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Revenue',
                    data: [1200, 1900, 1500, 2100, 1800, 2400, 2200],
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: '#94a3b8',
                            callback: function(value) {
                                return '$' + value;
                            }
                        },
                        grid: {
                            color: '#334155'
                        }
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

    // Platform Chart
    const platformCtx = document.getElementById('platformChart');
    if (platformCtx) {
        charts.platform = new Chart(platformCtx, {
            type: 'doughnut',
            data: {
                labels: ['YouTube', 'TikTok', 'Twitter', 'LinkedIn'],
                datasets: [{
                    data: [35, 40, 15, 10],
                    backgroundColor: [
                        '#ff0000',
                        '#000000',
                        '#1da1f2',
                        '#0077b5'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#94a3b8',
                            padding: 15
                        }
                    }
                }
            }
        });
    }

    // Analytics Chart
    const analyticsCtx = document.getElementById('analyticsChart');
    if (analyticsCtx) {
        charts.analytics = new Chart(analyticsCtx, {
            type: 'bar',
            data: {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                datasets: [
                    {
                        label: 'Views',
                        data: [450000, 520000, 480000, 610000],
                        backgroundColor: 'rgba(99, 102, 241, 0.8)'
                    },
                    {
                        label: 'Engagement',
                        data: [38000, 45000, 42000, 58000],
                        backgroundColor: 'rgba(139, 92, 246, 0.8)'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#94a3b8'
                        }
                    }
                },
                scales: {
                    y: {
                        ticks: {
                            color: '#94a3b8'
                        },
                        grid: {
                            color: '#334155'
                        }
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
}

// ===== POPULATE DATA =====
function populateActivities() {
    const activityList = document.getElementById('activityList');
    if (!activityList) return;

    activityList.innerHTML = mockData.activities.map(activity => `
        <div class="activity-item">
            <div class="activity-icon" style="background: ${activity.iconBg};">
                <i class="fas ${activity.icon}" style="color: white;"></i>
            </div>
            <div class="activity-content">
                <div class="activity-title">${activity.title}</div>
                <div class="activity-meta">${activity.meta}</div>
            </div>
        </div>
    `).join('');
}

function populateContent() {
    const contentGrid = document.getElementById('contentGrid');
    if (!contentGrid) return;

    contentGrid.innerHTML = mockData.content.map(content => `
        <div class="content-card">
            <div class="content-image">
                <i class="fab ${content.icon}"></i>
            </div>
            <div class="content-body">
                <div class="content-title">${content.title}</div>
                <div class="content-meta">
                    <span><i class="fas fa-calendar"></i> ${content.date}</span>
                    <span><i class="fas fa-eye"></i> ${content.views}</span>
                </div>
                <span class="content-status ${content.status}">${content.status}</span>
            </div>
        </div>
    `).join('');
}

function populateAccounts() {
    const accountsGrid = document.getElementById('accountsGrid');
    if (!accountsGrid) return;

    accountsGrid.innerHTML = mockData.accounts.map(account => `
        <div class="account-card">
            <div class="account-header">
                <div class="account-avatar" style="background: ${account.iconColor};">
                    <i class="fab ${account.icon}" style="color: white;"></i>
                </div>
                <div class="account-info">
                    <h4>${account.username}</h4>
                    <div class="account-platform">${account.platform}</div>
                </div>
            </div>
            <div class="account-stats">
                <div class="account-stat">
                    <div class="account-stat-value">${account.followers}</div>
                    <div class="account-stat-label">Followers</div>
                </div>
                <div class="account-stat">
                    <div class="account-stat-value">${account.posts}</div>
                    <div class="account-stat-label">Posts</div>
                </div>
            </div>
            <div class="account-status ${account.status}">
                <span class="status-dot"></span>
                ${account.status}
            </div>
        </div>
    `).join('');
}

function populateCampaigns() {
    const campaignsGrid = document.getElementById('campaignsGrid');
    if (!campaignsGrid) return;

    campaignsGrid.innerHTML = mockData.campaigns.map(campaign => `
        <div class="campaign-card">
            <div class="campaign-info">
                <div class="campaign-title">${campaign.title}</div>
                <div class="campaign-meta">
                    ${campaign.startDate} - ${campaign.endDate}
                </div>
                <div class="campaign-stats">
                    <div class="campaign-stat">
                        <div class="campaign-stat-label">Budget</div>
                        <div class="campaign-stat-value">${campaign.budget}</div>
                    </div>
                    <div class="campaign-stat">
                        <div class="campaign-stat-label">Spent</div>
                        <div class="campaign-stat-value">${campaign.spent}</div>
                    </div>
                    <div class="campaign-stat">
                        <div class="campaign-stat-label">Conversions</div>
                        <div class="campaign-stat-value">${campaign.conversions}</div>
                    </div>
                    <div class="campaign-stat">
                        <div class="campaign-stat-label">Revenue</div>
                        <div class="campaign-stat-value">${campaign.revenue}</div>
                    </div>
                    <div class="campaign-stat">
                        <div class="campaign-stat-label">ROI</div>
                        <div class="campaign-stat-value">${campaign.roi}</div>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

// ===== JARVIS AI =====
function initJarvis() {
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const voiceBtn = document.getElementById('voiceBtn');
    const quickActionBtns = document.querySelectorAll('.quick-action-btn');

    // Send message
    if (sendBtn && chatInput) {
        sendBtn.addEventListener('click', () => sendMessage());
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    }

    // Voice button
    if (voiceBtn) {
        voiceBtn.addEventListener('click', () => {
            voiceBtn.classList.toggle('recording');
            if (voiceBtn.classList.contains('recording')) {
                // Simulate voice recording
                setTimeout(() => {
                    voiceBtn.classList.remove('recording');
                    addMessage('user', 'Show me today\'s performance');
                    setTimeout(() => respondToMessage('Show me today\'s performance'), 1000);
                }, 3000);
            }
        });
    }

    // Quick actions
    quickActionBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const query = btn.dataset.query;
            addMessage('user', query);
            setTimeout(() => respondToMessage(query), 1000);
        });
    });
}

function sendMessage() {
    const chatInput = document.getElementById('chatInput');
    const message = chatInput.value.trim();

    if (!message) return;

    addMessage('user', message);
    chatInput.value = '';

    setTimeout(() => respondToMessage(message), 1000);
}

function addMessage(type, text) {
    const chatContainer = document.getElementById('chatContainer');

    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${type}`;

    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas ${type === 'user' ? 'fa-user' : 'fa-robot'}"></i>
        </div>
        <div class="message-content">
            <p>${text.replace(/\n/g, '<br>')}</p>
        </div>
    `;

    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function respondToMessage(message) {
    let response = mockData.jarvisResponses[message];

    if (!response) {
        response = `I understand you're asking about "${message}". As this is a demo, I have pre-programmed responses for:\n\n- Show me today's performance\n- Which platform is performing best?\n- Generate content ideas\n- Show revenue breakdown\n\nIn the full version, I can analyze real-time data and provide insights on any aspect of your business!`;
    }

    addMessage('assistant', response);
}

// ===== BUTTON HANDLERS =====
function initButtons() {
    const generateContentBtn = document.getElementById('generateContentBtn');
    const addAccountBtn = document.getElementById('addAccountBtn');
    const createCampaignBtn = document.getElementById('createCampaignBtn');
    const notificationBtn = document.getElementById('notificationBtn');
    const settingsBtn = document.getElementById('settingsBtn');

    if (generateContentBtn) {
        generateContentBtn.addEventListener('click', () => {
            alert('Content generation feature coming soon! This will use AI to generate content ideas and drafts.');
        });
    }

    if (addAccountBtn) {
        addAccountBtn.addEventListener('click', () => {
            alert('Add account feature coming soon! Connect your social media accounts here.');
        });
    }

    if (createCampaignBtn) {
        createCampaignBtn.addEventListener('click', () => {
            alert('Create campaign feature coming soon! Set up automated marketing campaigns.');
        });
    }

    if (notificationBtn) {
        notificationBtn.addEventListener('click', () => {
            alert('Notifications:\n\n• New follower milestone reached!\n• Content scheduled for tomorrow\n• Affiliate payment received');
        });
    }

    if (settingsBtn) {
        settingsBtn.addEventListener('click', () => {
            alert('Settings feature coming soon! Configure your preferences and integrations.');
        });
    }
}
