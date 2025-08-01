import { apiClient } from './api';
import axios from 'axios';

// Окремий клієнт для analytics service
const analyticsClient = axios.create({
  baseURL: 'http://localhost:8004',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface AnalyticsEvent {
  event_type: string;
  event_data?: any;
  user_id?: number;
  session_id?: string;
  ip_address?: string;
  user_agent?: string;
}

export interface MetricsResponse {
  metrics: {
    event_types: Record<string, number>;
    hourly_distribution: Record<string, number>;
    daily_distribution: Record<string, number>;
    top_events: [string, number][];
  };
  period: {
    start_date: string;
    end_date: string;
  };
  total_events: number;
}

export interface DashboardData {
  earnings: {
    total: number;
    monthly: number;
    weekly: number;
  };
  proposals: {
    sent: number;
    accepted: number;
    pending: number;
    rejected: number;
  };
  jobs: {
    applied: number;
    won: number;
    active: number;
    completed: number;
  };
  performance: {
    rating: number;
    success_rate: number;
  };
  categories: Array<{
    name: string;
    value: number;
    color: string;
  }>;
  time_series: Array<{
    date: string;
    earnings: number;
    proposals: number;
  }>;
  trends: {
    earnings: number;
    proposals: number;
  };
  generated_at: string;
}

export interface PerformanceReport {
  period: string;
  metrics: {
    jobs_applied: number;
    proposals_sent: number;
    interviews_scheduled: number;
    offers_received: number;
    earnings: number;
  };
  trends: {
    jobs_per_day: number;
    proposals_per_day: number;
    success_rate_trend: number;
  };
}

export class AnalyticsService {
  // Відстеження події
  async trackEvent(event: AnalyticsEvent): Promise<any> {
    const response = await apiClient.post('/analytics/track/event', event);
    return response.data!;
  }

  // Отримання метрик
  async getMetrics(params?: {
    metric_type?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<MetricsResponse> {
    const queryParams = new URLSearchParams();
    if (params?.metric_type) queryParams.append('metric_type', params.metric_type);
    if (params?.start_date) queryParams.append('start_date', params.start_date);
    if (params?.end_date) queryParams.append('end_date', params.end_date);

    const url = `/analytics/metrics${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await apiClient.get<MetricsResponse>(url);
    return response.data!;
  }

  // Отримання даних дашборду
  async getDashboardData(params?: {
    start_date?: string;
    end_date?: string;
  }): Promise<DashboardData> {
    const queryParams = new URLSearchParams();
    if (params?.start_date) queryParams.append('start_date', params.start_date);
    if (params?.end_date) queryParams.append('end_date', params.end_date);
    
    // Додаємо user_id
    const userId = this.getCurrentUserId() || 'test_user_123';
    queryParams.append('user_id', userId.toString());

    const url = `/analytics/dashboard${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await analyticsClient.get<{status: string, data: DashboardData}>(url);
    return response.data!.data;
  }

  // Отримання звіту про продуктивність
  async getPerformanceReport(params?: {
    start_date?: string;
    end_date?: string;
  }): Promise<PerformanceReport> {
    const queryParams = new URLSearchParams();
    if (params?.start_date) queryParams.append('start_date', params.start_date);
    if (params?.end_date) queryParams.append('end_date', params.end_date);

    const url = `/analytics/reports/performance${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await apiClient.get<PerformanceReport>(url);
    return response.data!;
  }

  // Отримання звіту про доходи
  async getRevenueReport(params?: {
    start_date?: string;
    end_date?: string;
  }): Promise<any> {
    const queryParams = new URLSearchParams();
    if (params?.start_date) queryParams.append('start_date', params.start_date);
    if (params?.end_date) queryParams.append('end_date', params.end_date);

    const url = `/analytics/reports/revenue${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await apiClient.get(url);
    return response.data!;
  }

  // Відстеження дій користувача
  trackUserAction(action: string, data?: any): void {
    this.trackEvent({
      event_type: `user_action_${action}`,
      event_data: data,
      user_id: this.getCurrentUserId(),
      session_id: this.getSessionId(),
    }).catch(console.error);
  }

  // Відстеження пошуку робіт
  trackJobSearch(query: string, results_count: number): void {
    this.trackEvent({
      event_type: 'job_search',
      event_data: { query, results_count },
      user_id: this.getCurrentUserId(),
    }).catch(console.error);
  }

  // Відстеження генерації пропозиції
  trackProposalGeneration(job_id: string, success: boolean): void {
    this.trackEvent({
      event_type: 'proposal_generated',
      event_data: { job_id, success },
      user_id: this.getCurrentUserId(),
    }).catch(console.error);
  }

  private getCurrentUserId(): number | undefined {
    const user = localStorage.getItem('user');
    if (user) {
      try {
        const userData = JSON.parse(user);
        return userData.id;
      } catch {
        return undefined;
      }
    }
    return undefined;
  }

  private getSessionId(): string | undefined {
    return localStorage.getItem('session_id') || undefined;
  }
}

export const analyticsService = new AnalyticsService(); 