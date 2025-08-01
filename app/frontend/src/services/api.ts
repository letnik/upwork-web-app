import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { ApiResponse, ApiError } from '../types';

// Базовий API клієнт
class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: (window as any).__REACT_APP_API_URL__ || 'http://localhost:8000',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor для додавання токена
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor для обробки помилок
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        return response;
      },
      (error) => {
        if (error.response?.status === 401) {
          // Token expired - redirect to login
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
        return Promise.reject(this.handleError(error));
      }
    );
  }

  private handleError(error: any): ApiError {
    if (error.response) {
      return {
        status: error.response.status,
        message: error.response.data?.message || error.response.statusText,
        details: error.response.data,
      };
    } else if (error.request) {
      return {
        status: 0,
        message: 'Network error - no response received',
      };
    } else {
      return {
        status: 0,
        message: error.message || 'Unknown error occurred',
      };
    }
  }

  // Generic methods
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await this.client.get(url, config);
    return {
      success: true,
      data: response.data
    };
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await this.client.post(url, data, config);
    return {
      success: true,
      data: response.data
    };
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await this.client.put(url, data, config);
    return {
      success: true,
      data: response.data
    };
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await this.client.delete(url, config);
    return {
      success: true,
      data: response.data
    };
  }

  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await this.client.patch(url, data, config);
    return {
      success: true,
      data: response.data
    };
  }
}

// Singleton instance
export const apiClient = new ApiClient();

// Utility functions
export const isApiError = (error: any): error is ApiError => {
  return error && typeof error.status === 'number' && typeof error.message === 'string';
};

export const handleApiError = (error: any): string => {
  if (isApiError(error)) {
    return error.message;
  }
  return 'An unexpected error occurred';
};

// Upwork API functions
export const getJobs = async (params?: any) => {
  return apiClient.get('/upwork/jobs', { params });
};

export const searchJobs = async (query: string, params?: any) => {
  return apiClient.post('/upwork/jobs/search', { query, ...params });
};

export const getJobDetails = async (jobId: string) => {
  return apiClient.get(`/upwork/jobs/${jobId}`);
}; 