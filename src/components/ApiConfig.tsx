import React, { useState } from 'react';
import { useApi } from '../context/ApiContext';
import { Key, Globe, Server } from 'lucide-react';

const ApiConfig: React.FC = () => {
  const { config, setConfig } = useApi();
  const [formData, setFormData] = useState({
    apiKey: config.apiKey,
    domain: config.domain,
    baseUrl: config.baseUrl
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setConfig(formData);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <div className="mx-auto h-12 w-12 bg-primary-100 rounded-full flex items-center justify-center">
            <Server className="h-6 w-6 text-primary-600" />
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Configure API Access
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Enter your ippi.io API credentials to access property data
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label htmlFor="apiKey" className="block text-sm font-medium text-gray-700 mb-1">
                <Key className="inline w-4 h-4 mr-1" />
                API Key
              </label>
              <input
                id="apiKey"
                name="apiKey"
                type="password"
                required
                value={formData.apiKey}
                onChange={(e) => setFormData({ ...formData, apiKey: e.target.value })}
                className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
                placeholder="Enter your API key"
              />
            </div>
            
            <div>
              <label htmlFor="domain" className="block text-sm font-medium text-gray-700 mb-1">
                <Globe className="inline w-4 h-4 mr-1" />
                Domain
              </label>
              <input
                id="domain"
                name="domain"
                type="text"
                required
                value={formData.domain}
                onChange={(e) => setFormData({ ...formData, domain: e.target.value })}
                className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
                placeholder="your-domain.com"
              />
            </div>
            
            <div>
              <label htmlFor="baseUrl" className="block text-sm font-medium text-gray-700 mb-1">
                <Server className="inline w-4 h-4 mr-1" />
                Base URL
              </label>
              <input
                id="baseUrl"
                name="baseUrl"
                type="url"
                required
                value={formData.baseUrl}
                onChange={(e) => setFormData({ ...formData, baseUrl: e.target.value })}
                className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
                placeholder="http://localhost:8000"
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              Connect to API
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ApiConfig;