import React, { useState, useEffect } from 'react';
import { useApi } from '../context/ApiContext';
import ApiService, { RentData } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Home, TrendingUp } from 'lucide-react';

const RentAnalysis: React.FC = () => {
  const { config } = useApi();
  const [rentAvg, setRentAvg] = useState<RentData[]>([]);
  const [rentYoy, setRentYoy] = useState<RentData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRentData = async () => {
      try {
        setLoading(true);
        const api = new ApiService(config.baseUrl, config.apiKey, config.domain);
        
        const [avgData, yoyData] = await Promise.all([
          api.getRentData('avg'),
          api.getRentData('yoy')
        ]);
        
        setRentAvg(avgData);
        setRentYoy(yoyData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch rent data');
      } finally {
        setLoading(false);
      }
    };

    fetchRentData();
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
  const chartData = rentAvg.map(avgItem => {
    const yoyItem = rentYoy.find(yoy => 
      yoy.county === avgItem.county && yoy.beds === avgItem.beds
    );
    
    return {
      county: avgItem.county,
      beds: avgItem.beds,
      avgRent: avgItem.avg || 0,
      yoyChange: yoyItem?.avg_yoy || 0
    };
  });

  // Group by county for summary
  const countyData = chartData.reduce((acc, item) => {
    if (!acc[item.county]) {
      acc[item.county] = [];
    }
    acc[item.county].push(item);
    return acc;
  }, {} as Record<string, typeof chartData>);

  const countySummary = Object.entries(countyData).map(([county, data]) => {
    const avgRent = data.reduce((sum, item) => sum + item.avgRent, 0) / data.length;
    const avgYoy = data.reduce((sum, item) => sum + item.yoyChange, 0) / data.length;
    
    return {
      county,
      avgRent: Math.round(avgRent),
      avgYoy: Math.round(avgYoy * 100) / 100,
      properties: data.length
    };
  }).sort((a, b) => b.avgRent - a.avgRent);

  const bedroomData = [1, 2, 3, 4, 5, 6].map(beds => {
    const items = chartData.filter(item => item.beds === beds);
    const avgRent = items.reduce((sum, item) => sum + item.avgRent, 0) / items.length;
    const avgYoy = items.reduce((sum, item) => sum + item.yoyChange, 0) / items.length;
    
    return {
      beds: beds === 6 ? '6+' : beds.toString(),
      avgRent: Math.round(avgRent) || 0,
      avgYoy: Math.round(avgYoy * 100) / 100 || 0
    };
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Rental Market Analysis</h2>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Home className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Avg National Rent</p>
              <p className="text-2xl font-bold text-gray-900">
                €{Math.round(chartData.reduce((sum, item) => sum + item.avgRent, 0) / chartData.length).toLocaleString()}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <TrendingUp className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Avg YoY Change</p>
              <p className="text-2xl font-bold text-green-600">
                +{Math.round((chartData.reduce((sum, item) => sum + item.yoyChange, 0) / chartData.length) * 100) / 100}%
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Home className="h-6 w-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Markets Tracked</p>
              <p className="text-2xl font-bold text-gray-900">{Object.keys(countyData).length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Average Rent by County</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={countySummary.slice(0, 10)}>
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
                formatter={(value) => [`€${Number(value).toLocaleString()}`, 'Average Rent']}
              />
              <Bar dataKey="avgRent" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Rent by Bedroom Count</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={bedroomData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="beds" />
              <YAxis 
                tickFormatter={(value) => `€${(value / 1000).toFixed(0)}k`}
              />
              <Tooltip 
                formatter={(value) => [`€${Number(value).toLocaleString()}`, 'Average Rent']}
              />
              <Bar dataKey="avgRent" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* County Summary Table */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Rental Market Summary by County</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  County
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Avg Rent
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  YoY Change
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Market Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {countySummary.map((item) => (
                <tr key={item.county} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {item.county}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    €{item.avgRent.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      item.avgYoy >= 0 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {item.avgYoy > 0 ? '+' : ''}{item.avgYoy.toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {item.avgYoy > 10 ? 'Very Hot' : 
                     item.avgYoy > 5 ? 'Hot Market' : 
                     item.avgYoy > 0 ? 'Growing' : 'Stable'}
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

export default RentAnalysis;