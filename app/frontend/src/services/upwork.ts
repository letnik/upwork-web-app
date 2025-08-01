import { apiClient } from './api';

export interface Job {
  id: string;
  title: string;
  description: string;
  budget: {
    min: number;
    max: number;
    currency: string;
  };
  skills: string[];
  client: {
    id: string;
    name: string;
    rating: number;
    total_spent: number;
  };
  posted_time: string;
  proposals_count: number;
  hire_rate: number;
  location: string;
  job_type: string;
  experience_level: string;
  duration: string;
}

export interface Proposal {
  id: string;
  job_id: string;
  freelancer_id: string;
  proposal_text: string;
  bid_amount: number;
  delivery_time: string;
  status: string;
  submitted_at: string;
}

export interface Client {
  id: string;
  name: string;
  rating: number;
  total_spent: number;
  location: string;
  member_since: string;
  jobs_posted: number;
  hire_rate: number;
}

export interface Freelancer {
  id: string;
  name: string;
  title: string;
  rating: number;
  total_earned: number;
  skills: string[];
  location: string;
  hourly_rate: number;
  success_rate: number;
}

export interface JobFilters {
  skills?: string;
  budget_min?: number;
  budget_max?: number;
  location?: string;
}

export interface JobSearchParams {
  query: string;
  skip?: number;
  limit?: number;
}

export interface CreateProposalRequest {
  job_id: string;
  proposal_text: string;
  bid_amount: number;
  delivery_time: string;
}

export interface AnalyticsOverview {
  overview: {
    total_jobs: number;
    total_proposals: number;
    average_budget: number;
    top_skills: [string, number][];
  };
  recent_jobs: Job[];
  recent_proposals: Proposal[];
}

export class UpworkService {
  // Отримання списку вакансій
  async getJobs(params?: {
    skip?: number;
    limit?: number;
    skills?: string;
    budget_min?: number;
    budget_max?: number;
    location?: string;
  }): Promise<{ jobs: Job[]; total: number; skip: number; limit: number; filters_applied: any }> {
    const queryParams = new URLSearchParams();
    
    if (params?.skip) queryParams.append('skip', params.skip.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.skills) queryParams.append('skills', params.skills);
    if (params?.budget_min) queryParams.append('budget_min', params.budget_min.toString());
    if (params?.budget_max) queryParams.append('budget_max', params.budget_max.toString());
    if (params?.location) queryParams.append('location', params.location);

    const url = `/upwork/jobs${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await apiClient.get(url);
    return response.data!;
  }

  // Отримання деталей вакансії
  async getJob(jobId: string): Promise<{ job: Job; proposals_count: number; proposals: Proposal[] }> {
    const response = await apiClient.get(`/upwork/jobs/${jobId}`);
    return response.data!;
  }

  // Пошук вакансій
  async searchJobs(params: JobSearchParams): Promise<{ jobs: Job[]; total: number; query: string; skip: number; limit: number }> {
    const response = await apiClient.post('/upwork/jobs/search', params);
    return response.data!;
  }

  // Отримання пропозицій користувача
  async getProposals(params?: {
    skip?: number;
    limit?: number;
    job_id?: string;
  }): Promise<{ applications: Proposal[]; total: number; skip: number; limit: number }> {
    const queryParams = new URLSearchParams();
    
    if (params?.skip) queryParams.append('skip', params.skip.toString());
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.job_id) queryParams.append('job_id', params.job_id);

    const url = `/upwork/applications${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await apiClient.get(url);
    return response.data!;
  }

  // Створення пропозиції
  async createProposal(request: CreateProposalRequest): Promise<{ proposal: Proposal; job: Job; message: string }> {
    const response = await apiClient.post('/upwork/applications', request);
    return response.data!;
  }

  // Отримання інформації про клієнта
  async getClient(clientId: string): Promise<{ client: Client }> {
    const response = await apiClient.get(`/upwork/clients/${clientId}`);
    return response.data!;
  }

  // Отримання інформації про фрілансера
  async getFreelancer(freelancerId: string): Promise<{ freelancer: Freelancer }> {
    const response = await apiClient.get(`/upwork/freelancers/${freelancerId}`);
    return response.data!;
  }

  // Отримання аналітики
  async getAnalyticsOverview(): Promise<AnalyticsOverview> {
    const response = await apiClient.get('/upwork/analytics/overview');
    return response.data!;
  }

  // Відстеження дій користувача
  trackJobView(jobId: string): void {
    // Можна додати відстеження через analytics service
    console.log(`Job viewed: ${jobId}`);
  }

  trackProposalCreated(jobId: string, bidAmount: number): void {
    // Можна додати відстеження через analytics service
    console.log(`Proposal created for job: ${jobId}, bid: ${bidAmount}`);
  }

  trackJobSearch(query: string, resultsCount: number): void {
    // Можна додати відстеження через analytics service
    console.log(`Job search: "${query}", found ${resultsCount} results`);
  }
}

export const upworkService = new UpworkService(); 