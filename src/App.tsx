import React from 'react';
import Dashboard from './components/Dashboard';
import { ApiProvider } from './context/ApiContext';

function App() {
  return (
    <ApiProvider>
      <div className="min-h-screen bg-gray-50">
        <Dashboard />
      </div>
    </ApiProvider>
  );
}

export default App;