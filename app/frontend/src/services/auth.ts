import { apiClient } from './api';
import { 
  LoginRequest, 
  RegisterRequest, 
  AuthResponse, 
  User, 
  MFASetupResponse, 
  MFAVerificationRequest 
} from '../types';

export class AuthService {
  // Авторизація
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/login-test', credentials);
    if (response.success && response.data) {
      // Зберігаємо токени
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data!;
  }

  async register(userData: RegisterRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/register', userData);
    if (response.success && response.data) {
      // Зберігаємо токени
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data!;
  }

  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout');
    } catch (error) {
      // Ігноруємо помилки при logout
    } finally {
      // Очищаємо локальне зберігання
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    }
  }

  async refreshToken(): Promise<AuthResponse> {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await apiClient.post<AuthResponse>('/auth/refresh', {
      refresh_token: refreshToken
    });

    if (response.success && response.data) {
      // Оновлюємо токени
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }

    return response.data!;
  }

  // MFA функції
  async setupMFA(): Promise<MFASetupResponse> {
    const response = await apiClient.post<MFASetupResponse>('/auth/mfa/setup');
    return response.data!;
  }

  async verifyMFA(code: string): Promise<void> {
    const request: MFAVerificationRequest = { code };
    await apiClient.post('/auth/mfa/verify', request);
  }

  async disableMFA(): Promise<void> {
    await apiClient.delete('/auth/mfa/disable');
  }

  async getMFAStatus(): Promise<{ enabled: boolean }> {
    const response = await apiClient.get<{ enabled: boolean }>('/auth/mfa/status');
    return response.data!;
  }

  // OAuth функції
  async getOAuthUrl(provider: string): Promise<{ url: string }> {
    const response = await apiClient.get<{ url: string }>(`/auth/oauth/${provider}/authorize`);
    return response.data!;
  }

  async handleOAuthCallback(provider: string, code: string): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>(`/auth/oauth/${provider}/callback`, { code });
    if (response.success && response.data) {
      // Зберігаємо токени
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data!;
  }

  // Утиліти
  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  }

  getCurrentUser(): User | null {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        return JSON.parse(userStr);
      } catch {
        return null;
      }
    }
    return null;
  }

  getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }
}

// Singleton instance
export const authService = new AuthService(); 