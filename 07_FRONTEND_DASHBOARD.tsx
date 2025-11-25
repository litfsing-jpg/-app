# =============================================
# FRONTEND DASHBOARD (REACT)
# =============================================

# ============================================
# ФАЙЛ: frontend/package.json
# ============================================

{
  "name": "content-automation-dashboard",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.22.0",
    "axios": "^1.6.7",
    "@tanstack/react-query": "^5.17.0",
    "zustand": "^4.5.0",
    "recharts": "^2.12.0",
    "lucide-react": "^0.316.0",
    "date-fns": "^3.3.1",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.1"
  },
  "devDependencies": {
    "typescript": "^5.3.3",
    "@types/react": "^18.2.48",
    "@types/react-dom": "^18.2.18",
    "vite": "^5.0.12",
    "@vitejs/plugin-react": "^4.2.1",
    "tailwindcss": "^3.4.1",
    "postcss": "^8.4.33",
    "autoprefixer": "^10.4.17"
  },
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  }
}


# ============================================
# ФАЙЛ: frontend/src/App.tsx
# ============================================

import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAuthStore } from './store/authStore';

// Layouts
import DashboardLayout from './components/Layout/DashboardLayout';

// Pages
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import AccountsPage from './pages/AccountsPage';
import ContentPage from './pages/ContentPage';
import AnalyticsPage from './pages/AnalyticsPage';
import FunnelPage from './pages/FunnelPage';
import NichesPage from './pages/NichesPage';
import SettingsPage from './pages/SettingsPage';
import VoicePage from './pages/VoicePage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 минут
      retry: 1,
    },
  },
});

// Protected Route компонент
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuthStore();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<DashboardPage />} />
            <Route path="accounts" element={<AccountsPage />} />
            <Route path="content" element={<ContentPage />} />
            <Route path="analytics" element={<AnalyticsPage />} />
            <Route path="funnel" element={<FunnelPage />} />
            <Route path="niches" element={<NichesPage />} />
            <Route path="voice" element={<VoicePage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;


# ============================================
# ФАЙЛ: frontend/src/store/authStore.ts
# ============================================

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  token: string | null;
  user: any | null;
  isAuthenticated: boolean;
  login: (token: string, user: any) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      isAuthenticated: false,
      
      login: (token, user) => set({
        token,
        user,
        isAuthenticated: true
      }),
      
      logout: () => set({
        token: null,
        user: null,
        isAuthenticated: false
      })
    }),
    {
      name: 'auth-storage'
    }
  )
);


# ============================================
# ФАЙЛ: frontend/src/services/api.ts
# ============================================

import axios from 'axios';
import { useAuthStore } from '../store/authStore';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Добавляем токен к запросам
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Обработка ошибок авторизации
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API методы
export const authApi = {
  login: (email: string, password: string) =>
    api.post('/auth/login', null, { params: { email, password } }),
  register: (data: any) => api.post('/auth/register', data),
  me: () => api.get('/users/me')
};

export const dashboardApi = {
  getSummary: () => api.get('/analytics/dashboard'),
  getFunnel: () => api.get('/analytics/funnel'),
  getRevenue: (period: string) => api.get(`/analytics/revenue?period=${period}`),
  getPlatforms: () => api.get('/analytics/platforms')
};

export const accountsApi = {
  getAll: (params?: any) => api.get('/accounts', { params }),
  getOne: (id: string) => api.get(`/accounts/${id}`),
  create: (data: any) => api.post('/accounts', data),
  update: (id: string, data: any) => api.patch(`/accounts/${id}`, data),
  delete: (id: string) => api.delete(`/accounts/${id}`),
  getStats: (id: string) => api.get(`/accounts/${id}/stats`)
};

export const contentApi = {
  getAll: (params?: any) => api.get('/content', { params }),
  getOne: (id: string) => api.get(`/content/${id}`),
  create: (data: any) => api.post('/content', data),
  generate: (data: any) => api.post('/content/generate', data),
  generateBatch: (data: any) => api.post('/content/generate-batch', data),
  update: (id: string, data: any) => api.patch(`/content/${id}`, data),
  delete: (id: string) => api.delete(`/content/${id}`),
  schedule: (id: string, data: any) => api.post(`/content/${id}/schedule`, data),
  getQueue: () => api.get('/content/queue')
};

