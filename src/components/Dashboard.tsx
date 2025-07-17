import React, { useState, useEffect } from 'react';
import { useApi } from '../context/ApiContext';
import ApiConfig from './ApiConfig';
import Overview from './Overview';
import CountyAnalysis from './CountyAnalysis';
import RentAnalysis from './RentAnalysis';
import PropertySearch from './PropertySearch';
import { BarChart3, Home, Search, TrendingUp } from 'lucide-react';

const Dashboard: React.FC = () => {
  const { isConfigured } = useApi();
  const [activeTab, setActiveTab] = useState('overview');

  if (!isConfigured) {
    return <ApiConfig />;
  }

  const tabs = [
    { id: 'overview', name: 'Overview', icon: BarChart3 },
    { id: 'county', name: 'County Analysis', icon: TrendingUp },
    { id: 'rent', name: 'Rent Analysis', icon: Home },
    { id: 'search', name: 'Property Search', icon: Search },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Property Market Dashboard</h1>
              <p className="text-gray-600 mt-1">Irish Property Data Analytics</p>
            </div>
          </div>
        </div>
      </header>

      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center px-3 py-4 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {tab.name}
                </button>
              );
            })}
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && <Overview />}
        {activeTab === 'county' && <CountyAnalysis />}
        {activeTab === 'rent' && <RentAnalysis />}
        {activeTab === 'search' && <PropertySearch />}
      </main>
    </div>
  );
};

export default Dashboard;