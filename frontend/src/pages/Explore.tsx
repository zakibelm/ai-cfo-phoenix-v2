import React, { useState } from 'react';
import { Document } from '../App';

interface ExploreProps {
  documents: Document[];
  ragContext: Document | null;
  setRagContext: (doc: Document | null) => void;
}

const Explore: React.FC<ExploreProps> = ({ documents, ragContext, setRagContext }) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredDocuments = documents.filter(doc =>
    doc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    doc.assigned_agents.some(agent => agent.toLowerCase().includes(searchTerm.toLowerCase())) ||
    doc.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div className="p-8">
      <h1 className="text-4xl font-heading font-bold mb-2">RAG Explorer</h1>
      <p className="text-secondary-text mb-8">
        Explorez et gérez vos documents vectorisés
      </p>

      <input
        type="text"
        placeholder="Rechercher par nom, agent ou tag..."
        className="w-full bg-input-background border border-border-color rounded-lg px-4 py-3 text-primary-text placeholder-secondary-text focus:outline-none focus:border-primary-accent mb-6"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />

      <div className="bg-card-bg border border-border-color rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-background border-b border-border-color">
              <tr>
                <th className="px-6 py-4 text-left text-sm font-semibold text-primary-text">
                  Document
                </th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-primary-text">
                  Status
                </th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-primary-text">
                  Date
                </th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-primary-text">
                  Agents
                </th>
                <th className="px-6 py-4 text-left text-sm font-semibold text-primary-text">
                  Tags
                </th>
                <th className="px-6 py-4 text-center text-sm font-semibold text-primary-text">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              {filteredDocuments.length > 0 ? (
                filteredDocuments.map(doc => {
                  const isSelected = ragContext?.id === doc.id;
                  return (
                    <tr
                      key={doc.id}
                      className={`border-b border-border-color hover:bg-background/50 transition-colors ${
                        isSelected ? 'bg-primary-accent/10' : ''
                      }`}
                    >
                      <td className="px-6 py-4 font-medium text-primary-text">
                        {doc.name}
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 rounded text-xs ${
                          doc.status === 'Processed' ? 'bg-green/20 text-green' :
                          doc.status === 'In Progress' ? 'bg-yellow/20 text-yellow' :
                          'bg-red/20 text-red'
                        }`}>
                          {doc.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-secondary-text text-sm">
                        {doc.uploaded}
                      </td>
                      <td className="px-6 py-4 text-secondary-text text-sm">
                        {doc.assigned_agents.join(', ') || 'Aucun'}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex gap-1 flex-wrap">
                          {doc.tags.map(tag => (
                            <span
                              key={tag}
                              className="px-2 py-1 bg-background rounded text-xs text-secondary-text"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-center">
                        <button
                          onClick={() => setRagContext(isSelected ? null : doc)}
                          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                            isSelected
                              ? 'bg-primary-accent/20 text-primary-accent border border-primary-accent'
                              : 'bg-background text-secondary-text border border-border-color hover:border-primary-accent/50'
                          }`}
                        >
                          {isSelected ? '✓ Contexte Actif' : 'Utiliser comme Contexte'}
                        </button>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center">
                    <div className="text-6xl mb-4">📁</div>
                    <h3 className="text-xl font-semibold text-primary-text mb-2">
                      Aucun Document Trouvé
                    </h3>
                    <p className="text-secondary-text">
                      Vos documents ingérés apparaîtront ici
                    </p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Explore;