export const nichesApi = {
  getAll: () => api.get('/niches'),
  getOne: (id: string) => api.get(`/niches/${id}`),
  create: (data: any) => api.post('/niches', data),
  update: (id: string, data: any) => api.patch(`/niches/${id}`, data),
  delete: (id: string) => api.delete(`/niches/${id}`),
  analyze: (name: string) => api.post('/niches/analyze', null, { params: { niche_name: name } }),
  suggest: (category?: string) => api.post('/niches/suggest', null, { params: { category } })
};

export const voiceApi = {
  query: (query: string) => api.post('/voice/query', null, { params: { query } }),
  speak: (audio: Blob) => {
    const formData = new FormData();
    formData.append('audio', audio);
    return api.post('/voice/speak', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  }
};

export default api;


# ============================================
# ФАЙЛ: frontend/src/components/Layout/DashboardLayout.tsx
# ============================================

import React, { useState } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import {
  LayoutDashboard,
  Users,
  FileText,
  BarChart3,
  Filter,
  Target,
  Mic,
  Settings,
  LogOut,
  Menu,
  X
} from 'lucide-react';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Аккаунты', href: '/accounts', icon: Users },
  { name: 'Контент', href: '/content', icon: FileText },
  { name: 'Аналитика', href: '/analytics', icon: BarChart3 },
  { name: 'Воронка', href: '/funnel', icon: Filter },
  { name: 'Ниши', href: '/niches', icon: Target },
  { name: 'Jarvis', href: '/voice', icon: Mic },
  { name: 'Настройки', href: '/settings', icon: Settings },
];

