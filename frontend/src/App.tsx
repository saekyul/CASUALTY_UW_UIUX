import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { fetchStatus } from './services/api';
import './App.css';

// Pages
import Home from './pages/Home';
import Emails from './pages/Emails';
import Data from './pages/Data';
import Settings from './pages/Settings';

function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkConnection = async () => {
      try {
        const status = await fetchStatus();
        setIsConnected(status.status === 'healthy' || status.status === 'degraded');
      } catch (error) {
        console.error('Failed to connect to backend:', error);
        setIsConnected(false);
      } finally {
        setLoading(false);
      }
    };

    checkConnection();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="mb-4 text-xl">Loading...</div>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="App min-h-screen bg-gray-50">
        {!isConnected && (
          <div className="bg-red-500 text-white p-4 text-center">
            Warning: Backend connection failed
          </div>
        )}

        <nav className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <h1 className="text-xl font-bold">CASUALTY LLM PoC</h1>
              </div>
              <div className="flex items-center space-x-4">
                <a href="/" className="text-gray-700 hover:text-gray-900">Home</a>
                <a href="/emails" className="text-gray-700 hover:text-gray-900">Emails</a>
                <a href="/data" className="text-gray-700 hover:text-gray-900">Data</a>
                <a href="/settings" className="text-gray-700 hover:text-gray-900">Settings</a>
              </div>
            </div>
          </div>
        </nav>

        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/emails" element={<Emails />} />
          <Route path="/data" element={<Data />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
