import React, { useState, useRef, useEffect } from 'react';
import { Document } from '../App';
import { sendQuery, checkBackendHealth } from '../services/apiService';

interface PlaygroundProps {
  ragContext: Document | null;
  setRagContext: (doc: Document | null) => void;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  agent?: string;
  sources?: any[];
}

const Playground: React.FC<PlaygroundProps> = ({ ragContext, setRagContext }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'init',
      role: 'assistant',
      agent: 'Oracle',
      content: "Bienvenue dans l'AI CFO Suite ! Je suis Oracle, votre orchestrateur IA. Comment puis-je vous aider aujourd'hui ?\n\nJe peux maintenant me connecter à nos agents internes pour traiter vos demandes. Essayez de me poser une question sur la fiscalité, la comptabilité ou les prévisions financières."
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isBackendOnline, setIsBackendOnline] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const checkHealth = async () => {
      const online = await checkBackendHealth();
      setIsBackendOnline(online);
    };
    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading || !isBackendOnline) return;

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: input
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await sendQuery(input, ragContext);

      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        agent: response.agent,
        content: response.response,
        sources: response.sources
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error: any) {
      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        agent: 'System',
        content: `Désolé, une erreur est survenue : ${error.message}`
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-screen flex flex-col">
      <div className="p-6 border-b border-border-color">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-heading font-bold">AI Playground</h1>
            <p className="text-secondary-text mt-1">
              Interagissez avec les agents de l'AI CFO Suite
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className={`flex items-center gap-2 px-3 py-2 rounded-lg ${
              isBackendOnline ? 'bg-green/20 text-green' : 'bg-red/20 text-red'
            }`}>
              <div className={`w-2 h-2 rounded-full ${
                isBackendOnline ? 'bg-green' : 'bg-red'
              } animate-pulse`}></div>
              <span className="text-sm font-medium">
                {isBackendOnline ? 'Backend En Ligne' : 'Backend Hors Ligne'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {ragContext && (
        <div className="px-6 py-3 bg-primary-accent/10 border-b border-primary-accent/30 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-primary-accent">📄</span>
            <span className="text-sm text-primary-text">
              Contexte actif : <strong>{ragContext.name}</strong>
            </span>
          </div>
          <button
            onClick={() => setRagContext(null)}
            className="text-sm text-secondary-text hover:text-primary-accent transition-colors"
          >
            ✕ Effacer
          </button>
        </div>
      )}

      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map(msg => (
          <div
            key={msg.id}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-2xl rounded-lg p-4 ${
                msg.role === 'user'
                  ? 'bg-primary-accent text-background'
                  : 'bg-card-bg border border-border-color'
              }`}
            >
              {msg.agent && (
                <div className="text-xs font-semibold mb-2 text-primary-accent">
                  {msg.agent}
                </div>
              )}
              <div className="whitespace-pre-wrap">{msg.content}</div>
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-3 pt-3 border-t border-border-color">
                  <div className="text-xs text-secondary-text">
                    Sources : {msg.sources.length} documents consultés
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-card-bg border border-border-color rounded-lg p-4">
              <div className="flex gap-2">
                <div className="w-2 h-2 bg-primary-accent rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-primary-accent rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-primary-accent rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-6 border-t border-border-color">
        <form onSubmit={handleSendMessage} className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={isBackendOnline ? "Posez votre question..." : "Backend hors ligne..."}
            disabled={isLoading || !isBackendOnline}
            className="flex-1 bg-input-background border border-border-color rounded-lg px-4 py-3 text-primary-text placeholder-secondary-text focus:outline-none focus:border-primary-accent disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim() || !isBackendOnline}
            className="bg-primary-accent text-background font-semibold px-6 py-3 rounded-lg hover:bg-primary-accent/90 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? '⏳' : '📤'} Envoyer
          </button>
        </form>
      </div>
    </div>
  );
};

export default Playground;
