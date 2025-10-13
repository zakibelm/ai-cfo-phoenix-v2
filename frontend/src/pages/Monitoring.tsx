import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface SystemMetrics {
  uptime_seconds: number;
  uptime_formatted: string;
  total_requests: number;
  total_errors: number;
  error_rate: number;
  agents_monitored: number;
  ssh_hosts_monitored: number;
}

interface AgentMetrics {
  agent_id: string;
  request_count: number;
  error_count: number;
  avg_response_time: number;
  min_response_time: number;
  max_response_time: number;
  success_rate: number;
  last_request: string | null;
}

interface SSHMetrics {
  host: string;
  connection_attempts: number;
  successful_connections: number;
  failed_connections: number;
  success_rate: number;
  avg_latency: number;
  last_connection: string | null;
}

interface HealthStatus {
  status: string;
  timestamp: string;
  metrics: SystemMetrics;
}

const Monitoring: React.FC = () => {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [agentMetrics, setAgentMetrics] = useState<AgentMetrics[]>([]);
  const [sshMetrics, setSSHMetrics] = useState<SSHMetrics[]>([]);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(5000);

  useEffect(() => {
    loadDashboard();
    
    if (autoRefresh) {
      const interval = setInterval(loadDashboard, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval]);

  const loadDashboard = async () => {
    try {
      const response = await axios.get('/api/v1/monitoring/dashboard');
      setHealth(response.data.health);
      setAgentMetrics(response.data.agents);
      setSSHMetrics(response.data.ssh);
    } catch (error) {
      console.error('Error loading monitoring dashboard:', error);
    }
  };

  const getHealthColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green';
      case 'degraded': return 'text-yellow';
      case 'unhealthy': return 'text-red';
      default: return 'text-secondary-text';
    }
  };

  const getHealthIcon = (status: string) => {
    switch (status) {
      case 'healthy': return '✅';
      case 'degraded': return '⚠️';
      case 'unhealthy': return '❌';
      default: return '❓';
    }
  };

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (days > 0) return `${days}j ${hours}h`;
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  };

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-4xl font-heading font-bold">Monitoring & Métriques</h1>
          <p className="text-secondary-text mt-1">
            Surveillance en temps réel du système et des agents
          </p>
        </div>
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-sm text-primary-text">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="w-4 h-4"
            />
            Auto-refresh
          </label>
          <select
            value={refreshInterval}
            onChange={(e) => setRefreshInterval(Number(e.target.value))}
            disabled={!autoRefresh}
            className="px-3 py-2 bg-input-background border border-border-color rounded-lg text-primary-text text-sm disabled:opacity-50"
          >
            <option value={3000}>3s</option>
            <option value={5000}>5s</option>
            <option value={10000}>10s</option>
            <option value={30000}>30s</option>
          </select>
          <button
            onClick={loadDashboard}
            className="px-4 py-2 bg-primary-accent text-background font-semibold rounded-lg hover:bg-primary-accent/90 transition-all"
          >
            🔄 Actualiser
          </button>
        </div>
      </div>

      {/* Health Status */}
      {health && (
        <div className="bg-card-bg border border-border-color rounded-lg p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-heading font-semibold mb-2">État du Système</h2>
              <div className="flex items-center gap-3">
                <span className="text-4xl">{getHealthIcon(health.status)}</span>
                <div>
                  <p className={`text-2xl font-bold ${getHealthColor(health.status)}`}>
                    {health.status.toUpperCase()}
                  </p>
                  <p className="text-sm text-secondary-text">
                    Mis à jour : {new Date(health.timestamp).toLocaleTimeString('fr-FR')}
                  </p>
                </div>
              </div>
            </div>
            
            <div className="grid grid-cols-3 gap-6">
              <div className="text-center">
                <p className="text-3xl font-bold text-primary-accent">
                  {formatUptime(health.metrics.uptime_seconds)}
                </p>
                <p className="text-sm text-secondary-text">Uptime</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-bold text-primary-text">
                  {health.metrics.total_requests.toLocaleString()}
                </p>
                <p className="text-sm text-secondary-text">Requêtes</p>
              </div>
              <div className="text-center">
                <p className={`text-3xl font-bold ${health.metrics.error_rate > 10 ? 'text-red' : 'text-green'}`}>
                  {health.metrics.error_rate.toFixed(1)}%
                </p>
                <p className="text-sm text-secondary-text">Taux d'erreur</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Agent Metrics */}
      <div className="bg-card-bg border border-border-color rounded-lg p-6 mb-6">
        <h2 className="text-2xl font-heading font-semibold mb-4">
          Métriques des Agents ({agentMetrics.length})
        </h2>
        
        {agentMetrics.length === 0 ? (
          <p className="text-secondary-text text-center py-8">
            Aucune métrique d'agent disponible
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border-color">
                  <th className="text-left py-3 px-4 text-sm font-medium text-secondary-text">Agent</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-secondary-text">Requêtes</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-secondary-text">Erreurs</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-secondary-text">Taux de succès</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-secondary-text">Temps moyen</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-secondary-text">Min/Max</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-secondary-text">Dernière requête</th>
                </tr>
              </thead>
              <tbody>
                {agentMetrics.map((metric) => (
                  <tr key={metric.agent_id} className="border-b border-border-color/50 hover:bg-background/50 transition-colors">
                    <td className="py-3 px-4">
                      <span className="font-medium text-primary-text">{metric.agent_id}</span>
                    </td>
                    <td className="text-right py-3 px-4 text-primary-text">
                      {metric.request_count}
                    </td>
                    <td className="text-right py-3 px-4">
                      <span className={metric.error_count > 0 ? 'text-red' : 'text-secondary-text'}>
                        {metric.error_count}
                      </span>
                    </td>
                    <td className="text-right py-3 px-4">
                      <span className={`font-semibold ${
                        metric.success_rate >= 95 ? 'text-green' :
                        metric.success_rate >= 80 ? 'text-yellow' :
                        'text-red'
                      }`}>
                        {metric.success_rate.toFixed(1)}%
                      </span>
                    </td>
                    <td className="text-right py-3 px-4 text-primary-text">
                      {metric.avg_response_time.toFixed(2)}s
                    </td>
                    <td className="text-right py-3 px-4 text-secondary-text text-sm">
                      {metric.min_response_time.toFixed(2)}s / {metric.max_response_time.toFixed(2)}s
                    </td>
                    <td className="text-right py-3 px-4 text-secondary-text text-sm">
                      {metric.last_request ? new Date(metric.last_request).toLocaleString('fr-FR') : 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* SSH Metrics */}
      {sshMetrics.length > 0 && (
        <div className="bg-card-bg border border-border-color rounded-lg p-6">
          <h2 className="text-2xl font-heading font-semibold mb-4">
            Connexions SSH ({sshMetrics.length})
          </h2>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border-color">
                  <th className="text-left py-3 px-4 text-sm font-medium text-secondary-text">Hôte</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-secondary-text">Tentatives</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-secondary-text">Succès</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-secondary-text">Échecs</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-secondary-text">Taux de succès</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-secondary-text">Latence moy.</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-secondary-text">Dernière connexion</th>
                </tr>
              </thead>
              <tbody>
                {sshMetrics.map((metric) => (
                  <tr key={metric.host} className="border-b border-border-color/50 hover:bg-background/50 transition-colors">
                    <td className="py-3 px-4">
                      <span className="font-medium text-primary-text font-mono text-sm">{metric.host}</span>
                    </td>
                    <td className="text-right py-3 px-4 text-primary-text">
                      {metric.connection_attempts}
                    </td>
                    <td className="text-right py-3 px-4 text-green">
                      {metric.successful_connections}
                    </td>
                    <td className="text-right py-3 px-4">
                      <span className={metric.failed_connections > 0 ? 'text-red' : 'text-secondary-text'}>
                        {metric.failed_connections}
                      </span>
                    </td>
                    <td className="text-right py-3 px-4">
                      <span className={`font-semibold ${
                        metric.success_rate >= 95 ? 'text-green' :
                        metric.success_rate >= 80 ? 'text-yellow' :
                        'text-red'
                      }`}>
                        {metric.success_rate.toFixed(1)}%
                      </span>
                    </td>
                    <td className="text-right py-3 px-4 text-primary-text">
                      {metric.avg_latency.toFixed(0)}ms
                    </td>
                    <td className="text-right py-3 px-4 text-secondary-text text-sm">
                      {metric.last_connection ? new Date(metric.last_connection).toLocaleString('fr-FR') : 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default Monitoring;
