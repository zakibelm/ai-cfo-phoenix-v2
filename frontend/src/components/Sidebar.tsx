import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FiHome,
  FiFileText,
  FiSearch,
  FiCode,
  FiActivity,
  FiSettings,
  FiCpu,
  FiMenu,
  FiX,
  FiCircle,
  FiLogOut,
  FiUser,
} from 'react-icons/fi';
import { Page } from '../App';
import { useStore } from '../store/useStore';
import { useLogout, useCurrentUser } from '../hooks/useAuth';
import HistoryPanel from './HistoryPanel';

interface SidebarProps {
  currentPage: Page;
  setCurrentPage: (page: Page) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ currentPage, setCurrentPage }) => {
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const { sidebarCollapsed, toggleSidebar, user } = useStore();
  const { data: currentUser } = useCurrentUser();
  const logoutMutation = useLogout();

  const displayUser = currentUser || user;

  const menuItems = [
    { page: Page.DASHBOARD, label: 'Dashboard', icon: FiHome },
    { page: Page.DOCUMENTS, label: 'Documents', icon: FiFileText },
    { page: Page.EXPLORE, label: 'Explorer', icon: FiSearch },
    { page: Page.PLAYGROUND, label: 'Playground', icon: FiCode },
    { page: Page.MONITORING, label: 'Monitoring', icon: FiActivity },
    { page: Page.ADMIN, label: 'Admin', icon: FiSettings },
    { page: Page.ADMIN_AGENTS, label: 'Agents', icon: FiCpu },
  ];

  const handleNavigation = (page: Page) => {
    setCurrentPage(page);
    setIsMobileOpen(false);
  };

  const handleLogout = () => {
    logoutMutation.mutate();
  };

  const sidebarVariants = {
    open: { width: '16rem' },
    collapsed: { width: '5rem' },
  };

  const itemVariants = {
    open: { opacity: 1, x: 0 },
    collapsed: { opacity: 0, x: -20 },
  };

  return (
    <>
      {/* Mobile Menu Button */}
      <button
        onClick={() => setIsMobileOpen(!isMobileOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-card-bg border border-border-color rounded-lg text-primary-text hover:bg-background transition-colors"
      >
        {isMobileOpen ? <FiX size={24} /> : <FiMenu size={24} />}
      </button>

      {/* Mobile Overlay */}
      <AnimatePresence>
        {isMobileOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setIsMobileOpen(false)}
            className="lg:hidden fixed inset-0 bg-black/50 z-40"
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.aside
        initial={false}
        animate={sidebarCollapsed ? 'collapsed' : 'open'}
        variants={sidebarVariants}
        transition={{ duration: 0.3, ease: 'easeInOut' }}
        className={`
          fixed lg:relative inset-y-0 left-0 z-40
          ${isMobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
          bg-card-bg border-r border-border-color flex flex-col
          transition-transform duration-300 ease-in-out
        `}
        style={{ width: sidebarCollapsed ? '5rem' : '16rem' }}
      >
        {/* Header */}
        <div className="p-6 border-b border-border-color">
          <div className="flex items-center justify-between">
            {!sidebarCollapsed && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <h1 className="text-2xl font-bold text-gradient-primary">
                  AI CFO Suite
                </h1>
                <p className="text-sm text-secondary-text mt-1">Phoenix v3.1</p>
              </motion.div>
            )}
            
            {/* Desktop Toggle */}
            <button
              onClick={toggleSidebar}
              className="hidden lg:block p-2 hover:bg-background rounded-lg transition-colors text-secondary-text hover:text-primary-text"
            >
              <FiMenu size={20} />
            </button>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 overflow-y-auto">
          {menuItems.map((item, index) => {
            const Icon = item.icon;
            const isActive = currentPage === item.page;

            return (
              <motion.button
                key={item.page}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                onClick={() => handleNavigation(item.page)}
                className={`
                  w-full flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition-all
                  ${isActive
                    ? 'bg-primary-accent/10 text-primary-accent border border-primary-accent/30 shadow-glow'
                    : 'text-secondary-text hover:bg-background hover:text-primary-text'
                  }
                  ${sidebarCollapsed ? 'justify-center' : ''}
                `}
                title={sidebarCollapsed ? item.label : ''}
              >
                <Icon size={20} className="flex-shrink-0" />
                
                <AnimatePresence>
                  {!sidebarCollapsed && (
                    <motion.span
                      variants={itemVariants}
                      initial="collapsed"
                      animate="open"
                      exit="collapsed"
                      className="font-medium"
                    >
                      {item.label}
                    </motion.span>
                  )}
                </AnimatePresence>
              </motion.button>
            );
          })}
        </nav>

        {/* History Panel */}
        <div className="px-4 border-t border-border-color pt-4">
          <HistoryPanel collapsed={sidebarCollapsed} />
        </div>

        {/* User Profile & Logout */}
        <div className="p-4 border-t border-border-color">
          {!sidebarCollapsed ? (
            <div className="space-y-3">
              {/* User Info */}
              {displayUser && (
                <div className="flex items-center gap-3 p-3 bg-background rounded-lg">
                  <div className="w-10 h-10 rounded-full bg-primary-accent/20 flex items-center justify-center">
                    <FiUser className="text-primary-accent" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-primary-text truncate">
                      {displayUser.full_name}
                    </p>
                    <p className="text-xs text-secondary-text truncate">
                      {displayUser.email}
                    </p>
                  </div>
                </div>
              )}

              {/* Logout Button */}
              <button
                onClick={handleLogout}
                disabled={logoutMutation.isPending}
                className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-secondary-text hover:bg-background hover:text-red transition-all"
              >
                <FiLogOut size={20} />
                <span className="font-medium">
                  {logoutMutation.isPending ? 'Déconnexion...' : 'Déconnexion'}
                </span>
              </button>

              {/* Status */}
              <div className="text-xs text-secondary-text">
                <div className="flex items-center gap-2 mb-1">
                  <FiCircle className="text-green animate-pulse" size={12} />
                  <span>Backend Online</span>
                </div>
                <p>Multi-Agent System Active</p>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              {/* User Avatar */}
              <div className="flex justify-center">
                <div className="w-10 h-10 rounded-full bg-primary-accent/20 flex items-center justify-center">
                  <FiUser className="text-primary-accent" />
                </div>
              </div>

              {/* Logout Icon */}
              <button
                onClick={handleLogout}
                disabled={logoutMutation.isPending}
                className="w-full flex justify-center p-2 rounded-lg text-secondary-text hover:bg-background hover:text-red transition-all"
                title="Déconnexion"
              >
                <FiLogOut size={20} />
              </button>

              {/* Status */}
              <div className="flex justify-center">
                <FiCircle className="text-green animate-pulse" size={12} />
              </div>
            </div>
          )}
        </div>
      </motion.aside>
    </>
  );
};

export default Sidebar;

