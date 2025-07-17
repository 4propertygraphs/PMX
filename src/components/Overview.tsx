import React, { useState, useEffect } from 'react';
import { useApi } from '../context/ApiContext';
import ApiService, { PropertyData } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { TrendingUp, TrendingDown, Home, DollarSign } from 'lucide-react';

const Overview: React.FC = () => {
  const { config } = useApi();
  const [countyData, setCountyData] = useState<Record<string, PropertyData[]>>({});
  const [yoyData, setYoyData] = useState<Record<string, PropertyData[]>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const api = new ApiService(config.baseUrl, config.apiKey, config.domain);
        
        const [avgData, yoyResults] = await Promise.all([
          api.getCountyAverage(),
          api.getCountyYoY()
        ]);
        
        setCountyData(avgData);
        setYoyData(yoyResults);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [config]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <p className="text-red-800">Error: {error}</p>
      </div>
    );
  }

  // Process data for charts
  const chartData = Object.entries(countyData).map(([county, data]) => {
    const avgPrice = data.reduce((sum, item) => sum + (item.avg || 0), 0) / data.length;
    const yoyChange = yoyData[county] ? 
      yoyData[county].reduce((sum, item) => sum + (item.yoy || 0), 0) / yoyData[county].length : 0;
    
    return {
      county,
      avgPrice: Math.round(avgPrice),
      yoyChange: Math.round(yoyChange * 100) / 100
    };
  }).sort((a, b) => b.avgPrice - a.avgPrice).slice(0, 10);

  const totalProperties = Object.values(countyData).reduce((sum, data) => sum + data.length, 0);
  const avgNationalPrice = chartData.reduce((sum, item) => sum + item.avgPrice, 0) / chartData.length;
  const avgYoYChange = chartData.reduce((sum, item) => sum + item.yoyChange, 0) / chartData.length;

  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Home className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Properties</p>
              <p className="text-2xl font-bold text-gray-900">{totalProperties.toLocaleString()}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <DollarSign className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Avg National Price</p>
              <p className="text-2xl font-bold text-gray-900">€{avgNationalPrice.toLocaleString()}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className={`p-2 rounded-lg ${avgYoYChange >= 0 ? 'bg-green-100' : 'bg-red-100'}`}>
              {avgYoYChange >= 0 ? 
                <TrendingUp className="h-6 w-6 text-green-600" /> : 
                <TrendingDown className="h-6 w-6 text-red-600" />
              }
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Avg YoY Change</p>
              <p className={`text-2xl font-bold ${avgYoYChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {avgYoYChange > 0 ? '+' : ''}{avgYoYChange.toFixed(1)}%
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <BarChart className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Counties Tracked</p>
              <p className="text-2xl font-bold text-gray-900">{Object.keys(countyData).length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Average Prices by County</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="county" 
                angle={-45}
                textAnchor="end"
                height={80}
                fontSize={12}
              />
              <YAxis 
                tickFormatter={(value) => `€${(value / 1000).toFixed(0)}k`}
              />
              <Tooltip 
                formatter={(value) => [`€${Number(value).toLocaleString()}`, 'Average Price']}
              />
              <Bar dataKey="avgPrice" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Year-over-Year Change</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="county" 
                angle={-45}
                textAnchor="end"
                height={80}
                fontSize={12}
              />
              <YAxis 
                tickFormatter={(value) => `${value}%`}
              />
              <Tooltip 
                formatter={(value) => [`${Number(value).toFixed(1)}%`, 'YoY Change']}
              />
              <Line 
                type="monotone" 
                dataKey="yoyChange" 
                stroke="#10b981" 
                strokeWidth={2}
                dot={{ fill: '#10b981', strokeWidth: 2, r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* County Table */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">County Summary</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  County
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Avg Price
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  YoY Change
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Properties
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {chartData.map((item) => (
                <tr key={item.county} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {item.county}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    €{item.avgPrice.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      item.yoyChange >= 0 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {item.yoyChange > 0 ? '+' : ''}{item.yoyChange.toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {countyData[item.county]?.length || 0}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Overview;