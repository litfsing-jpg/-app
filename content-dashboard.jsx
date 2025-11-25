import React, { useState, useEffect } from 'react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { LayoutDashboard, Users, FileText, BarChart3, Filter, Target, Mic, Settings, Play, Plus, Sparkles, Send, Volume2, TrendingUp, DollarSign, Eye, AlertCircle, CheckCircle, Clock, Loader2, X, ChevronRight, Zap, Bot } from 'lucide-react';

// Моковые данные для демонстрации
const initialAccounts = [
  { id: 1, platform: 'tiktok', username: '@productivity_hacks', followers: 45200, status: 'active', health: 95, posts_today: 3 },
  { id: 2, platform: 'tiktok', username: '@money_mindset', followers: 32100, status: 'active', health: 88, posts_today: 2 },
  { id: 3, platform: 'twitter', username: '@tech_insights', followers: 18500, status: 'active', health: 92, posts_today: 5 },
  { id: 4, platform: 'linkedin', username: 'Alex Growth', followers: 8200, status: 'warming_up', health: 75, posts_today: 1 },
  { id: 5, platform: 'youtube', username: '@shorts_viral', followers: 12400, status: 'active', health: 90, posts_today: 2 },
];

const initialContent = [
  { id: 1, title: '5 утренних привычек миллионеров', platform: 'tiktok', status: 'published', views: 45000, likes: 3200 },
  { id: 2, title: 'Почему 90% людей не богатеют', platform: 'tiktok', status: 'scheduled', views: 0, likes: 0 },
  { id: 3, title: 'Thread: Как я заработал первый $1000 онлайн', platform: 'twitter', status: 'published', views: 12000, likes: 890 },
  { id: 4, title: 'Секрет продуктивности Илона Маска', platform: 'youtube', status: 'ready', views: 0, likes: 0 },
];

const weekData = [
  { day: 'Пн', views: 12000, leads: 24, revenue: 150 },
  { day: 'Вт', views: 18000, leads: 35, revenue: 220 },
  { day: 'Ср', views: 15000, leads: 28, revenue: 180 },
  { day: 'Чт', views: 22000, leads: 42, revenue: 350 },
  { day: 'Пт', views: 28000, leads: 55, revenue: 420 },
  { day: 'Сб', views: 35000, leads: 68, revenue: 580 },
  { day: 'Вс', views: 25000, leads: 48, revenue: 380 },
];

const platformColors = {
  tiktok: '#00f2ea',
  twitter: '#1da1f2',
  linkedin: '#0077b5',
  youtube: '#ff0000',
  telegram: '#0088cc'
};

const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#f97316'];

