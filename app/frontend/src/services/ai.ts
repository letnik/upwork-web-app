import { apiClient } from './api';

export interface JobAnalysis {
  keywords: string[];
  estimated_duration: string;
  complexity_level: string;
}

export interface ProposalRequest {
  job_description: string;
  user_profile?: string;
}

export interface ProposalResponse {
  proposal: string;
  job_analysis: JobAnalysis;
  status: string;
}

export interface JobFilterRequest {
  jobs: any[];
  user_preferences?: any;
}

export interface JobOptimizationRequest {
  proposal_text: string;
  job_description: string;
}

export class AIService {
  // Генерація пропозиції
  async generateProposal(request: ProposalRequest): Promise<ProposalResponse> {
    const response = await apiClient.post<ProposalResponse>('/ai/generate/proposal', request);
    return response.data!;
  }

  // Аналіз роботи
  async analyzeJob(job_description: string): Promise<any> {
    const response = await apiClient.post('/ai/analyze/job', { job_description });
    return response.data!;
  }

  // Фільтрація робіт
  async filterJobs(request: JobFilterRequest): Promise<any> {
    const response = await apiClient.post('/ai/filter/jobs', request);
    return response.data!;
  }

  // Оптимізація пропозиції
  async optimizeProposal(request: JobOptimizationRequest): Promise<any> {
    const response = await apiClient.post('/ai/optimize/proposal', request);
    return response.data!;
  }
}

export const aiService = new AIService(); 