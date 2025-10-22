import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FiClock,
  FiChevronDown,
  FiChevronUp,
  FiStar,
  FiTrash2,
  FiMessageCircle,
  FiSearch,
  FiFileText,
  FiBarChart,
} from 'react-icons/fi';
import { useHistory, useDeleteHistoryEntry, useUpdateHistoryEntry } from '../hooks/useHistory';
import { formatDistanceToNow } from 'date-fns';
import { fr } from 'date-fns/locale';

interface HistoryPanelProps {
  collapsed: boolean;
  onSelectEntry?: (entryId: string) => void;
}

const HistoryPanel: React.FC<HistoryPanelProps> = ({ collapsed, onSelectEntry }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [filter, setFilter] = useState<string | undefined>(undefined);
  
  const { data: history, isLoading } = useHistory(10, filter);
  const deleteMutation = useDeleteHistoryEntry();
  const updateMutation = useUpdateHistoryEntry();

  const getIcon = (type: string) => {
    switch (type) {
      case 'chat':
        return FiMessageCircle;
      case 'query':
        return FiSearch;
      case 'document':
        return FiFileText;
      case 'analysis':
        return FiBarChart;
      default:
        return FiClock;
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'chat':
        return 'Chat';
      case 'query':
        return 'Requête';
      case 'document':
        return 'Document';
      case 'analysis':
        return 'Analyse';
      default:
        return type;
    }
  };

  const handleToggleFavorite = (id: string, currentState: boolean) => {
    updateMutation.mutate({
      id,
      data: { is_favorite: !currentState },
    });
  };

  const handleDelete = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Supprimer cette entrée de l\'historique ?')) {
      deleteMutation.mutate(id);
    }
  };

  if (collapsed) {
    return (
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex justify-center p-2 hover:bg-background rounded-lg transition-colors text-secondary-text hover:text-primary-text"
        title="Historique"
      >
        <FiClock size={20} />
      </button>
    );
  }

  return (
    <div className="mb-4">
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between px-4 py-2 hover:bg-background rounded-lg transition-colors text-secondary-text hover:text-primary-text"
      >
        <div className="flex items-center gap-2">
          <FiClock size={18} />
          <span className="text-sm font-medium">Historique</span>
        </div>
        {isExpanded ? <FiChevronUp size={16} /> : <FiChevronDown size={16} />}
      </button>

      {/* History List */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="mt-2 space-y-1 max-h-64 overflow-y-auto">
              {isLoading ? (
                <div className="px-4 py-2 text-xs text-secondary-text">
                  Chargement...
                </div>
              ) : history && history.length > 0 ? (
                history.map((entry) => {
                  const Icon = getIcon(entry.type);
                  return (
                    <motion.div
                      key={entry.id}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="group relative"
                    >
                      <button
                        onClick={() => onSelectEntry?.(entry.id)}
                        className="w-full text-left px-3 py-2 hover:bg-background rounded-lg transition-colors"
                      >
                        <div className="flex items-start gap-2">
                          <Icon size={14} className="text-secondary-text mt-0.5 flex-shrink-0" />
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-1 mb-0.5">
                              <p className="text-xs font-medium text-primary-text truncate">
                                {entry.title}
                              </p>
                              {entry.is_favorite && (
                                <FiStar size={10} className="text-yellow fill-yellow flex-shrink-0" />
                              )}
                            </div>
                            <p className="text-xs text-secondary-text truncate">
                              {entry.preview}
                            </p>
                            <p className="text-xs text-tertiary-text mt-0.5">
                              {formatDistanceToNow(new Date(entry.created_at), {
                                addSuffix: true,
                                locale: fr,
                              })}
                            </p>
                          </div>
                        </div>
                      </button>

                      {/* Actions (visible on hover) */}
                      <div className="absolute right-2 top-2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleToggleFavorite(entry.id, entry.is_favorite);
                          }}
                          className="p-1 hover:bg-card-bg rounded transition-colors"
                          title={entry.is_favorite ? 'Retirer des favoris' : 'Ajouter aux favoris'}
                        >
                          <FiStar
                            size={12}
                            className={entry.is_favorite ? 'text-yellow fill-yellow' : 'text-secondary-text'}
                          />
                        </button>
                        <button
                          onClick={(e) => handleDelete(entry.id, e)}
                          className="p-1 hover:bg-card-bg rounded transition-colors text-secondary-text hover:text-red"
                          title="Supprimer"
                        >
                          <FiTrash2 size={12} />
                        </button>
                      </div>
                    </motion.div>
                  );
                })
              ) : (
                <div className="px-4 py-2 text-xs text-secondary-text">
                  Aucun historique
                </div>
              )}
            </div>

            {/* Filter Tabs */}
            <div className="mt-2 px-2 flex gap-1 text-xs">
              <button
                onClick={() => setFilter(undefined)}
                className={`px-2 py-1 rounded transition-colors ${
                  !filter
                    ? 'bg-primary-accent/20 text-primary-accent'
                    : 'text-secondary-text hover:bg-background'
                }`}
              >
                Tout
              </button>
              <button
                onClick={() => setFilter('chat')}
                className={`px-2 py-1 rounded transition-colors ${
                  filter === 'chat'
                    ? 'bg-primary-accent/20 text-primary-accent'
                    : 'text-secondary-text hover:bg-background'
                }`}
              >
                Chat
              </button>
              <button
                onClick={() => setFilter('query')}
                className={`px-2 py-1 rounded transition-colors ${
                  filter === 'query'
                    ? 'bg-primary-accent/20 text-primary-accent'
                    : 'text-secondary-text hover:bg-background'
                }`}
              >
                Requêtes
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default HistoryPanel;

