import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Stepper,
  Step,
  StepLabel,
  Button,
  Grid,
  Card,
  CardContent,
  Chip,
  Divider,
  Alert,
} from '@mui/material';
import {
  Description as DescriptionIcon,
  Work as WorkIcon,
  Payment as PaymentIcon,
  Send as SendIcon,
} from '@mui/icons-material';
import ProposalForm from '../components/ProposalForm';
import ProposalTemplate from '../components/ProposalTemplate';

interface ProposalData {
  jobTitle: string;
  jobDescription: string;
  clientBudget: string;
  clientTimeline: string;
  skills: string[];
  proposalTitle: string;
  coverLetter: string;
  hourlyRate: number;
  estimatedHours: number;
  totalPrice: number;
  timeline: string;
  portfolio: string[];
}

const steps = [
  'Аналіз завдання',
  'Створення пропозиції',
  'Перевірка та відправка',
];

const ProposalCreator: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [proposalData, setProposalData] = useState<ProposalData>({
    jobTitle: '',
    jobDescription: '',
    clientBudget: '',
    clientTimeline: '',
    skills: [],
    proposalTitle: '',
    coverLetter: '',
    hourlyRate: 0,
    estimatedHours: 0,
    totalPrice: 0,
    timeline: '',
    portfolio: [],
  });

  const [savedProposals, setSavedProposals] = useState<ProposalData[]>([]);

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleSaveProposal = () => {
    setSavedProposals([...savedProposals, proposalData]);
    setProposalData({
      jobTitle: '',
      jobDescription: '',
      clientBudget: '',
      clientTimeline: '',
      skills: [],
      proposalTitle: '',
      coverLetter: '',
      hourlyRate: 0,
      estimatedHours: 0,
      totalPrice: 0,
      timeline: '',
      portfolio: [],
    });
    setActiveStep(0);
  };

  const handleSubmitProposal = () => {
    // Тут буде логіка відправки пропозиції
    console.log('Відправка пропозиції:', proposalData);
    handleSaveProposal();
  };

  const getStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Аналіз завдання
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      <WorkIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                      Інформація про завдання
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      Введіть деталі завдання для аналізу та створення оптимальної пропозиції
                    </Typography>
                    <ProposalForm
                      proposalData={proposalData}
                      setProposalData={setProposalData}
                      step="analysis"
                    />
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      <DescriptionIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                      Аналіз вимог
                    </Typography>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Необхідні навички:
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                        {proposalData.skills.map((skill, index) => (
                          <Chip key={index} label={skill} size="small" />
                        ))}
                      </Box>
                    </Box>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Бюджет клієнта: {proposalData.clientBudget}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="subtitle2" gutterBottom>
                        Терміни: {proposalData.clientTimeline}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
        );
      case 1:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Створення пропозиції
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={8}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      <DescriptionIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                      Деталі пропозиції
                    </Typography>
                    <ProposalForm
                      proposalData={proposalData}
                      setProposalData={setProposalData}
                      step="creation"
                    />
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      <PaymentIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                      Фінансові деталі
                    </Typography>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Годинна ставка: ${proposalData.hourlyRate}
                      </Typography>
                    </Box>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Очікувані години: {proposalData.estimatedHours}
                      </Typography>
                    </Box>
                    <Divider sx={{ my: 2 }} />
                    <Box>
                      <Typography variant="h6" gutterBottom>
                        Загальна вартість: ${proposalData.totalPrice}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
        );
      case 2:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Перевірка та відправка
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Alert severity="info" sx={{ mb: 3 }}>
                  Перевірте всі деталі перед відправкою пропозиції
                </Alert>
                <ProposalTemplate proposalData={proposalData} />
              </Grid>
            </Grid>
          </Box>
        );
      default:
        return 'Unknown step';
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom align="center">
        Створення пропозиції
      </Typography>
      <Typography variant="body1" color="text.secondary" align="center" sx={{ mb: 4 }}>
        Створіть професійну пропозицію для завдання на Upwork
      </Typography>

      <Paper sx={{ p: 3, mb: 4 }}>
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        <Box sx={{ mt: 2, mb: 2 }}>
          {getStepContent(activeStep)}
        </Box>

        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
          <Button
            color="inherit"
            disabled={activeStep === 0}
            onClick={handleBack}
            sx={{ mr: 1 }}
          >
            Назад
          </Button>
          <Box>
            <Button
              variant="outlined"
              onClick={handleSaveProposal}
              sx={{ mr: 1 }}
            >
              Зберегти чернетку
            </Button>
            {activeStep === steps.length - 1 ? (
              <Button
                variant="contained"
                onClick={handleSubmitProposal}
                startIcon={<SendIcon />}
              >
                Відправити пропозицію
              </Button>
            ) : (
              <Button variant="contained" onClick={handleNext}>
                Далі
              </Button>
            )}
          </Box>
        </Box>
      </Paper>

      {savedProposals.length > 0 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Збережені чернетки
          </Typography>
          <Grid container spacing={2}>
            {savedProposals.map((proposal, index) => (
              <Grid item xs={12} md={6} key={index}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {proposal.proposalTitle || `Чернетка ${index + 1}`}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      {proposal.jobTitle}
                    </Typography>
                    <Typography variant="body2">
                      Бюджет: ${proposal.totalPrice}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Paper>
      )}
    </Container>
  );
};

export default ProposalCreator; 