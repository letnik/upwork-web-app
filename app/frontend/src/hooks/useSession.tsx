import { useState, useEffect, useCallback } from 'react';
import { useAuth } from './useAuth';

interface Session {
  id: number;
  ip_address: string | null;
  user_agent: string | null;
  created_at: string;
  expires_at: string;
  is_current: boolean;
}

interface SessionData {
  sessions: Session[];
  total: number;
}

interface UseSessionReturn {
  sessions: Session[];
  total: number;
  loading: boolean;
  error: string | null;
  refreshSessions: () => Promise<void>;
  deactivateSession: (sessionId: number) => Promise<boolean>;
  deactivateAllSessions: () => Promise<boolean>;
  refreshSession: (refreshToken: string) => Promise<boolean>;
}

export const useSession = (): UseSessionReturn => {
  const { user, token } = useAuth();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSessions = useCallback(async () => {
    if (!token) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/auth/sessions/sessions', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Помилка завантаження сесій');
      }

      const data: SessionData = await response.json();
      setSessions(data.sessions);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Помилка завантаження сесій');
    } finally {
      setLoading(false);
    }
  }, [token]);

  const refreshSessions = useCallback(async () => {
    await fetchSessions();
  }, [fetchSessions]);

  const deactivateSession = useCallback(async (sessionId: number): Promise<boolean> => {
    if (!token) return false;

    try {
      const response = await fetch(`/api/auth/sessions/sessions/${sessionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Помилка деактивації сесії');
      }

      // Оновлюємо список сесій
      await fetchSessions();
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Помилка деактивації сесії');
      return false;
    }
  }, [token, fetchSessions]);

  const deactivateAllSessions = useCallback(async (): Promise<boolean> => {
    if (!token) return false;

    try {
      const response = await fetch('/api/auth/sessions/sessions/all', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Помилка деактивації всіх сесій');
      }

      // Оновлюємо список сесій
      await fetchSessions();
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Помилка деактивації всіх сесій');
      return false;
    }
  }, [token, fetchSessions]);

  const refreshSession = useCallback(async (refreshToken: string): Promise<boolean> => {
    try {
      const response = await fetch('/api/auth/sessions/refresh', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ refresh_token: refreshToken })
      });

      if (!response.ok) {
        throw new Error('Помилка оновлення сесії');
      }

      const data = await response.json();
      
      // Оновлюємо токени в localStorage
      localStorage.setItem('token', data.session_token);
      localStorage.setItem('refreshToken', data.refresh_token);
      
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Помилка оновлення сесії');
      return false;
    }
  }, []);

  // Завантажуємо сесії при зміні токена
  useEffect(() => {
    if (token) {
      fetchSessions();
    }
  }, [token, fetchSessions]);

  return {
    sessions,
    total,
    loading,
    error,
    refreshSessions,
    deactivateSession,
    deactivateAllSessions,
    refreshSession
  };
}; 