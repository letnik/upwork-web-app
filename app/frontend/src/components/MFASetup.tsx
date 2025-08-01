import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  TextField,
  Alert,
  Paper,
  Grid,
  CircularProgress,
} from '@mui/material';
import { QRCodeSVG } from 'qrcode.react';

interface MFASetupProps {
  onSetupComplete: () => void;
  onCancel: () => void;
}

const MFASetup: React.FC<MFASetupProps> = ({ onSetupComplete, onCancel }) => {
  const [qrCode, setQrCode] = useState<string>('');
  const [secret, setSecret] = useState<string>('');
  const [verificationCode, setVerificationCode] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [isVerified, setIsVerified] = useState(false);

  useEffect(() => {
    // Генеруємо QR код та секрет
    generateMFASecret();
  }, []);

  const generateMFASecret = async () => {
    try {
      setIsLoading(true);
      // Тут буде API виклик для генерації MFA секрету
      const mockSecret = 'JBSWY3DPEHPK3PXP';
      const mockQrCode = `otpauth://totp/UpworkAI:user@example.com?secret=${mockSecret}&issuer=UpworkAI`;
      
      setSecret(mockSecret);
      setQrCode(mockQrCode);
    } catch (error) {
      setError('Помилка генерації MFA секрету');
    } finally {
      setIsLoading(false);
    }
  };

  const verifyCode = async () => {
    if (!verificationCode || verificationCode.length !== 6) {
      setError('Введіть 6-значний код');
      return;
    }

    try {
      setIsLoading(true);
      setError('');
      
      // Тут буде API виклик для верифікації коду
      // const response = await fetch('/api/auth/mfa/verify', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ code: verificationCode, secret })
      // });

      // Мок верифікація
      if (verificationCode === '123456') {
        setIsVerified(true);
        setTimeout(() => {
          onSetupComplete();
        }, 1000);
      } else {
        setError('Невірний код. Спробуйте ще раз.');
      }
    } catch (error) {
      setError('Помилка верифікації коду');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading && !qrCode) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Налаштування двофакторної автентифікації
      </Typography>
      
      <Typography variant="body2" color="text.secondary" paragraph>
        Для налаштування MFA відскануйте QR код у додатку Google Authenticator або введіть секретний ключ вручну.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {isVerified && (
        <Alert severity="success" sx={{ mb: 2 }}>
          MFA успішно налаштовано!
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Box textAlign="center">
            <Typography variant="subtitle1" gutterBottom>
              QR код
            </Typography>
            {qrCode && (
              <Box sx={{ p: 2, border: '1px solid #ddd', borderRadius: 1, display: 'inline-block' }}>
                <QRCodeSVG value={qrCode} size={200} />
              </Box>
            )}
          </Box>
        </Grid>

        <Grid item xs={12} md={6}>
          <Box>
            <Typography variant="subtitle1" gutterBottom>
              Секретний ключ
            </Typography>
            <TextField
              fullWidth
              value={secret}
              variant="outlined"
              size="small"
              sx={{ mb: 2 }}
              InputProps={{ readOnly: true }}
            />

            <Typography variant="subtitle1" gutterBottom>
              Код підтвердження
            </Typography>
            <TextField
              fullWidth
              value={verificationCode}
              onChange={(e) => setVerificationCode(e.target.value)}
              placeholder="Введіть 6-значний код"
              variant="outlined"
              size="small"
              sx={{ mb: 2 }}
              inputProps={{ maxLength: 6 }}
            />

            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                variant="contained"
                onClick={verifyCode}
                disabled={isLoading || isVerified}
                sx={{ flex: 1 }}
              >
                {isLoading ? <CircularProgress size={20} /> : 'Підтвердити'}
              </Button>
              
              <Button
                variant="outlined"
                onClick={onCancel}
                disabled={isLoading}
              >
                Скасувати
              </Button>
            </Box>
          </Box>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default MFASetup; 