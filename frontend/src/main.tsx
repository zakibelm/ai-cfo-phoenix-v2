import React, { useState } from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import { LoadingScreen } from './components/LoadingScreen.tsx'
import './index.css'

const Root = () => {
  const [isBackendReady, setIsBackendReady] = useState(false);

  if (!isBackendReady) {
    return <LoadingScreen onReady={() => setIsBackendReady(true)} />;
  }

  return <App />;
};

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>,
)

