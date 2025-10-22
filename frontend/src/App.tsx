import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { Toaster } from 'react-hot-toast';
import { queryClient } from './lib/queryClient';
import { useStore } from './store/useStore';
import { authService } from './services/authService';

// Pages
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Documents from './pages/Documents';
import Explore from './pages/Explore';
import Playground from './pages/Playground';
import Admin from './pages/Admin';
import AdminAgents from './pages/AdminAgents';
import Monitoring from './pages/Monitoring';

// Components
import Sidebar from './components/Sidebar';
import ChatAssistant from './components/ChatAssistant';
import ProtectedRoute from './components/ProtectedRoute';

export enum Page {
  DASHBOARD = 'Dashboard',
  DOCUMENTS = 'Documents',
  EXPLORE = 'Explore',
  PLAYGROUND = 'Playground',
  ADMIN = 'Admin',
  ADMIN_AGENTS = 'AdminAgents',
  MONITORING = 'Monitoring',
}

export interface Document {
  id: string;
  name: string;
  status: string;
  uploaded: string;
  tags: string[];
  assigned_agents: string[];
  doctype: string;
  country: string;
}

// Main App Layout (for authenticated users)
const AppLayout: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<Page>(Page.DASHBOARD);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [ragContext, setRagContext] = useState<any>(null);

  const addDocument = (doc: Document) => {
    setDocuments(prev => [...prev, doc]);
  };

  const renderPage = () => {
    switch (currentPage) {
      case Page.DASHBOARD:
        return <Dashboard documents={documents} />;
      case Page.DOCUMENTS:
        return <Documents addDocument={addDocument} documents={documents} setDocuments={setDocuments} />;
      case Page.EXPLORE:
        return <Explore documents={documents} ragContext={ragContext} setRagContext={setRagContext} />;
      case Page.PLAYGROUND:
        return <Playground ragContext={ragContext} setRagContext={setRagContext} />;
      case Page.ADMIN:
        return <Admin />;
      case Page.ADMIN_AGENTS:
        return <AdminAgents />;
      case Page.MONITORING:
        return <Monitoring />;
      default:
        return <Dashboard documents={documents} />;
    }
  };

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar currentPage={currentPage} setCurrentPage={setCurrentPage} />
      <main className="flex-1 overflow-y-auto">
        {renderPage()}
      </main>
      <ChatAssistant currentPage={currentPage} />
    </div>
  );
};

function App() {
  const { isAuthenticated, login } = useStore();

  // Initialize auth state from localStorage on mount
  useEffect(() => {
    const initAuth = async () => {
      if (authService.isAuthenticated()) {
        try {
          const user = await authService.getCurrentUser();
          const accessToken = authService.getAccessToken();
          const refreshToken = authService.getRefreshToken();
          
          if (user && accessToken && refreshToken) {
            login(user, accessToken, refreshToken);
          }
        } catch (error) {
          console.error('Failed to initialize auth:', error);
          authService.clearTokens();
        }
      }
    };

    initAuth();
  }, [login]);

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route 
            path="/login" 
            element={isAuthenticated ? <Navigate to="/" replace /> : <Login />} 
          />
          
          {/* Protected Routes */}
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          />
        </Routes>

        {/* Toast Notifications */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: 'var(--bg-card)',
              color: 'var(--text-primary)',
              border: '1px solid var(--border-primary)',
              borderRadius: '0.5rem',
            },
            success: {
              iconTheme: {
                primary: 'var(--color-success)',
                secondary: 'white',
              },
            },
            error: {
              iconTheme: {
                primary: 'var(--color-error)',
                secondary: 'white',
              },
            },
          }}
        />

        {/* React Query Devtools */}
        <ReactQueryDevtools initialIsOpen={false} />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;

