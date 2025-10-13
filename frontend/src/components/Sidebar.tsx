import React from 'react';
import { Page } from '../App';

interface SidebarProps {
  currentPage: Page;
  setCurrentPage: (page: Page) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ currentPage, setCurrentPage }) => {
  const menuItems = [
    { page: Page.DASHBOARD, label: 'Dashboard', icon: '📊' },
    { page: Page.UPLOAD, label: 'Upload', icon: '📤' },
    { page: Page.EXPLORE, label: 'Explorer', icon: '🔍' },
    { page: Page.PLAYGROUND, label: 'Playground', icon: '🤖' },
    { page: Page.MONITORING, label: 'Monitoring', icon: '📈' },
    { page: Page.ADMIN, label: 'Admin', icon: '⚙️' },
    { page: Page.ADMIN_AGENTS, label: 'Agents', icon: '🧠' },
  ];

  return (
    <aside className="w-64 bg-card-bg border-r border-border-color flex flex-col">
      <div className="p-6 border-b border-border-color">
        <h1 className="text-2xl font-heading font-bold text-primary-accent">
          AI CFO Suite
        </h1>
        <p className="text-sm text-secondary-text mt-1">Phoenix v2.0</p>
      </div>
      
      <nav className="flex-1 p-4">
        {menuItems.map((item) => (
          <button
            key={item.page}
            onClick={() => setCurrentPage(item.page)}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition-all ${
              currentPage === item.page
                ? 'bg-primary-accent/10 text-primary-accent border border-primary-accent/30'
                : 'text-secondary-text hover:bg-card-bg hover:text-primary-text'
            }`}
          >
            <span className="text-xl">{item.icon}</span>
            <span className="font-medium">{item.label}</span>
          </button>
        ))}
      </nav>
      
      <div className="p-4 border-t border-border-color">
        <div className="text-xs text-secondary-text">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-2 h-2 rounded-full bg-green animate-pulse"></div>
            <span>Backend Online</span>
          </div>
          <p>Multi-Agent System Active</p>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
