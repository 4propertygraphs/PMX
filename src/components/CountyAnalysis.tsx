import React, { useState, useEffect } from 'react';
import { useApi } from '../context/ApiContext';
import ApiService, { PropertyData } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { MapPin, Bed } from 'lucide-react';

const CountyAnalysis: React.FC = () => {
  const { config } = useApi();
  const [selectedCounty, setSelectedCounty] = useState('Dublin');
  const [data, setData] = useState<PropertyData[]>([]);
  const [yoyData, setYoyData] = useState<PropertyData[]>([]);
  const [loading, setLoading] = useState(false);
  const [counties] = useState([
    'Dublin', 'Cork', 'Galway', 'Limerick', 'Waterford', 'Kerry', 'Mayo', 
    'Donegal', 'Wicklow', 'Meath', 'Kildare', 'Wexford', 'Clare', 'Tipperary'
  ]);

  useEffect(() => {
    const fetchCountyData = async () => {
      if (!selectedCounty) return;
      
      try {
        setLoading(true);
        const api = new ApiService(config.baseUrl, config.apiKey, config.domain);
        
        const [avgData, yoyResults] = await Promise.all([
          api.getSpecificData(selectedCounty, undefined, undefined, undefined, 'average'),
          api.getSpecificData(selectedCounty, undefined, undefined, undefined, 'yoy')
        ]);
        
        setData(avgData);
        setYoyData(yoyResults);
      } catch (err) {
        console.error('Error fetching county data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchCountyData();
  }, [selectedCounty, config]);

  const chartData = [1, 2, 3, 4, 5, 6].map(beds => {
    const avgItem = data.find(item => item.beds === beds);
    const yoyItem = yoyData.find(item => item.beds === beds);
    
    return {
      beds: beds === 6 ? '6+' : beds.toString(),
      avgPrice: avgItem?.avg || 0,
      yoyChange: yoyItem?.yoy || 0
    };
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">County Analysis</h2>
        <div className="flex items-center space-x-4">
          <MapPin className="h-5 w-5 text-gray-400" />
          <select
            value={selectedCounty}
            onChange={(e) => setSelectedCounty(e.target.value)}
            className="block w-48 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
          >
            {counties.map(county => (
              <option key={county} value={county}>{county}</option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Average Prices by Bedrooms - {selectedCounty}
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="beds" />
                  <YAxis tickFormatter={(value) => `€${(value / 1000).toFixed(0)}k`} />
                  <Tooltip 
                    formatter={(value) => [`€${Number(value).toLocaleString()}`, 'Average Price']}
                  />
                  <Bar dataKey="avgPrice" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Year-over-Year Change by Bedrooms
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="beds" />
                  <YAxis tickFormatter={(value) => `${value}%`} />
                  <Tooltip 
                    formatter={(value) => [`${Number(value).toFixed(1)}%`, 'YoY Change']}
                  />
                  <Bar 
                    dataKey="yoyChange" 
                    fill={(entry) => entry >= 0 ? '#10b981' : '#ef4444'}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Detailed Breakdown - {selectedCounty}
            </h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      <Bed className="inline w-4 h-4 mr-1" />
                      Bedrooms
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Average Price
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
                  {chartData.map((item) => (
                    <tr key={item.beds} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {item.beds} {item.beds === '1' ? 'Bedroom' : 'Bedrooms'}
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
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {item.yoyChange > 5 ? 'Hot Market' : 
                         item.yoyChange > 0 ? 'Growing' : 
                         item.yoyChange > -5 ? 'Stable' : 'Declining'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default CountyAnalysis;