export default function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const { logout, user } = useAuthStore();
  
  return (
    <div className="min-h-screen bg-gray-100">
      {/* Mobile sidebar */}
      <div className={`fixed inset-0 z-50 lg:hidden ${sidebarOpen ? '' : 'hidden'}`}>
        <div className="fixed inset-0 bg-gray-600 bg-opacity-75" onClick={() => setSidebarOpen(false)} />
        <div className="fixed inset-y-0 left-0 flex w-64 flex-col bg-gray-900">
          <div className="flex h-16 items-center justify-between px-4">
            <span className="text-xl font-bold text-white">Content System</span>
            <button onClick={() => setSidebarOpen(false)} className="text-white">
              <X className="h-6 w-6" />
            </button>
          </div>
          <nav className="flex-1 space-y-1 px-2 py-4">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`flex items-center px-4 py-3 text-sm font-medium rounded-lg ${
                    isActive
                      ? 'bg-gray-800 text-white'
                      : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                  }`}
                  onClick={() => setSidebarOpen(false)}
                >
                  <item.icon className="mr-3 h-5 w-5" />
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </div>
      </div>
      
      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex min-h-0 flex-1 flex-col bg-gray-900">
          <div className="flex h-16 items-center px-4">
            <span className="text-xl font-bold text-white">🚀 Content System</span>
          </div>
          <nav className="flex-1 space-y-1 px-2 py-4">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                    isActive
                      ? 'bg-indigo-600 text-white'
                      : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                  }`}
                >
                  <item.icon className="mr-3 h-5 w-5" />
                  {item.name}
                </Link>
              );
            })}
          </nav>
          <div className="p-4 border-t border-gray-800">
            <button
              onClick={logout}
              className="flex items-center w-full px-4 py-2 text-sm text-gray-300 hover:text-white hover:bg-gray-800 rounded-lg"
            >
              <LogOut className="mr-3 h-5 w-5" />
              Выйти
            </button>
          </div>
        </div>
      </div>
      
      {/* Main content */}
      <div className="lg:pl-64">
        <div className="sticky top-0 z-40 flex h-16 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm">
          <button
            type="button"
            className="lg:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-6 w-6" />
          </button>
          
          <div className="flex flex-1 justify-end">
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">{user?.email}</span>
            </div>
          </div>
        </div>
        
        <main className="py-6 px-4 sm:px-6 lg:px-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}


# ============================================
# ФАЙЛ: frontend/src/pages/DashboardPage.tsx
# ============================================

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from '../services/api';
import {
  Users,
  Eye,
  DollarSign,
  TrendingUp,
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

// Карточка статистики
const StatCard = ({ title, value, change, icon: Icon, color }: any) => (
  <div className="bg-white rounded-xl shadow-sm p-6">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm text-gray-500">{title}</p>
        <p className="text-2xl font-bold mt-1">{value}</p>
        {change && (
          <p className={`text-sm mt-1 ${change > 0 ? 'text-green-600' : 'text-red-600'}`}>
            {change > 0 ? '+' : ''}{change}% vs прошлый период
          </p>
        )}
      </div>
      <div className={`p-3 rounded-full ${color}`}>
        <Icon className="h-6 w-6 text-white" />
      </div>
    </div>
  </div>
);

export default function DashboardPage() {
  const { data: summary, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => dashboardApi.getSummary().then(res => res.data)
  });
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }
  
  const stats = [
    {
      title: 'Всего подписчиков',
      value: summary?.total_followers?.toLocaleString() || '0',
      change: 12,
      icon: Users,
      color: 'bg-blue-500'
    },
    {
      title: 'Опубликовано сегодня',
      value: summary?.published_today || '0',
      icon: CheckCircle,
      color: 'bg-green-500'
    },
    {
      title: 'Доход за месяц',
      value: `$${summary?.revenue_month?.toLocaleString() || '0'}`,
      change: 8,
      icon: DollarSign,
      color: 'bg-purple-500'
    },
    {
      title: 'Новых лидов сегодня',
      value: summary?.new_leads_today || '0',
      icon: TrendingUp,
      color: 'bg-orange-500'
    }
  ];
  
  // Данные для графика
  const chartData = [
    { date: 'Пн', views: 4000, leads: 24 },
    { date: 'Вт', views: 3000, leads: 18 },
    { date: 'Ср', views: 5000, leads: 32 },
    { date: 'Чт', views: 4500, leads: 28 },
    { date: 'Пт', views: 6000, leads: 40 },
    { date: 'Сб', views: 5500, leads: 35 },
    { date: 'Вс', views: 4800, leads: 30 }
  ];
  
  // Данные для pie chart платформ
  const platformData = summary?.platforms_stats?.map((p: any) => ({
    name: p.platform,
    value: p.total_followers
  })) || [];
  
  const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#f97316'];
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <span className="text-sm text-gray-500">
          Обновлено: {new Date().toLocaleTimeString()}
        </span>
      </div>
      
      {/* Статистика */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <StatCard key={index} {...stat} />
        ))}
      </div>
      
      {/* Предупреждения */}
      {(summary?.accounts_needing_attention > 0 || summary?.failed_publications > 0) && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-yellow-600 mr-2" />
            <span className="text-yellow-800 font-medium">Требует внимания:</span>
          </div>
          <ul className="mt-2 text-sm text-yellow-700 list-disc list-inside">
            {summary?.accounts_needing_attention > 0 && (
              <li>{summary.accounts_needing_attention} аккаунтов с низким health score</li>
            )}
            {summary?.failed_publications > 0 && (
              <li>{summary.failed_publications} неудачных публикаций</li>
            )}
          </ul>
        </div>
      )}
      
      {/* Графики */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* График просмотров */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold mb-4">Просмотры и лиды</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="views"
                stroke="#6366f1"
                strokeWidth={2}
                name="Просмотры"
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="leads"
                stroke="#10b981"
                strokeWidth={2}
                name="Лиды"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        
        {/* Pie chart платформ */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h3 className="text-lg font-semibold mb-4">Подписчики по платформам</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={platformData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {platformData.map((_: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      {/* Аккаунты */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h3 className="text-lg font-semibold mb-4">Аккаунты</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <p className="text-3xl font-bold text-indigo-600">{summary?.total_accounts || 0}</p>
            <p className="text-sm text-gray-500">Всего</p>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <p className="text-3xl font-bold text-green-600">{summary?.active_accounts || 0}</p>
            <p className="text-sm text-gray-500">Активных</p>
          </div>
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <p className="text-3xl font-bold text-blue-600">{summary?.scheduled_content || 0}</p>
            <p className="text-sm text-gray-500">В очереди</p>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <p className="text-3xl font-bold text-purple-600">{summary?.total_content || 0}</p>
            <p className="text-sm text-gray-500">Контента</p>
          </div>
        </div>
      </div>
    </div>
  );
}


# ============================================
# ФАЙЛ: frontend/src/pages/VoicePage.tsx
# ============================================

import React, { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Send, Volume2, Loader2 } from 'lucide-react';
import { voiceApi } from '../services/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  audio?: string;
}

export default function VoicePage() {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Привет! Я Jarvis, твой AI-ассистент. Чем могу помочь?' }
  ]);
  const [input, setInput] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Автоскролл к последнему сообщению
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  // Отправка текстового сообщения
  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;
    
    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);
    
    try {
      const response = await voiceApi.query(userMessage);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.data.response
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Извини, произошла ошибка. Попробуй ещё раз.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Начало записи голоса
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      
      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };
      
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        stream.getTracks().forEach(track => track.stop());
        
        // Отправляем на сервер
        setIsLoading(true);
        try {
          const response = await voiceApi.speak(audioBlob);
          const { query, response: answer, audio } = response.data;
          
          setMessages(prev => [
            ...prev,
            { role: 'user', content: query },
            { role: 'assistant', content: answer, audio }
          ]);
          
          // Воспроизводим ответ
          if (audio) {
            playAudio(audio);
          }
        } catch (error) {
          setMessages(prev => [...prev, {
            role: 'assistant',
            content: 'Не удалось обработать голосовое сообщение.'
          }]);
        } finally {
          setIsLoading(false);
        }
      };
      
      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Не удалось получить доступ к микрофону');
    }
  };
  
  // Остановка записи
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };
  
  // Воспроизведение аудио
  const playAudio = (base64Audio: string) => {
    const audio = new Audio(`data:audio/mp3;base64,${base64Audio}`);
    audioRef.current = audio;
    setIsPlaying(true);
    
    audio.onended = () => setIsPlaying(false);
    audio.play();
  };
  
  return (
    <div className="h-[calc(100vh-10rem)] flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold text-gray-900">🤖 Jarvis</h1>
        <span className="text-sm text-gray-500">Голосовой ассистент</span>
      </div>
      
      {/* Чат */}
      <div className="flex-1 bg-white rounded-xl shadow-sm overflow-hidden flex flex-col">
        {/* Сообщения */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                  message.role === 'user'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>
                {message.audio && (
                  <button
                    onClick={() => playAudio(message.audio!)}
                    className="mt-2 flex items-center text-sm opacity-75 hover:opacity-100"
                  >
                    <Volume2 className="h-4 w-4 mr-1" />
                    Воспроизвести
                  </button>
                )}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-2xl px-4 py-3">
                <Loader2 className="h-5 w-5 animate-spin text-gray-500" />
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
        
        {/* Ввод */}
        <div className="border-t p-4">
          <div className="flex items-center gap-3">
            {/* Кнопка записи */}
            <button
              onClick={isRecording ? stopRecording : startRecording}
              disabled={isLoading}
              className={`p-3 rounded-full transition-colors ${
                isRecording
                  ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse'
                  : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
              }`}
            >
              {isRecording ? <MicOff className="h-6 w-6" /> : <Mic className="h-6 w-6" />}
            </button>
            
            {/* Текстовый ввод */}
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Напиши или нажми на микрофон..."
              disabled={isRecording || isLoading}
              className="flex-1 px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            
            {/* Кнопка отправки */}
            <button
              onClick={sendMessage}
              disabled={!input.trim() || isLoading}
              className="p-3 bg-indigo-600 text-white rounded-full hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="h-6 w-6" />
            </button>
          </div>
          
          {isRecording && (
            <p className="text-center text-sm text-red-500 mt-2 animate-pulse">
              🔴 Запись... Нажми снова чтобы остановить
            </p>
          )}
        </div>
      </div>
    </div>
  );
}


# ============================================
# ФАЙЛ: frontend/src/pages/LoginPage.tsx
# ============================================

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { authApi } from '../services/api';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const navigate = useNavigate();
  const { login } = useAuthStore();
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    
    try {
      const response = await authApi.login(email, password);
      const { access_token } = response.data;
      
      // Получаем информацию о пользователе
      const userResponse = await authApi.me();
      
      login(access_token, userResponse.data);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка входа');
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded-xl shadow-lg w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">🚀 Content System</h1>
          <p className="text-gray-500 mt-2">Войдите в систему</p>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm">
              {error}
            </div>
          )}
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="your@email.com"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Пароль
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="••••••••"
              required
            />
          </div>
          
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-indigo-600 text-white py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50"
          >
            {isLoading ? 'Вход...' : 'Войти'}
          </button>
        </form>
      </div>
    </div>
  );
}


# ============================================
# ФАЙЛ: frontend/tailwind.config.js
# ============================================

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}


# ============================================
# ФАЙЛ: frontend/vite.config.ts
# ============================================

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