// Компонент навигации
const Sidebar = ({ currentPage, setCurrentPage }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'accounts', label: 'Аккаунты', icon: Users },
    { id: 'content', label: 'Контент', icon: FileText },
    { id: 'generate', label: 'Генерация', icon: Sparkles },
    { id: 'jarvis', label: 'Jarvis AI', icon: Bot },
    { id: 'analytics', label: 'Аналитика', icon: BarChart3 },
  ];

  return (
    <div className="w-64 bg-gray-900 min-h-screen p-4 flex flex-col">
      <div className="flex items-center gap-2 mb-8 px-2">
        <Zap className="w-8 h-8 text-indigo-500" />
        <span className="text-xl font-bold text-white">ContentAI</span>
      </div>
      
      <nav className="flex-1 space-y-1">
        {navItems.map(item => (
          <button
            key={item.id}
            onClick={() => setCurrentPage(item.id)}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
              currentPage === item.id 
                ? 'bg-indigo-600 text-white' 
                : 'text-gray-400 hover:bg-gray-800 hover:text-white'
            }`}
          >
            <item.icon className="w-5 h-5" />
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
      
      <div className="border-t border-gray-800 pt-4 mt-4">
        <div className="px-4 py-2 text-sm text-gray-500">
          🟢 Система активна
        </div>
      </div>
    </div>
  );
};

// Карточка статистики
const StatCard = ({ title, value, change, icon: Icon, color, subtitle }) => (
  <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
    <div className="flex items-start justify-between">
      <div className="flex-1">
        <p className="text-sm font-medium text-gray-500">{title}</p>
        <p className="text-2xl font-bold mt-1 text-gray-900">{value}</p>
        {change !== undefined && (
          <p className={`text-sm mt-1 flex items-center gap-1 ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            <TrendingUp className={`w-3 h-3 ${change < 0 ? 'rotate-180' : ''}`} />
            {change >= 0 ? '+' : ''}{change}%
          </p>
        )}
        {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
      </div>
      <div className={`p-3 rounded-xl ${color}`}>
        <Icon className="w-6 h-6 text-white" />
      </div>
    </div>
  </div>
);

// Dashboard страница
const DashboardPage = ({ accounts, content }) => {
  const totalFollowers = accounts.reduce((sum, a) => sum + a.followers, 0);
  const activeAccounts = accounts.filter(a => a.status === 'active').length;
  const publishedToday = content.filter(c => c.status === 'published').length;
  
  const platformData = accounts.reduce((acc, account) => {
    const existing = acc.find(p => p.name === account.platform);
    if (existing) {
      existing.value += account.followers;
    } else {
      acc.push({ name: account.platform, value: account.followers });
    }
    return acc;
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-500">Добро пожаловать в Content Automation System</p>
        </div>
        <div className="text-sm text-gray-500">
          Обновлено: {new Date().toLocaleTimeString('ru-RU')}
        </div>
      </div>

      {/* Статистика */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Всего подписчиков"
          value={totalFollowers.toLocaleString()}
          change={12}
          icon={Users}
          color="bg-blue-500"
        />
        <StatCard
          title="Опубликовано сегодня"
          value={publishedToday}
          icon={CheckCircle}
          color="bg-green-500"
          subtitle={`${activeAccounts} активных аккаунтов`}
        />
        <StatCard
          title="Доход за неделю"
          value="$2,280"
          change={18}
          icon={DollarSign}
          color="bg-purple-500"
        />
        <StatCard
          title="Новых лидов"
          value="300"
          change={24}
          icon={TrendingUp}
          color="bg-orange-500"
        />
      </div>

      {/* Графики */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <h3 className="text-lg font-semibold mb-4">Просмотры и доход</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={weekData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="day" stroke="#9ca3af" />
              <YAxis yAxisId="left" stroke="#9ca3af" />
              <YAxis yAxisId="right" orientation="right" stroke="#9ca3af" />
              <Tooltip 
                contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
              />
              <Line yAxisId="left" type="monotone" dataKey="views" stroke="#6366f1" strokeWidth={3} dot={false} name="Просмотры" />
              <Line yAxisId="right" type="monotone" dataKey="revenue" stroke="#10b981" strokeWidth={3} dot={false} name="Доход ($)" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <h3 className="text-lg font-semibold mb-4">Подписчики по платформам</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={platformData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={5}
                dataKey="value"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {platformData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Последний контент */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
        <h3 className="text-lg font-semibold mb-4">Последний контент</h3>
        <div className="space-y-3">
          {content.slice(0, 4).map(item => (
            <div key={item.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className={`w-2 h-2 rounded-full ${
                  item.status === 'published' ? 'bg-green-500' :
                  item.status === 'scheduled' ? 'bg-blue-500' : 'bg-yellow-500'
                }`} />
                <div>
                  <p className="font-medium text-gray-900">{item.title}</p>
                  <p className="text-sm text-gray-500">{item.platform}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm font-medium">{item.views.toLocaleString()} просмотров</p>
                <p className="text-xs text-gray-500">{item.likes.toLocaleString()} лайков</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Страница аккаунтов
const AccountsPage = ({ accounts }) => {
  const getPlatformIcon = (platform) => {
    const icons = {
      tiktok: '📱',
      twitter: '🐦',
      linkedin: '💼',
      youtube: '▶️',
      telegram: '✈️'
    };
    return icons[platform] || '📌';
  };

  const getStatusBadge = (status) => {
    const styles = {
      active: 'bg-green-100 text-green-700',
      warming_up: 'bg-yellow-100 text-yellow-700',
      paused: 'bg-gray-100 text-gray-700',
      shadowbanned: 'bg-red-100 text-red-700'
    };
    const labels = {
      active: 'Активен',
      warming_up: 'Прогрев',
      paused: 'Пауза',
      shadowbanned: 'Shadowban'
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status]}`}>
        {labels[status]}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Аккаунты</h1>
          <p className="text-gray-500">Управление социальными сетями</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors">
          <Plus className="w-4 h-4" />
          Добавить аккаунт
        </button>
      </div>

      <div className="grid gap-4">
        {accounts.map(account => (
          <div key={account.id} className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="text-3xl">{getPlatformIcon(account.platform)}</div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-gray-900">{account.username}</h3>
                    {getStatusBadge(account.status)}
                  </div>
                  <p className="text-sm text-gray-500 capitalize">{account.platform}</p>
                </div>
              </div>
              
              <div className="flex items-center gap-8">
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-900">{account.followers.toLocaleString()}</p>
                  <p className="text-xs text-gray-500">подписчиков</p>
                </div>
                
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-900">{account.posts_today}</p>
                  <p className="text-xs text-gray-500">постов сегодня</p>
                </div>
                
                <div className="w-24">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs text-gray-500">Health</span>
                    <span className="text-xs font-medium">{account.health}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        account.health >= 80 ? 'bg-green-500' :
                        account.health >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${account.health}%` }}
                    />
                  </div>
                </div>
                
                <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                  <ChevronRight className="w-5 h-5 text-gray-400" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Страница контента
const ContentPage = ({ content, setContent }) => {
  const getStatusBadge = (status) => {
    const config = {
      published: { bg: 'bg-green-100', text: 'text-green-700', label: 'Опубликован' },
      scheduled: { bg: 'bg-blue-100', text: 'text-blue-700', label: 'Запланирован' },
      ready: { bg: 'bg-yellow-100', text: 'text-yellow-700', label: 'Готов' },
      generating: { bg: 'bg-purple-100', text: 'text-purple-700', label: 'Генерация...' }
    };
    const c = config[status] || config.ready;
    return <span className={`px-2 py-1 rounded-full text-xs font-medium ${c.bg} ${c.text}`}>{c.label}</span>;
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Контент</h1>
          <p className="text-gray-500">Управление созданным контентом</p>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Название</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Платформа</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Статус</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Просмотры</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Действия</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {content.map(item => (
              <tr key={item.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <p className="font-medium text-gray-900">{item.title}</p>
                </td>
                <td className="px-6 py-4 capitalize text-gray-600">{item.platform}</td>
                <td className="px-6 py-4">{getStatusBadge(item.status)}</td>
                <td className="px-6 py-4 text-gray-600">{item.views.toLocaleString()}</td>
                <td className="px-6 py-4">
                  <button className="text-indigo-600 hover:text-indigo-800 text-sm font-medium">
                    Открыть
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// Страница генерации контента с реальным Claude API
const GeneratePage = ({ content, setContent }) => {
  const [platform, setPlatform] = useState('tiktok');
  const [topic, setTopic] = useState('');
  const [niche, setNiche] = useState('productivity');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState(null);
  const [error, setError] = useState(null);

  const generateContent = async () => {
    if (!topic.trim()) {
      setError('Введите тему для генерации');
      return;
    }
    
    setIsGenerating(true);
    setError(null);
    setGeneratedContent(null);

    const systemPrompt = `Ты — Senior Copywriter с опытом создания вирального контента. Специализация: короткие видео для TikTok, YouTube Shorts, Twitter threads.

ПРАВИЛА:
1. Hook в первые 2 секунды ОБЯЗАТЕЛЕН
2. Говори на языке аудитории (русский)
3. Используй storytelling
4. Один CTA на единицу контента

Отвечай ТОЛЬКО валидным JSON без markdown.`;

    const userPrompt = `Создай сценарий для короткого видео (30-45 секунд) для платформы ${platform}.

Ниша: ${niche}
Тема: ${topic}

Верни JSON:
{
  "title": "название видео",
  "hook": "первые 2 секунды - цепляющая фраза",
  "script": "полный сценарий с таймкодами (0:00-0:03, 0:03-0:15, и т.д.)",
  "caption": "подпись для публикации (до 200 символов)",
  "hashtags": ["5-7 релевантных хештегов"],
  "cta": "призыв к действию"
}`;

    try {
      const response = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 2000,
          messages: [
            { 
              role: "user", 
              content: `${systemPrompt}\n\n${userPrompt}` 
            }
          ]
        })
      });

      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error.message);
      }

      let responseText = data.content[0].text;
      responseText = responseText.replace(/```json\n?/g, "").replace(/```\n?/g, "").trim();
      
      const parsed = JSON.parse(responseText);
      setGeneratedContent(parsed);
      
      // Добавляем в список контента
      const newContent = {
        id: Date.now(),
        title: parsed.title,
        platform: platform,
        status: 'ready',
        views: 0,
        likes: 0,
        ...parsed
      };
      setContent(prev => [newContent, ...prev]);
      
    } catch (err) {
      console.error('Generation error:', err);
      setError(`Ошибка генерации: ${err.message}`);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">🪄 Генерация контента</h1>
        <p className="text-gray-500">AI-генерация сценариев через Claude</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Форма */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100 space-y-4">
          <h3 className="font-semibold text-gray-900">Параметры генерации</h3>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Платформа</label>
            <select 
              value={platform}
              onChange={e => setPlatform(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="tiktok">TikTok</option>
              <option value="youtube">YouTube Shorts</option>
              <option value="twitter">Twitter Thread</option>
              <option value="linkedin">LinkedIn Post</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Ниша</label>
            <select 
              value={niche}
              onChange={e => setNiche(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="productivity">Продуктивность</option>
              <option value="money">Финансы / Заработок</option>
              <option value="health">Здоровье</option>
              <option value="tech">Технологии</option>
              <option value="business">Бизнес</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Тема контента</label>
            <input
              type="text"
              value={topic}
              onChange={e => setTopic(e.target.value)}
              placeholder="Например: 5 утренних привычек успешных людей"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
          
          {error && (
            <div className="p-3 bg-red-50 text-red-700 rounded-lg text-sm">
              {error}
            </div>
          )}
          
          <button
            onClick={generateContent}
            disabled={isGenerating}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Генерация...
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                Сгенерировать контент
              </>
            )}
          </button>
        </div>

        {/* Результат */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <h3 className="font-semibold text-gray-900 mb-4">Результат</h3>
          
          {!generatedContent && !isGenerating && (
            <div className="text-center py-12 text-gray-400">
              <Sparkles className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>Здесь появится сгенерированный контент</p>
            </div>
          )}
          
          {isGenerating && (
            <div className="text-center py-12">
              <Loader2 className="w-12 h-12 mx-auto mb-3 text-indigo-600 animate-spin" />
              <p className="text-gray-600">Claude генерирует контент...</p>
            </div>
          )}
          
          {generatedContent && (
            <div className="space-y-4">
              <div>
                <label className="text-xs font-medium text-gray-500 uppercase">Название</label>
                <p className="text-lg font-semibold text-gray-900">{generatedContent.title}</p>
              </div>
              
              <div>
                <label className="text-xs font-medium text-gray-500 uppercase">Hook (первые 2 сек)</label>
                <p className="p-3 bg-yellow-50 rounded-lg text-yellow-800 font-medium">{generatedContent.hook}</p>
              </div>
              
              <div>
                <label className="text-xs font-medium text-gray-500 uppercase">Сценарий</label>
                <p className="p-3 bg-gray-50 rounded-lg text-gray-700 whitespace-pre-wrap text-sm">{generatedContent.script}</p>
              </div>
              
              <div>
                <label className="text-xs font-medium text-gray-500 uppercase">Подпись</label>
                <p className="p-3 bg-gray-50 rounded-lg text-gray-700">{generatedContent.caption}</p>
              </div>
              
              <div>
                <label className="text-xs font-medium text-gray-500 uppercase">Хештеги</label>
                <div className="flex flex-wrap gap-2 mt-1">
                  {generatedContent.hashtags?.map((tag, i) => (
                    <span key={i} className="px-2 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm">
                      {tag.startsWith('#') ? tag : `#${tag}`}
                    </span>
                  ))}
                </div>
              </div>
              
              <div>
                <label className="text-xs font-medium text-gray-500 uppercase">CTA</label>
                <p className="p-3 bg-green-50 rounded-lg text-green-800">{generatedContent.cta}</p>
              </div>
              
              <button className="w-full mt-4 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
                ✅ Сохранено в контент
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Jarvis AI Assistant
const JarvisPage = () => {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Привет! Я Jarvis, твой AI-ассистент. Могу помочь с аналитикой, советами по контенту или ответить на вопросы о системе. Чем могу помочь?' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;
    
    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    const systemPrompt = `Ты — JARVIS, персональный AI-ассистент системы автоматического контента.

КОНТЕКСТ СИСТЕМЫ:
- 5 активных аккаунтов (TikTok, Twitter, LinkedIn, YouTube)
- 116,400 подписчиков суммарно
- $2,280 дохода за неделю
- 300 новых лидов
- Ниши: продуктивность, финансы

СТИЛЬ:
- Дружелюбный, но профессиональный
- Краткий и информативный
- Давай конкретные советы
- Используй эмодзи умеренно

Отвечай на русском языке. Будь полезным ассистентом.`;

    try {
      const response = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 1000,
          messages: [
            { 
              role: "user", 
              content: `${systemPrompt}\n\nВопрос пользователя: ${userMessage}` 
            }
          ]
        })
      });

      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error.message);
      }

      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: data.content[0].text 
      }]);
      
    } catch (err) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `Извини, произошла ошибка: ${err.message}` 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col">
      <div className="mb-4">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Bot className="w-8 h-8 text-indigo-600" />
          Jarvis AI Assistant
        </h1>
        <p className="text-gray-500">Голосовой ассистент системы (текстовый режим)</p>
      </div>

      <div className="flex-1 bg-white rounded-xl shadow-sm border border-gray-100 flex flex-col overflow-hidden">
        {/* Сообщения */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                msg.role === 'user' 
                  ? 'bg-indigo-600 text-white' 
                  : 'bg-gray-100 text-gray-900'
              }`}>
                <p className="whitespace-pre-wrap">{msg.content}</p>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-2xl px-4 py-3">
                <Loader2 className="w-5 h-5 animate-spin text-gray-500" />
              </div>
            </div>
          )}
        </div>

        {/* Ввод */}
        <div className="border-t p-4">
          <div className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyPress={e => e.key === 'Enter' && sendMessage()}
              placeholder="Спроси что-нибудь..."
              className="flex-1 px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <button
              onClick={sendMessage}
              disabled={!input.trim() || isLoading}
              className="px-4 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
          
          <div className="flex gap-2 mt-3">
            {['Как дела с доходом?', 'Какой контент работает лучше?', 'Дай совет по росту'].map(q => (
              <button 
                key={q}
                onClick={() => setInput(q)}
                className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-full text-gray-600 transition-colors"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Страница аналитики
const AnalyticsPage = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">📊 Аналитика</h1>
        <p className="text-gray-500">Детальная статистика и метрики</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard title="Всего просмотров" value="155,000" change={15} icon={Eye} color="bg-blue-500" />
        <StatCard title="Конверсия" value="3.2%" change={8} icon={TrendingUp} color="bg-green-500" />
        <StatCard title="ROI" value="340%" change={22} icon={DollarSign} color="bg-purple-500" />
      </div>

      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
        <h3 className="text-lg font-semibold mb-4">Лиды по дням</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={weekData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="day" stroke="#9ca3af" />
            <YAxis stroke="#9ca3af" />
            <Tooltip />
            <Bar dataKey="leads" fill="#6366f1" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
        <h3 className="text-lg font-semibold mb-4">Воронка продаж</h3>
        <div className="space-y-3">
          {[
            { stage: 'Просмотры', value: 155000, color: 'bg-blue-500', width: '100%' },
            { stage: 'Клики', value: 4650, color: 'bg-indigo-500', width: '60%' },
            { stage: 'Лиды', value: 300, color: 'bg-purple-500', width: '40%' },
            { stage: 'Конверсии', value: 48, color: 'bg-green-500', width: '20%' },
          ].map(item => (
            <div key={item.stage} className="flex items-center gap-4">
              <div className="w-24 text-sm text-gray-600">{item.stage}</div>
              <div className="flex-1 bg-gray-100 rounded-full h-8 overflow-hidden">
                <div className={`h-full ${item.color} flex items-center justify-end pr-3`} style={{ width: item.width }}>
                  <span className="text-white text-sm font-medium">{item.value.toLocaleString()}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Главный компонент
export default function ContentAutomationDashboard() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [accounts] = useState(initialAccounts);
  const [content, setContent] = useState(initialContent);

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <DashboardPage accounts={accounts} content={content} />;
      case 'accounts':
        return <AccountsPage accounts={accounts} />;
      case 'content':
        return <ContentPage content={content} setContent={setContent} />;
      case 'generate':
        return <GeneratePage content={content} setContent={setContent} />;
      case 'jarvis':
        return <JarvisPage />;
      case 'analytics':
        return <AnalyticsPage />;
      default:
        return <DashboardPage accounts={accounts} content={content} />;
    }
  };

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar currentPage={currentPage} setCurrentPage={setCurrentPage} />
      <main className="flex-1 p-8 overflow-auto">
        {renderPage()}
      </main>
    </div>
  );
}
