import axios from 'axios';

export interface PropertyData {
  county: string;
  beds: number;
  price?: number;
  avg?: number;
  yoy?: number;
  avg_yoy?: number;
  region?: string;
  area?: string;
}

export interface RentData {
  county: string;
  beds: number;
  avg?: number;
  avg_yoy?: number;
}

export interface PropertyDetails {
  county: string;
  region: string;
  area: string;
  beds: number;
  price: number;
  rawAddress: string;
  location: string;
  saleDate: string;
  sqrMetres: number;
}

class ApiService {
  private baseUrl: string;
  private apiKey: string;
  private domain: string;

  constructor(baseUrl: string, apiKey: string, domain: string) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
    this.domain = domain;
  }

  private getParams() {
    return {
      key: this.apiKey,
      domain: this.domain
    };
  }

  async getCountyYoY(): Promise<Record<string, PropertyData[]>> {
    const response = await axios.get(`${this.baseUrl}/api/pmx/all`, {
      params: {
        ...this.getParams(),
        entity: 'county',
        version: 'yoy'
      }
    });
    return response.data;
  }

  async getCountyAverage(): Promise<Record<string, PropertyData[]>> {
    const response = await axios.get(`${this.baseUrl}/api/pmx/all`, {
      params: {
        ...this.getParams(),
        entity: 'county',
        version: 'average'
      }
    });
    return response.data;
  }

  async getRegionData(version: 'yoy' | 'average'): Promise<Record<string, PropertyData[]>> {
    const response = await axios.get(`${this.baseUrl}/api/pmx/all`, {
      params: {
        ...this.getParams(),
        entity: 'region',
        version
      }
    });
    return response.data;
  }

  async getAreaData(version: 'yoy' | 'average'): Promise<Record<string, PropertyData[]>> {
    const response = await axios.get(`${this.baseUrl}/api/pmx/all`, {
      params: {
        ...this.getParams(),
        entity: 'area',
        version
      }
    });
    return response.data;
  }

  async getRentData(version: 'yoy' | 'avg'): Promise<RentData[]> {
    const response = await axios.get(`${this.baseUrl}/api/pmx/rent`, {
      params: {
        ...this.getParams(),
        version
      }
    });
    return Object.values(response.data).flat();
  }

  async getPropertyDetails(area?: string): Promise<PropertyDetails[]> {
    const response = await axios.get(`${this.baseUrl}/api/eval/property`, {
      params: {
        ...this.getParams(),
        area: area || 'All'
      }
    });
    return Object.values(response.data);
  }

  async getSpecificData(
    county: string,
    beds?: string,
    region?: string,
    area?: string,
    type: 'yoy' | 'average' = 'average'
  ): Promise<PropertyData[]> {
    const endpoint = type === 'yoy' ? '/api/pmx/yoy' : '/api/pmx/average';
    const response = await axios.get(`${this.baseUrl}${endpoint}`, {
      params: {
        ...this.getParams(),
        county,
        beds,
        region,
        area
      }
    });
    return Object.values(response.data);
  }
}

export default ApiService;