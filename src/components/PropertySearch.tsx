import React, { useState, useEffect } from 'react';
import { useApi } from '../context/ApiContext';
import ApiService, { PropertyDetails } from '../services/api';
import { Search, MapPin, Calendar, Home, DollarSign } from 'lucide-react';

const PropertySearch: React.FC = () => {
  const { config } = useApi();
  const [properties, setProperties] = useState<PropertyDetails[]>([]);
  const [filteredProperties, setFilteredProperties] = useState<PropertyDetails[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCounty, setSelectedCounty] = useState('All');
  const [selectedBeds, setSelectedBeds] = useState('All');
  const [priceRange, setPriceRange] = useState({ min: '', max: '' });

  const counties = ['All', 'Dublin', 'Cork', 'Galway', 'Limerick', 'Waterford', 'Kerry', 'Mayo'];
  const bedrooms = ['All', '1', '2', '3', '4', '5', '6+'];

  useEffect(() => {
    const fetchProperties = async () => {
      try {
        setLoading(true);
        const api = new ApiService(config.baseUrl, config.apiKey, config.domain);
        const data = await api.getPropertyDetails();
        setProperties(data);
        setFilteredProperties(data);
      } catch (err) {
        console.error('Error fetching properties:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchProperties();
  }, [config]);

  useEffect(() => {
    let filtered = properties;

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(property =>
        property.rawAddress.toLowerCase().includes(searchTerm.toLowerCase()) ||
        property.area.toLowerCase().includes(searchTerm.toLowerCase()) ||
        property.region.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by county
    if (selectedCounty !== 'All') {
      filtered = filtered.filter(property => property.county === selectedCounty);
    }

    // Filter by bedrooms
    if (selectedBeds !== 'All') {
      const beds = selectedBeds === '6+' ? 6 : parseInt(selectedBeds);
      filtered = filtered.filter(property => 
        selectedBeds === '6+' ? property.beds >= 6 : property.beds === beds
      );
    }

    // Filter by price range
    if (priceRange.min) {
      filtered = filtered.filter(property => property.price >= parseInt(priceRange.min));
    }
    if (priceRange.max) {
      filtered = filtered.filter(property => property.price <= parseInt(priceRange.max));
    }

    setFilteredProperties(filtered);
  }, [properties, searchTerm, selectedCounty, selectedBeds, priceRange]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IE');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Property Search</h2>
        <div className="text-sm text-gray-500">
          {filteredProperties.length} of {properties.length} properties
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <Search className="inline w-4 h-4 mr-1" />
              Search
            </label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Address, area, region..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <MapPin className="inline w-4 h-4 mr-1" />
              County
            </label>
            <select
              value={selectedCounty}
              onChange={(e) => setSelectedCounty(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            >
              {counties.map(county => (
                <option key={county} value={county}>{county}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <Home className="inline w-4 h-4 mr-1" />
              Bedrooms
            </label>
            <select
              value={selectedBeds}
              onChange={(e) => setSelectedBeds(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            >
              {bedrooms.map(bed => (
                <option key={bed} value={bed}>{bed}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <DollarSign className="inline w-4 h-4 mr-1" />
              Min Price
            </label>
            <input
              type="number"
              value={priceRange.min}
              onChange={(e) => setPriceRange({ ...priceRange, min: e.target.value })}
              placeholder="€0"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Max Price
            </label>
            <input
              type="number"
              value={priceRange.max}
              onChange={(e) => setPriceRange({ ...priceRange, max: e.target.value })}
              placeholder="€1,000,000"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="card">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Address
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Location
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Price
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Beds
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Size
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Sale Date
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredProperties.slice(0, 100).map((property, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm text-gray-900">
                    <div className="max-w-xs truncate" title={property.rawAddress}>
                      {property.rawAddress}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div>
                      <div className="font-medium text-gray-900">{property.area}</div>
                      <div className="text-gray-500">{property.region}, {property.county}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    €{property.price.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {property.beds}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {property.sqrMetres ? `${property.sqrMetres}m²` : 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <div className="flex items-center">
                      <Calendar className="w-4 h-4 mr-1" />
                      {formatDate(property.saleDate)}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {filteredProperties.length > 100 && (
          <div className="px-6 py-4 bg-gray-50 border-t">
            <p className="text-sm text-gray-500">
              Showing first 100 results. Use filters to narrow down your search.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default PropertySearch;