import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FiFileText, FiCpu, FiActivity, FiTrendingUp, FiCheckCircle, FiClock } from 'react-icons/fi';
import { Document } from '../App';
import { fetchAgents } from '../services/apiService';
import { useGSAP, staggerFadeIn } from '../hooks/useGSAP';
import Card from '../components/ui/Card';
import LoadingSpinner from '../components/ui/LoadingSpinner';

interface DashboardProps {
  documents: Document[];
}

const Dashboard: React.FC<DashboardProps> = ({ documents }) => {
  const [agents, setAgents] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  const containerRef = useGSAP((ctx) => {
    staggerFadeIn('.kpi-card', { delay: 0.2 });
    staggerFadeIn('.agent-card', { delay: 0.4 });
    staggerFadeIn('.activity-item', { delay: 0.6 });
  }, [agents, documents]);

  useEffect(() => {
    const loadAgents = async () => {
      try {
        const agentData = await fetchAgents();
        setAgents(agentData);
      } catch (error) {
        console.error('Error loading agents:', error);
      } finally {
        setIsLoading(false);
      }
    };
    loadAgents();
  }, []);

  const kpis = [
    {
      title: 'Documents Indexés',
      value: documents.length.toString(),
      subtitle: 'Total dans la base',
      icon: FiFileText,
      color: 'text-primary-accent',
      bgColor: 'bg-primary-accent/10',
    },
    {
      title: 'Agents Actifs',
      value: agents.length.toString(),
      subtitle: 'Systèmes prêts',
      icon: FiCpu,
      color: 'text-blue',
      bgColor: 'bg-blue/10',
    },
    {
      title: 'Backend Status',
      value: 'Online',
      subtitle: 'Health check passed',
      icon: FiActivity,
      color: 'text-green',
      bgColor: 'bg-green/10',
    },
    {
      title: 'Requêtes Totales',
      value: agents.reduce((sum, a) => sum + (a.query_count || 0), 0).toString(),
      subtitle: 'Depuis le démarrage',
      icon: FiTrendingUp,
      color: 'text-yellow',
      bgColor: 'bg-yellow/10',
    }
  ];

  const recentActivities = [
    { action: 'Document analysé', detail: 'Financial Report Q4 2024', time: 'Il y a 5 min', status: 'success' },
    { action: 'Agent déployé', detail: 'TaxAgent v2.1', time: 'Il y a 15 min', status: 'success' },
    { action: 'Requête traitée', detail: 'Analyse de trésorerie', time: 'Il y a 30 min', status: 'success' },
    { action: 'Backup complété', detail: 'Base de données vectorielle', time: 'Il y a 1h', status: 'success' },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <LoadingSpinner size="xl" />
      </div>
    );
  }

  return (
    <div ref={containerRef} className="p-4 md:p-8 max-w-7xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-3xl md:text-4xl font-bold mb-2 text-gradient-primary">
          Dashboard
        </h1>
        <p className="text-secondary-text">
          Vue d'ensemble de votre AI CFO Suite
        </p>
      </motion.div>

      {/* KPIs Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 mb-8">
        {kpis.map((kpi, index) => {
          const Icon = kpi.icon;
          return (
            <Card key={index} hover className="kpi-card p-6">
              <div className="flex items-start justify-between mb-4">
                <div className={`p-3 rounded-lg ${kpi.bgColor}`}>
                  <Icon className={`text-2xl ${kpi.color}`} />
                </div>
              </div>
              <h3 className="text-secondary-text text-sm font-medium mb-2">
                {kpi.title}
              </h3>
              <p className={`text-3xl font-bold ${kpi.color} mb-1`}>
                {kpi.value}
              </p>
              <p className="text-xs text-secondary-text">{kpi.subtitle}</p>
            </Card>
          );
        })}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Agents List */}
        <Card className="p-6">
          <h2 className="text-xl md:text-2xl font-semibold mb-4 flex items-center gap-2">
            <FiCpu className="text-primary-accent" />
            Agents Disponibles
          </h2>
          <div className="space-y-3">
            {agents.length > 0 ? (
              agents.map((agent, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="agent-card flex items-center justify-between p-4 bg-background rounded-lg hover:bg-card-bg transition-colors border border-border-color hover:border-primary-accent/30"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-primary-accent/10 flex items-center justify-center">
                      <FiCpu className="text-primary-accent" />
                    </div>
                    <div>
                      <h3 className="font-medium text-primary-text">
                        {agent.name || `Agent ${index + 1}`}
                      </h3>
                      <p className="text-sm text-secondary-text">
                        {agent.role || 'Multi-purpose Agent'}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs px-2 py-1 rounded-full bg-green/20 text-green">
                      Active
                    </span>
                  </div>
                </motion.div>
              ))
            ) : (
              <p className="text-secondary-text text-center py-8">
                Aucun agent disponible
              </p>
            )}
          </div>
        </Card>

        {/* Recent Activity */}
        <Card className="p-6">
          <h2 className="text-xl md:text-2xl font-semibold mb-4 flex items-center gap-2">
            <FiActivity className="text-primary-accent" />
            Activité Récente
          </h2>
          <div className="space-y-3">
            {recentActivities.map((activity, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="activity-item flex items-start gap-3 p-3 bg-background rounded-lg hover:bg-card-bg transition-colors"
              >
                <div className="mt-1">
                  {activity.status === 'success' ? (
                    <FiCheckCircle className="text-green" />
                  ) : (
                    <FiClock className="text-yellow" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium text-primary-text text-sm">
                    {activity.action}
                  </h4>
                  <p className="text-xs text-secondary-text truncate">
                    {activity.detail}
                  </p>
                </div>
                <span className="text-xs text-secondary-text whitespace-nowrap">
                  {activity.time}
                </span>
              </motion.div>
            ))}
          </div>
        </Card>
      </div>

      {/* Quick Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="mt-6"
      >
        <Card className="p-6">
          <h2 className="text-xl md:text-2xl font-semibold mb-4">
            Statistiques Rapides
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-primary-accent">98%</p>
              <p className="text-xs text-secondary-text">Précision IA</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green">2.3s</p>
              <p className="text-xs text-secondary-text">Temps de réponse</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-blue">24/7</p>
              <p className="text-xs text-secondary-text">Disponibilité</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow">1.2k</p>
              <p className="text-xs text-secondary-text">Requêtes/jour</p>
            </div>
          </div>
        </Card>
      </motion.div>
    </div>
  );
};

export default Dashboard;

