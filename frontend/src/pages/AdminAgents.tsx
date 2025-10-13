import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Agent {
  id: string;
  name: string;
  role: string;
  goal: string;
  backstory: string;
  system_prompt: string | null;
  namespace: string;
  is_active: boolean;
  is_custom: boolean;
  is_remote: boolean;
  icon: string;
  color: string;
  ssh_host: string | null;
  ssh_port: number;
  ssh_username: string | null;
  ssh_endpoint: string;
  query_count: number;
}

const AdminAgents: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [sshTestResult, setSshTestResult] = useState<string | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    id: '',
    name: '',
    role: '',
    goal: '',
    backstory: '',
    system_prompt: '',
    namespace: 'default',
    icon: '🤖',
    color: '#64ffda',
    is_remote: false,
    ssh_host: '',
    ssh_port: 22,
    ssh_username: '',
    ssh_password: '',
    ssh_key_path: '',
    ssh_endpoint: '/process',
    keywords: ''
  });

  useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    try {
      const response = await axios.get('/api/v1/agents');
      setAgents(response.data.agents);
    } catch (error) {
      console.error('Error loading agents:', error);
    }
  };

  const handleSelectAgent = (agent: Agent) => {
    setSelectedAgent(agent);
    setFormData({
      id: agent.id,
      name: agent.name,
      role: agent.role,
      goal: agent.goal,
      backstory: agent.backstory,
      system_prompt: agent.system_prompt || '',
      namespace: agent.namespace,
      icon: agent.icon,
      color: agent.color,
      is_remote: agent.is_remote,
      ssh_host: agent.ssh_host || '',
      ssh_port: agent.ssh_port,
      ssh_username: agent.ssh_username || '',
      ssh_password: '',
      ssh_key_path: '',
      ssh_endpoint: agent.ssh_endpoint,
      keywords: ''
    });
    setIsEditing(false);
    setIsCreating(false);
  };

  const handleCreateNew = () => {
    setSelectedAgent(null);
    setFormData({
      id: '',
      name: '',
      role: '',
      goal: '',
      backstory: '',
      system_prompt: '',
      namespace: 'default',
      icon: '🤖',
      color: '#64ffda',
      is_remote: false,
      ssh_host: '',
      ssh_port: 22,
      ssh_username: '',
      ssh_password: '',
      ssh_key_path: '',
      ssh_endpoint: '/process',
      keywords: ''
    });
    setIsCreating(true);
    setIsEditing(true);
  };

  const handleSave = async () => {
    try {
      const payload = {
        ...formData,
        keywords: formData.keywords.split(',').map(k => k.trim()).filter(k => k)
      };

      if (isCreating) {
        await axios.post('/api/v1/agents', payload);
        alert('Agent créé avec succès !');
      } else if (selectedAgent) {
        await axios.put(`/api/v1/agents/${selectedAgent.id}`, payload);
        alert('Agent mis à jour avec succès !');
      }

      await loadAgents();
      setIsEditing(false);
      setIsCreating(false);
    } catch (error: any) {
      alert(`Erreur : ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleTestSSH = async () => {
    try {
      setSshTestResult('Test en cours...');
      const response = await axios.post('/api/v1/agents/ssh/test', {
        host: formData.ssh_host,
        port: formData.ssh_port,
        username: formData.ssh_username,
        password: formData.ssh_password || null,
        key_path: formData.ssh_key_path || null
      });

      if (response.data.success) {
        setSshTestResult('✅ Connexion SSH réussie !');
      } else {
        setSshTestResult(`❌ Échec : ${response.data.details?.error}`);
      }
    } catch (error: any) {
      setSshTestResult(`❌ Erreur : ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleDelete = async (agentId: string) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cet agent ?')) return;

    try {
      await axios.delete(`/api/v1/agents/${agentId}`);
      alert('Agent supprimé avec succès !');
      await loadAgents();
      setSelectedAgent(null);
    } catch (error: any) {
      alert(`Erreur : ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleReloadAgents = async () => {
    try {
      await axios.post('/api/v1/agents/reload');
      alert('Agents rechargés avec succès !');
      await loadAgents();
    } catch (error: any) {
      alert(`Erreur : ${error.response?.data?.detail || error.message}`);
    }
  };

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-4xl font-heading font-bold">Gestion des Agents</h1>
          <p className="text-secondary-text mt-1">
            Configurez les agents locaux et distants (SSH)
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleReloadAgents}
            className="px-4 py-2 bg-background border border-border-color text-primary-text rounded-lg hover:border-primary-accent/50 transition-all"
          >
            🔄 Recharger
          </button>
          <button
            onClick={handleCreateNew}
            className="px-4 py-2 bg-primary-accent text-background font-semibold rounded-lg hover:bg-primary-accent/90 transition-all"
          >
            ➕ Nouvel Agent
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Liste des agents */}
        <div className="lg:col-span-1">
          <div className="bg-card-bg border border-border-color rounded-lg p-4">
            <h2 className="text-xl font-heading font-semibold mb-4">Agents ({agents.length})</h2>
            <div className="space-y-2 max-h-[600px] overflow-y-auto">
              {agents.map(agent => (
                <button
                  key={agent.id}
                  onClick={() => handleSelectAgent(agent)}
                  className={`w-full text-left p-3 rounded-lg transition-all ${
                    selectedAgent?.id === agent.id
                      ? 'bg-primary-accent/20 border border-primary-accent'
                      : 'bg-background border border-border-color hover:border-primary-accent/50'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-2xl">{agent.icon}</span>
                    <div className="flex-1">
                      <p className="font-medium text-primary-text">{agent.name}</p>
                      <p className="text-xs text-secondary-text">{agent.role}</p>
                    </div>
                    {agent.is_remote && (
                      <span className="text-xs px-2 py-1 bg-blue/20 text-blue rounded">SSH</span>
                    )}
                  </div>
                  <div className="flex items-center justify-between text-xs text-secondary-text">
                    <span>{agent.query_count} requêtes</span>
                    <span className={agent.is_active ? 'text-green' : 'text-red'}>
                      {agent.is_active ? '● Actif' : '○ Inactif'}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Détails et édition */}
        <div className="lg:col-span-2">
          {(selectedAgent || isCreating) ? (
            <div className="bg-card-bg border border-border-color rounded-lg p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-heading font-semibold">
                  {isCreating ? 'Nouvel Agent' : 'Configuration de l\'Agent'}
                </h2>
                <div className="flex gap-2">
                  {!isEditing && !isCreating && (
                    <>
                      <button
                        onClick={() => setIsEditing(true)}
                        className="px-4 py-2 bg-background border border-border-color text-primary-text rounded-lg hover:border-primary-accent/50 transition-all"
                      >
                        ✏️ Éditer
                      </button>
                      {selectedAgent?.is_custom && (
                        <button
                          onClick={() => handleDelete(selectedAgent.id)}
                          className="px-4 py-2 bg-red/20 border border-red text-red rounded-lg hover:bg-red/30 transition-all"
                        >
                          🗑️ Supprimer
                        </button>
                      )}
                    </>
                  )}
                  {(isEditing || isCreating) && (
                    <>
                      <button
                        onClick={() => {
                          setIsEditing(false);
                          setIsCreating(false);
                          if (selectedAgent) handleSelectAgent(selectedAgent);
                        }}
                        className="px-4 py-2 bg-background border border-border-color text-secondary-text rounded-lg hover:border-border-color transition-all"
                      >
                        Annuler
                      </button>
                      <button
                        onClick={handleSave}
                        className="px-4 py-2 bg-primary-accent text-background font-semibold rounded-lg hover:bg-primary-accent/90 transition-all"
                      >
                        💾 Sauvegarder
                      </button>
                    </>
                  )}
                </div>
              </div>

              <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2">
                {/* Informations de base */}
                <div>
                  <label className="block text-sm font-medium text-primary-text mb-2">
                    ID de l'Agent {isCreating && <span className="text-red">*</span>}
                  </label>
                  <input
                    type="text"
                    value={formData.id}
                    onChange={(e) => setFormData({...formData, id: e.target.value})}
                    disabled={!isCreating}
                    className="w-full bg-input-background border border-border-color rounded-lg px-4 py-2 text-primary-text disabled:opacity-50"
                    placeholder="ex: MyCustomAgent"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-primary-text mb-2">
                      Nom <span className="text-red">*</span>
                    </label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      disabled={!isEditing && !isCreating}
                      className="w-full bg-input-background border border-border-color rounded-lg px-4 py-2 text-primary-text disabled:opacity-50"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-primary-text mb-2">
                      Rôle <span className="text-red">*</span>
                    </label>
                    <input
                      type="text"
                      value={formData.role}
                      onChange={(e) => setFormData({...formData, role: e.target.value})}
                      disabled={!isEditing && !isCreating}
                      className="w-full bg-input-background border border-border-color rounded-lg px-4 py-2 text-primary-text disabled:opacity-50"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-primary-text mb-2">
                    Objectif <span className="text-red">*</span>
                  </label>
                  <textarea
                    value={formData.goal}
                    onChange={(e) => setFormData({...formData, goal: e.target.value})}
                    disabled={!isEditing && !isCreating}
                    rows={2}
                    className="w-full bg-input-background border border-border-color rounded-lg px-4 py-2 text-primary-text disabled:opacity-50"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-primary-text mb-2">
                    Backstory <span className="text-red">*</span>
                  </label>
                  <textarea
                    value={formData.backstory}
                    onChange={(e) => setFormData({...formData, backstory: e.target.value})}
                    disabled={!isEditing && !isCreating}
                    rows={3}
                    className="w-full bg-input-background border border-border-color rounded-lg px-4 py-2 text-primary-text disabled:opacity-50"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-primary-text mb-2">
                    Prompt Système (Optionnel)
                  </label>
                  <textarea
                    value={formData.system_prompt}
                    onChange={(e) => setFormData({...formData, system_prompt: e.target.value})}
                    disabled={!isEditing && !isCreating}
                    rows={6}
                    className="w-full bg-input-background border border-border-color rounded-lg px-4 py-2 text-primary-text font-mono text-sm disabled:opacity-50"
                    placeholder="Si vide, un prompt par défaut sera généré..."
                  />
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-primary-text mb-2">
                      Namespace
                    </label>
                    <input
                      type="text"
                      value={formData.namespace}
                      onChange={(e) => setFormData({...formData, namespace: e.target.value})}
                      disabled={!isEditing && !isCreating}
                      className="w-full bg-input-background border border-border-color rounded-lg px-4 py-2 text-primary-text disabled:opacity-50"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-primary-text mb-2">
                      Icon
                    </label>
                    <input
                      type="text"
                      value={formData.icon}
                      onChange={(e) => setFormData({...formData, icon: e.target.value})}
                      disabled={!isEditing && !isCreating}
                      className="w-full bg-input-background border border-border-color rounded-lg px-4 py-2 text-primary-text disabled:opacity-50"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-primary-text mb-2">
                      Couleur
                    </label>
                    <input
                      type="color"
                      value={formData.color}
                      onChange={(e) => setFormData({...formData, color: e.target.value})}
                      disabled={!isEditing && !isCreating}
                      className="w-full h-10 bg-input-background border border-border-color rounded-lg disabled:opacity-50"
                    />
                  </div>
                </div>

                {/* Configuration SSH */}
                <div className="border-t border-border-color pt-4 mt-4">
                  <div className="flex items-center gap-3 mb-4">
                    <input
                      type="checkbox"
                      checked={formData.is_remote}
                      onChange={(e) => setFormData({...formData, is_remote: e.target.checked})}
                      disabled={!isEditing && !isCreating}
                      className="w-5 h-5"
                    />
                    <label className="text-lg font-medium text-primary-text">
                      Agent Distant (SSH)
                    </label>
                  </div>

                  {formData.is_remote && (
                    <div className="space-y-4 pl-8">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-primary-text mb-2">
                            Hôte SSH <span className="text-red">*</span>
                          </label>
                          <input
                            type="text"
                            value={formData.ssh_host}
                            onChange={(e) => setFormData({...formData, ssh_host: e.target.value})}
                            disabled={!isEditing && !isCreating}
                            className="w-full bg-input-background border border-border-color rounded-lg px-4 py-2 text-primary-text disabled:opacity-50"
                            placeholder="192.168.1.10 ou agent.example.com"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-primary-text mb-2">
                            Port SSH
                          </label>
                          <input
                            type="number"
                            value={formData.ssh_port}
                            onChange={(e) => setFormData({...formData, ssh_port: parseInt(e.target.value)})}
                            disabled={!isEditing && !isCreating}
                            className="w-full bg-input-background border border-border-color rounded-lg px-4 py-2 text-primary-text disabled:opacity-50"
                          />
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-primary-text mb-2">
                          Nom d'utilisateur <span className="text-red">*</span>
                        </label>
                        <input
                          type="text"
                          value={formData.ssh_username}
                          onChange={(e) => setFormData({...formData, ssh_username: e.target.value})}
                          disabled={!isEditing && !isCreating}
                          className="w-full bg-input-background border border-border-color rounded-lg px-4 py-2 text-primary-text disabled:opacity-50"
                          placeholder="root ou ubuntu"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-primary-text mb-2">
                          Mot de passe SSH (ou laissez vide pour utiliser une clé)
                        </label>
                        <input
                          type="password"
                          value={formData.ssh_password}
                          onChange={(e) => setFormData({...formData, ssh_password: e.target.value})}
                          disabled={!isEditing && !isCreating}
                          className="w-full bg-input-background border border-border-color rounded-lg px-4 py-2 text-primary-text disabled:opacity-50"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-primary-text mb-2">
                          Chemin de la clé privée SSH (optionnel)
                        </label>
                        <input
                          type="text"
                          value={formData.ssh_key_path}
                          onChange={(e) => setFormData({...formData, ssh_key_path: e.target.value})}
                          disabled={!isEditing && !isCreating}
                          className="w-full bg-input-background border border-border-color rounded-lg px-4 py-2 text-primary-text disabled:opacity-50"
                          placeholder="/home/user/.ssh/id_rsa"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-primary-text mb-2">
                          Endpoint de l'agent distant
                        </label>
                        <input
                          type="text"
                          value={formData.ssh_endpoint}
                          onChange={(e) => setFormData({...formData, ssh_endpoint: e.target.value})}
                          disabled={!isEditing && !isCreating}
                          className="w-full bg-input-background border border-border-color rounded-lg px-4 py-2 text-primary-text disabled:opacity-50"
                          placeholder="/process ou http://localhost:8000/api/process"
                        />
                      </div>

                      {(isEditing || isCreating) && (
                        <div>
                          <button
                            onClick={handleTestSSH}
                            className="px-4 py-2 bg-blue/20 border border-blue text-blue rounded-lg hover:bg-blue/30 transition-all"
                          >
                            🔌 Tester la Connexion SSH
                          </button>
                          {sshTestResult && (
                            <p className="mt-2 text-sm text-secondary-text">{sshTestResult}</p>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-card-bg border border-border-color rounded-lg p-12 text-center">
              <div className="text-6xl mb-4">🤖</div>
              <h3 className="text-xl font-semibold text-primary-text mb-2">
                Sélectionnez un Agent
              </h3>
              <p className="text-secondary-text">
                Choisissez un agent dans la liste ou créez-en un nouveau
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminAgents;
