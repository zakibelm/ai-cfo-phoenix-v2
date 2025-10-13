import React from 'react';

const Admin: React.FC = () => {
  const services = [
    { name: 'Qdrant Vector DB', endpoint: 'http://localhost:6333', status: 'online' },
    { name: 'PostgreSQL', endpoint: 'localhost:5432', status: 'online' },
    { name: 'Redis Cache', endpoint: 'localhost:6379', status: 'online' },
    { name: 'MinIO Storage', endpoint: 'http://localhost:9000', status: 'online' },
    { name: 'FastAPI Backend', endpoint: 'http://localhost:8000', status: 'online' }
  ];

  return (
    <div className="p-8">
      <h1 className="text-4xl font-heading font-bold mb-2">Administration</h1>
      <p className="text-secondary-text mb-8">
        Configuration et gestion du système
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card-bg border border-border-color rounded-lg p-6">
          <h2 className="text-2xl font-heading font-semibold mb-4">
            Services & Intégrations
          </h2>
          <p className="text-secondary-text mb-6">
            État des composants open-source intégrés
          </p>
          <div className="space-y-3">
            {services.map((service, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-4 bg-background rounded-lg"
              >
                <div>
                  <p className="font-medium text-primary-text">{service.name}</p>
                  <p className="text-xs text-secondary-text">{service.endpoint}</p>
                </div>
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${
                    service.status === 'online' ? 'bg-green' : 'bg-red'
                  } animate-pulse`}></div>
                  <span className={`text-sm ${
                    service.status === 'online' ? 'text-green' : 'text-red'
                  }`}>
                    {service.status === 'online' ? 'En ligne' : 'Hors ligne'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-card-bg border border-border-color rounded-lg p-6">
          <h2 className="text-2xl font-heading font-semibold mb-4">
            Gestion du Vector Store
          </h2>
          <p className="text-secondary-text mb-6">
            Gérer l'index des documents et la base de données vectorielle
          </p>
          <div className="space-y-3">
            <button className="w-full bg-background border border-border-color hover:border-primary-accent/50 text-primary-text font-medium py-3 rounded-lg transition-all">
              Ré-indexer Tous les Documents
            </button>
            <button className="w-full bg-background border border-border-color hover:border-primary-accent/50 text-primary-text font-medium py-3 rounded-lg transition-all">
              Voir les Statistiques d'Index
            </button>
            <button className="w-full bg-background border border-border-color hover:border-primary-accent/50 text-primary-text font-medium py-3 rounded-lg transition-all">
              Nettoyer le Cache
            </button>
          </div>
        </div>

        <div className="bg-card-bg border border-border-color rounded-lg p-6">
          <h2 className="text-2xl font-heading font-semibold mb-4">
            Configuration des Agents
          </h2>
          <p className="text-secondary-text mb-6">
            Paramètres du système multi-agents
          </p>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-primary-text mb-2">
                Modèle d'Embeddings
              </label>
              <input
                type="text"
                value="BAAI/bge-small-en-v1.5"
                readOnly
                className="w-full bg-background border border-border-color rounded-lg px-4 py-2 text-secondary-text"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-primary-text mb-2">
                Modèle LLM par Défaut
              </label>
              <input
                type="text"
                value="mistralai/mistral-7b-instruct"
                readOnly
                className="w-full bg-background border border-border-color rounded-lg px-4 py-2 text-secondary-text"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-primary-text mb-2">
                Top-K (Résultats RAG)
              </label>
              <input
                type="number"
                value="10"
                readOnly
                className="w-full bg-background border border-border-color rounded-lg px-4 py-2 text-secondary-text"
              />
            </div>
          </div>
        </div>

        <div className="bg-card-bg border border-border-color rounded-lg p-6">
          <h2 className="text-2xl font-heading font-semibold mb-4">
            Informations Système
          </h2>
          <div className="space-y-3">
            <div className="flex justify-between p-3 bg-background rounded-lg">
              <span className="text-secondary-text">Version</span>
              <span className="text-primary-text font-medium">2.0.0</span>
            </div>
            <div className="flex justify-between p-3 bg-background rounded-lg">
              <span className="text-secondary-text">Architecture</span>
              <span className="text-primary-text font-medium">Multi-Agent RAG</span>
            </div>
            <div className="flex justify-between p-3 bg-background rounded-lg">
              <span className="text-secondary-text">Framework Agents</span>
              <span className="text-primary-text font-medium">CrewAI + AutoGen</span>
            </div>
            <div className="flex justify-between p-3 bg-background rounded-lg">
              <span className="text-secondary-text">Vector DB</span>
              <span className="text-primary-text font-medium">Qdrant</span>
            </div>
            <div className="flex justify-between p-3 bg-background rounded-lg">
              <span className="text-secondary-text">Backend</span>
              <span className="text-primary-text font-medium">FastAPI + Python</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Admin;
