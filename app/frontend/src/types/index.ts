// API Response типи
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

// Auth типи
export interface User {
  id: number;
  email: string;
  first_name?: string;
  last_name?: string;
  mfa_enabled: boolean;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

export interface AuthResponse {
  user: User;
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// MFA типи
export interface MFASetupResponse {
  qr_code: string;
  backup_codes: string[];
  secret_key: string;
}

export interface MFAVerificationRequest {
  code: string;
}

// OAuth типи
export interface OAuthConnection {
  id: string;
  provider: string;
  provider_user_id: string;
  access_token: string;
  refresh_token: string;
  expires_at: string;
  created_at: string;
}

// Upwork типи
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
  posted_date: string;
  deadline: string;
  category: string;
  subcategory: string;
  location: string;
  type: 'hourly' | 'fixed';
}

export interface JobSearchParams {
  query?: string;
  category?: string;
  subcategory?: string;
  budget_min?: number;
  budget_max?: number;
  skills?: string[];
  location?: string;
  type?: 'hourly' | 'fixed';
  page?: number;
  limit?: number;
}

export interface Proposal {
  id: string;
  job_id: string;
  cover_letter: string;
  bid_amount: number;
  estimated_hours?: number;
  status: 'pending' | 'accepted' | 'rejected' | 'withdrawn';
  created_at: string;
  updated_at: string;
}

// AI типи
export interface AIAnalysis {
  job_id: string;
  analysis: {
    difficulty: 'easy' | 'medium' | 'hard';
    competition: 'low' | 'medium' | 'high';
    recommended_bid: number;
    skills_match: number;
    success_probability: number;
  };
  suggestions: string[];
  generated_proposal?: string;
}

// UI типи
export interface NavItem {
  label: string;
  path: string;
  icon?: string;
  children?: NavItem[];
}

export interface TableColumn<T = any> {
  key: keyof T;
  label: string;
  sortable?: boolean;
  render?: (value: any, row: T) => any;
}

// Error типи
export interface ApiError {
  status: number;
  message: string;
  details?: any;
}

// Form типи
export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'email' | 'password' | 'number' | 'select' | 'textarea';
  required?: boolean;
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
    message?: string;
  };
  options?: { value: string; label: string }[];
} 