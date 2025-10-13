import React, { useState } from 'react';
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import Explore from './pages/Explore';
import Playground from './pages/Playground';
import Admin from './pages/Admin';
import AdminAgents from './pages/AdminAgents';
import Monitoring from './pages/Monitoring';
import Sidebar from './components/Sidebar';

export enum Page {
  DASHBOARD = 'Dashboard',
  UPLOAD = 'Upload',
  EXPLORE = 'Explore',
  PLAYGROUND = 'Playground',
  ADMIN = 'Admin',
  ADMIN_AGENTS = 'AdminAgents',
  MONITORING = 'Monitoring',
}

export interface Document {
  id: string;
  name: string;
  status: 'Processed' | 'In Progress' | 'Queued' | 'Failed';
  uploaded: string;
  assigned_agents: string[];
  tags: string[];
  doctype: string;
  country: string;
}

function App() {
  const [currentPage, setCurrentPage] = useState<Page>(Page.DASHBOARD);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [ragContext, setRagContext] = useState<Document | null>(null);

  const addDocument = (doc: Document) => {
    setDocuments(prev => [doc, ...prev]);
  };

  const renderPage = () => {
    switch (currentPage) {
      case Page.DASHBOARD:
        return <Dashboard documents={documents} />;
      case Page.UPLOAD:
        return <Upload addDocument={addDocument} />;
      case Page.EXPLORE:
        return <Explore documents={documents} ragContext={ragContext} setRagContext={setRagContext} />;
      case Page.PLAYGROUND:
        return <Playground ragContext={ragContext} setRagContext={setRagContext} />;
      case Page.ADMIN:
        return <Admin />;
      case Page.ADMIN_AGENTS:
        return <AdminAgents />;
      case Page.MONITORING:
        return <Monitoring />;
      default:
        return <Dashboard documents={documents} />;
    }
  };

  return (
    <div className="flex h-screen bg-background">
      <Sidebar currentPage={currentPage} setCurrentPage={setCurrentPage} />
      <main className="flex-1 overflow-auto">
        {renderPage()}
      </main>
    </div>
  );
}

export default App;
