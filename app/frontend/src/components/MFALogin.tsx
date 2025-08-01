import React, { useState } from 'react';
import { Box, Typography, TextField, Button, Paper, Alert, CircularProgress } from '@mui/material';

interface MFALoginProps {
  userId: number;
  onVerificationSuccess: (method: string) => void;
  onCancel: () => void;
}

const MFALogin: React.FC<MFALoginProps> = ({ userId, onVerificationSuccess, onCancel }) => {
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const verifyCode = async () => {
    if (!code.trim()) {
      setError('Введіть код підтвердження');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/auth/mfa/verify-login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_id: userId,
          code: code
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Невірний код підтвердження');
      }

      const data = await response.json();
      onVerificationSuccess(data.method);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Помилка перевірки коду');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 3, maxWidth: 400, mx: 'auto' }}>
      <Typography variant="h5" gutterBottom>
        Двофакторна автентифікація
      </Typography>

      <Typography variant="body1" sx={{ mb: 2 }}>
        Введіть 6-значний код з вашого додатку двофакторної автентифікації:
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <TextField
        fullWidth
        label="Код підтвердження"
        value={code}
        onChange={(e) => setCode(e.target.value)}
        placeholder="000000"
        sx={{ mb: 2 }}
        autoFocus
      />

      <Box display="flex" gap={2}>
        <Button
          variant="contained"
          onClick={verifyCode}
          disabled={loading || !code.trim()}
          fullWidth
        >
          {loading ? <CircularProgress size={20} /> : 'Підтвердити'}
        </Button>
        <Button
          variant="outlined"
          onClick={onCancel}
          disabled={loading}
        >
          Скасувати
        </Button>
      </Box>

      <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
        Якщо у вас немає доступу до додатку, використайте резервний код.
      </Typography>
    </Paper>
  );
};

export default MFALogin; 