import React, { createContext, useContext, useState, ReactNode } from 'react';

interface ApiConfig {
  apiKey: string;
  domain: string;
  baseUrl: string;
}

interface ApiContextType {
  config: ApiConfig;
  setConfig: (config: ApiConfig) => void;
  isConfigured: boolean;
}

const ApiContext = createContext<ApiContextType | undefined>(undefined);

export const useApi = () => {
  const context = useContext(ApiContext);
  if (!context) {
    throw new Error('useApi must be used within an ApiProvider');
  }
  return context;
};

interface ApiProviderProps {
  children: ReactNode;
}

export const ApiProvider: React.FC<ApiProviderProps> = ({ children }) => {
  const [config, setConfig] = useState<ApiConfig>({
    apiKey: '',
    domain: '',
    baseUrl: ''
  });

  const isConfigured = config.apiKey && config.domain;

  return (
    <ApiContext.Provider value={{ config, setConfig, isConfigured }}>
      {children}
    </ApiContext.Provider>
  );
};