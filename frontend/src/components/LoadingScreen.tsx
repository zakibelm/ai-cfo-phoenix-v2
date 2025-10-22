/**
 * Loading Screen Component
 * Displays while waiting for backend to be ready
 */

import React, { useEffect, useState } from 'react';
import { connectionService, HealthStatus } from '../services/connectionService';

interface LoadingScreenProps {
  onReady: () => void;
}

export const LoadingScreen: React.FC<LoadingScreenProps> = ({ onReady }) => {
  const [status, setStatus] = useState<HealthStatus>({
    status: 'unhealthy',
    backend_available: false,
    message: 'Connecting to backend...'
  });
  const [dots, setDots] = useState('');

  useEffect(() => {
    // Animated dots
    const dotsInterval = setInterval(() => {
      setDots(prev => prev.length >= 3 ? '' : prev + '.');
    }, 500);

    // Subscribe to connection status
    const unsubscribe = connectionService.onStatusChange((newStatus) => {
      setStatus(newStatus);
      
      if (newStatus.backend_available && newStatus.status === 'healthy') {
        setTimeout(() => {
          onReady();
        }, 1000); // Small delay for smooth transition
      }
    });

    // Start waiting for backend
    connectionService.waitForBackend().then((ready) => {
      if (ready) {
        setTimeout(() => {
          onReady();
        }, 1000);
      }
    });

    return () => {
      clearInterval(dotsInterval);
      unsubscribe();
    };
  }, [onReady]);

  const getStatusColor = () => {
    switch (status.status) {
      case 'healthy':
        return 'text-green-400';
      case 'degraded':
        return 'text-yellow-400';
      default:
        return 'text-cyan-400';
    }
  };

  const getStatusIcon = () => {
    switch (status.status) {
      case 'healthy':
        return '✅';
      case 'degraded':
        return '⚠️';
      default:
        return '🔄';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
      <div className="text-center">
        {/* Logo */}
        <div className="mb-8">
          <h1 className="text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500 mb-2">
            Phoenix
          </h1>
          <p className="text-xl text-slate-400">AI CFO Suite</p>
        </div>

        {/* Loading Animation */}
        <div className="mb-8">
          <div className="relative w-24 h-24 mx-auto">
            <div className="absolute inset-0 border-4 border-cyan-400/20 rounded-full"></div>
            <div className="absolute inset-0 border-4 border-transparent border-t-cyan-400 rounded-full animate-spin"></div>
            <div className="absolute inset-2 border-4 border-transparent border-t-blue-500 rounded-full animate-spin animation-delay-150"></div>
            <div className="absolute inset-4 border-4 border-transparent border-t-purple-500 rounded-full animate-spin animation-delay-300"></div>
          </div>
        </div>

        {/* Status Message */}
        <div className={`text-lg font-medium ${getStatusColor()} mb-4`}>
          <span className="mr-2">{getStatusIcon()}</span>
          {status.message || 'Initializing system'}{dots}
        </div>

        {/* Progress Steps */}
        <div className="space-y-2 text-sm text-slate-400">
          <div className="flex items-center justify-center space-x-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span>Database services</span>
            <span className="text-green-400">✓</span>
          </div>
          <div className="flex items-center justify-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${status.backend_available ? 'bg-green-400' : 'bg-cyan-400 animate-pulse'}`}></div>
            <span>Backend API</span>
            {status.backend_available && <span className="text-green-400">✓</span>}
          </div>
          <div className="flex items-center justify-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${status.status === 'healthy' ? 'bg-green-400' : 'bg-slate-600'}`}></div>
            <span>AI Agents</span>
            {status.status === 'healthy' && <span className="text-green-400">✓</span>}
          </div>
        </div>

        {/* Retry Info */}
        {!status.backend_available && (
          <div className="mt-8 text-xs text-slate-500">
            <p>Waiting for backend to be ready...</p>
            <p className="mt-1">This may take 20-30 seconds on first start</p>
          </div>
        )}

        {/* Error State */}
        {status.status === 'unhealthy' && status.message?.includes('maximum retries') && (
          <div className="mt-8 p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
            <p className="text-red-400 font-medium mb-2">❌ Connection Failed</p>
            <p className="text-sm text-slate-400 mb-4">
              Unable to connect to backend. Please check:
            </p>
            <ul className="text-xs text-slate-500 text-left max-w-md mx-auto space-y-1">
              <li>• Docker containers are running: <code className="text-cyan-400">docker-compose ps</code></li>
              <li>• Backend logs: <code className="text-cyan-400">docker-compose logs backend</code></li>
              <li>• Environment variables are set correctly</li>
            </ul>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 px-6 py-2 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg transition-colors"
            >
              Retry Connection
            </button>
          </div>
        )}
      </div>

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        .animation-delay-150 {
          animation-delay: 150ms;
        }
        .animation-delay-300 {
          animation-delay: 300ms;
        }
      `}</style>
    </div>
  );
};

