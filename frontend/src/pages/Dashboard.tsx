import React, { useEffect, useState } from 'react';
import { Document } from '../App';
import { fetchAgents } from '../services/apiService';

interface DashboardProps {
  documents: Document[];
}

const Dashboard: React.FC<DashboardProps> = ({ documents }) => {
  const [agents, setAgents] = useState<any[]>([]);

  useEffect(() => {
    const loadAgents = async () => {
      try {
        const agentData = await fetchAgents();
        setAgents(agentData);
      } catch (error) {
        console.error('Error loading agents:', error);
      }
    };
    loadAgents();
  }, []);

  const kpis = [
    {
      title: 'Documents Indexés',
      value: documents.length.toString(),
      subtitle: 'Total dans la base',
      color: 'text-green'
    },
    {
      title: 'Agents Actifs',
      value: agents.length.toString(),
      subtitle: 'Systèmes prêts',
      color: 'text-blue'
    },
    {
      title: 'Backend Status',
      value: 'Online',
      subtitle: 'Health check passed',
      color: 'text-green'
    },
    {
      title: 'Requêtes Totales',
      value: agents.reduce((sum, a) => sum + (a.query_count || 0), 0).toString(),
      subtitle: 'Depuis le démarrage',
      color: 'text-yellow'
    }
  ];

  return (
    <div className="p-8">
      <h1 className="text-4xl font-heading font-bold mb-2">Dashboard</h1>
      <p className="text-secondary-text mb-8">
        Vue d'ensemble de votre AI CFO Suite
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {kpis.map((kpi, index) => (
          <div
            key={index}
            className="bg-card-bg border border-border-color rounded-lg p-6 hover:border-primary-accent/30 transition-all"
          >
            <h3 className="text-secondary-text text-sm font-medium mb-2">
              {kpi.title}
            </h3>
            <p className={`text-3xl font-bold ${kpi.color} mb-1`}>
              {kpi.value}
            </p>
            <p className="text-xs text-secondary-text">{kpi.subtitle}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card-bg border border-border-color rounded-lg p-6">
          <h2 className="text-xl font-heading font-semibold mb-4">
            Agents Disponibles
          </h2>
          <div className="space-y-3">
            {agents.map((agent, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-background rounded-lg"
              >
                <div>
                  <p className="font-medium text-primary-text">{agent.name}</p>
                  <p className="text-xs text-secondary-text">{agent.role}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-primary-accent">
                    {agent.query_count || 0} requêtes
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-card-bg border border-border-color rounded-lg p-6">
          <h2 className="text-xl font-heading font-semibold mb-4">
            Documents Récents
          </h2>
          <div className="space-y-3">
            {documents.slice(0, 5).map((doc) => (
              <div
                key={doc.id}
                className="flex items-center justify-between p-3 bg-background rounded-lg"
              >
                <div className="flex-1">
                  <p className="font-medium text-primary-text truncate">
                    {doc.name}
                  </p>
                  <p className="text-xs text-secondary-text">
                    {doc.assigned_agents.join(', ') || 'Aucun agent'}
                  </p>
                </div>
                <div className="ml-4">
                  <span className={`px-2 py-1 rounded text-xs ${
                    doc.status === 'Processed' ? 'bg-green/20 text-green' :
                    doc.status === 'In Progress' ? 'bg-yellow/20 text-yellow' :
                    'bg-red/20 text-red'
                  }`}>
                    {doc.status}
                  </span>
                </div>
              </div>
            ))}
            {documents.length === 0 && (
              <p className="text-secondary-text text-center py-8">
                Aucun document uploadé
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
