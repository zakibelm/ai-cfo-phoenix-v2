import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FiMessageCircle,
  FiX,
  FiSend,
  FiMinimize2,
  FiMaximize2,
  FiRefreshCw,
  FiCopy,
  FiCheck,
} from 'react-icons/fi';
import { useMutation } from '@tanstack/react-query';
import { useCreateHistoryEntry } from '../hooks/useHistory';
import axios from 'axios';
import toast from 'react-hot-toast';
import ReactMarkdown from 'react-markdown';
import { Page } from '../App';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
  enhanced_prompt?: string;
  suggestions?: string[];
}

interface ChatAssistantProps {
  currentPage: Page;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const ChatAssistant: React.FC<ChatAssistantProps> = ({ currentPage }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: "👋 Bonjour ! Je suis votre assistant IA. Comment puis-je vous aider aujourd'hui ?",
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const createHistoryMutation = useCreateHistoryEntry();

  const chatMutation = useMutation({
    mutationFn: async (message: string) => {
      const response = await axios.post(`${API_BASE_URL}/assistant/chat`, {
        message,
        conversation_history: messages.slice(-6).map(m => ({
          role: m.role,
          content: m.content,
        })),
        user_context: {
          current_page: currentPage,
        },
      });
      return response.data;
    },
    onSuccess: (data) => {
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: data.message,
          enhanced_prompt: data.enhanced_prompt,
          suggestions: data.suggestions,
          timestamp: data.timestamp,
        },
      ]);
    },
    onError: (error: any) => {
      toast.error('Erreur de communication avec l\'assistant');
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: "Désolé, je rencontre un problème technique. Pouvez-vous réessayer ?",
        },
      ]);
    },
  });

  const handleSend = () => {
    if (!inputValue.trim() || chatMutation.isPending) return;

    const userMessage = inputValue.trim();
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setInputValue('');
    chatMutation.mutate(userMessage);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInputValue(suggestion);
    inputRef.current?.focus();
  };

  const handleCopy = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
    toast.success('Copié dans le presse-papier');
  };

  const handleReset = () => {
    // Save current conversation to history before resetting
    if (messages.length > 1) {
      const firstUserMessage = messages.find(m => m.role === 'user');
      if (firstUserMessage) {
        createHistoryMutation.mutate({
          title: firstUserMessage.content.substring(0, 50) + '...',
          type: 'chat',
          content: { messages },
          tags: ['assistant'],
        });
      }
    }
    
    setMessages([
      {
        role: 'assistant',
        content: "👋 Conversation réinitialisée. Comment puis-je vous aider ?",
      },
    ]);
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (isOpen && !isMinimized) {
      inputRef.current?.focus();
    }
  }, [isOpen, isMinimized]);

  return (
    <>
      {/* Floating Button */}
      <AnimatePresence>
        {!isOpen && (
          <motion.button
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={() => setIsOpen(true)}
            className="fixed bottom-6 right-6 z-50 w-14 h-14 bg-gradient-primary rounded-full shadow-glow-strong flex items-center justify-center text-white hover:shadow-glow transition-all"
          >
            <FiMessageCircle size={24} />
          </motion.button>
        )}
      </AnimatePresence>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{
              opacity: 1,
              y: 0,
              scale: 1,
              height: isMinimized ? 'auto' : '600px',
            }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="fixed bottom-6 right-6 z-50 w-96 max-w-[calc(100vw-3rem)] glass-strong rounded-xl shadow-2xl flex flex-col overflow-hidden"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-border-color bg-card-bg/50">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green rounded-full animate-pulse" />
                <h3 className="font-semibold text-primary-text">Assistant IA</h3>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleReset}
                  className="p-1.5 hover:bg-background rounded transition-colors text-secondary-text hover:text-primary-text"
                  title="Réinitialiser"
                >
                  <FiRefreshCw size={16} />
                </button>
                <button
                  onClick={() => setIsMinimized(!isMinimized)}
                  className="p-1.5 hover:bg-background rounded transition-colors text-secondary-text hover:text-primary-text"
                >
                  {isMinimized ? <FiMaximize2 size={16} /> : <FiMinimize2 size={16} />}
                </button>
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-1.5 hover:bg-background rounded transition-colors text-secondary-text hover:text-primary-text"
                >
                  <FiX size={16} />
                </button>
              </div>
            </div>

            {/* Messages */}
            {!isMinimized && (
              <>
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {messages.map((message, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[80%] rounded-lg p-3 ${
                          message.role === 'user'
                            ? 'bg-primary-accent text-white'
                            : 'bg-background border border-border-color'
                        }`}
                      >
                        <div className="prose prose-sm prose-invert max-w-none">
                          <ReactMarkdown>{message.content}</ReactMarkdown>
                        </div>

                        {/* Enhanced Prompt */}
                        {message.enhanced_prompt && (
                          <div className="mt-2 p-2 bg-card-bg/50 rounded border border-primary-accent/30">
                            <p className="text-xs text-secondary-text mb-1">💡 Prompt amélioré :</p>
                            <p className="text-sm">{message.enhanced_prompt}</p>
                            <button
                              onClick={() => handleCopy(message.enhanced_prompt!, index)}
                              className="mt-1 text-xs text-primary-accent hover:underline flex items-center gap-1"
                            >
                              {copiedIndex === index ? (
                                <>
                                  <FiCheck size={12} /> Copié
                                </>
                              ) : (
                                <>
                                  <FiCopy size={12} /> Copier
                                </>
                              )}
                            </button>
                          </div>
                        )}

                        {/* Suggestions */}
                        {message.suggestions && message.suggestions.length > 0 && (
                          <div className="mt-2 space-y-1">
                            <p className="text-xs text-secondary-text">Suggestions :</p>
                            {message.suggestions.map((suggestion, i) => (
                              <button
                                key={i}
                                onClick={() => handleSuggestionClick(suggestion)}
                                className="block w-full text-left text-xs p-2 bg-card-bg/30 hover:bg-card-bg rounded border border-border-color hover:border-primary-accent/50 transition-colors"
                              >
                                {suggestion}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    </motion.div>
                  ))}

                  {chatMutation.isPending && (
                    <div className="flex justify-start">
                      <div className="bg-background border border-border-color rounded-lg p-3">
                        <div className="flex gap-1">
                          <div className="w-2 h-2 bg-primary-accent rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                          <div className="w-2 h-2 bg-primary-accent rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                          <div className="w-2 h-2 bg-primary-accent rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                        </div>
                      </div>
                    </div>
                  )}

                  <div ref={messagesEndRef} />
                </div>

                {/* Input */}
                <div className="p-4 border-t border-border-color bg-card-bg/50">
                  <div className="flex gap-2">
                    <input
                      ref={inputRef}
                      type="text"
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Posez votre question..."
                      className="flex-1 px-3 py-2 bg-background border border-border-color rounded-lg text-primary-text placeholder-secondary-text focus:outline-none focus:ring-2 focus:ring-primary-accent focus:border-transparent text-sm"
                      disabled={chatMutation.isPending}
                    />
                    <button
                      onClick={handleSend}
                      disabled={!inputValue.trim() || chatMutation.isPending}
                      className="p-2 bg-primary-accent text-white rounded-lg hover:bg-primary-accent/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      <FiSend size={18} />
                    </button>
                  </div>
                </div>
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default ChatAssistant;

