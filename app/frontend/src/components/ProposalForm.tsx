import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Chip,
  Stack,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  InputAdornment,
  Alert,
} from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon } from '@mui/icons-material';

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

interface ProposalFormProps {
  proposalData: ProposalData;
  setProposalData: React.Dispatch<React.SetStateAction<ProposalData>>;
  step: 'analysis' | 'creation';
}

const ProposalForm: React.FC<ProposalFormProps> = ({
  proposalData,
  setProposalData,
  step,
}) => {
  const [newSkill, setNewSkill] = useState('');
  const [newPortfolioItem, setNewPortfolioItem] = useState('');

  const handleInputChange = (field: keyof ProposalData, value: any) => {
    setProposalData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleAddSkill = () => {
    if (newSkill.trim() && !proposalData.skills.includes(newSkill.trim())) {
      handleInputChange('skills', [...proposalData.skills, newSkill.trim()]);
      setNewSkill('');
    }
  };

  const handleRemoveSkill = (skillToRemove: string) => {
    handleInputChange(
      'skills',
      proposalData.skills.filter((skill) => skill !== skillToRemove)
    );
  };

  const handleAddPortfolioItem = () => {
    if (newPortfolioItem.trim() && !proposalData.portfolio.includes(newPortfolioItem.trim())) {
      handleInputChange('portfolio', [...proposalData.portfolio, newPortfolioItem.trim()]);
      setNewPortfolioItem('');
    }
  };

  const handleRemovePortfolioItem = (itemToRemove: string) => {
    handleInputChange(
      'portfolio',
      proposalData.portfolio.filter((item) => item !== itemToRemove)
    );
  };

  const calculateTotalPrice = () => {
    const total = proposalData.hourlyRate * proposalData.estimatedHours;
    handleInputChange('totalPrice', total);
  };

  React.useEffect(() => {
    calculateTotalPrice();
  }, [proposalData.hourlyRate, proposalData.estimatedHours]);

  if (step === 'analysis') {
    return (
      <Box>
        <Typography variant="h6" gutterBottom>
          Інформація про завдання
        </Typography>
        
        <Stack spacing={3}>
          <TextField
            fullWidth
            label="Назва завдання"
            value={proposalData.jobTitle}
            onChange={(e) => handleInputChange('jobTitle', e.target.value)}
            placeholder="Наприклад: Розробка веб-сайту для компанії"
          />

          <TextField
            fullWidth
            multiline
            rows={4}
            label="Опис завдання"
            value={proposalData.jobDescription}
            onChange={(e) => handleInputChange('jobDescription', e.target.value)}
            placeholder="Детальний опис того, що потрібно зробити..."
          />

          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              fullWidth
              label="Бюджет клієнта"
              value={proposalData.clientBudget}
              onChange={(e) => handleInputChange('clientBudget', e.target.value)}
              placeholder="$500-1000"
            />
            <TextField
              fullWidth
              label="Терміни клієнта"
              value={proposalData.clientTimeline}
              onChange={(e) => handleInputChange('clientTimeline', e.target.value)}
              placeholder="2-3 тижні"
            />
          </Box>

          <Box>
            <Typography variant="subtitle1" gutterBottom>
              Необхідні навички
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <TextField
                size="small"
                label="Додати навичку"
                value={newSkill}
                onChange={(e) => setNewSkill(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAddSkill()}
                sx={{ flexGrow: 1 }}
              />
              <Button
                variant="outlined"
                onClick={handleAddSkill}
                startIcon={<AddIcon />}
              >
                Додати
              </Button>
            </Box>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {proposalData.skills.map((skill, index) => (
                <Chip
                  key={index}
                  label={skill}
                  onDelete={() => handleRemoveSkill(skill)}
                  deleteIcon={<DeleteIcon />}
                />
              ))}
            </Box>
          </Box>
        </Stack>
      </Box>
    );
  }

  if (step === 'creation') {
    return (
      <Box>
        <Typography variant="h6" gutterBottom>
          Деталі пропозиції
        </Typography>
        
        <Stack spacing={3}>
          <TextField
            fullWidth
            label="Назва пропозиції"
            value={proposalData.proposalTitle}
            onChange={(e) => handleInputChange('proposalTitle', e.target.value)}
            placeholder="Професійна розробка веб-сайту"
          />

          <TextField
            fullWidth
            multiline
            rows={6}
            label="Супровідний лист"
            value={proposalData.coverLetter}
            onChange={(e) => handleInputChange('coverLetter', e.target.value)}
            placeholder="Привіт! Я зацікавлений у вашому проекті..."
          />

          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              fullWidth
              type="number"
              label="Годинна ставка"
              value={proposalData.hourlyRate}
              onChange={(e) => handleInputChange('hourlyRate', Number(e.target.value))}
              InputProps={{
                startAdornment: <InputAdornment position="start">$</InputAdornment>,
              }}
            />
            <TextField
              fullWidth
              type="number"
              label="Очікувані години"
              value={proposalData.estimatedHours}
              onChange={(e) => handleInputChange('estimatedHours', Number(e.target.value))}
            />
          </Box>

          <TextField
            fullWidth
            label="Терміни виконання"
            value={proposalData.timeline}
            onChange={(e) => handleInputChange('timeline', e.target.value)}
            placeholder="2-3 тижні"
          />

          <Box>
            <Typography variant="subtitle1" gutterBottom>
              Портфоліо (посилання на роботи)
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <TextField
                fullWidth
                size="small"
                label="Додати посилання"
                value={newPortfolioItem}
                onChange={(e) => setNewPortfolioItem(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAddPortfolioItem()}
                placeholder="https://example.com/project"
              />
              <Button
                variant="outlined"
                onClick={handleAddPortfolioItem}
                startIcon={<AddIcon />}
              >
                Додати
              </Button>
            </Box>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              {proposalData.portfolio.map((item, index) => (
                <Chip
                  key={index}
                  label={item}
                  onDelete={() => handleRemovePortfolioItem(item)}
                  deleteIcon={<DeleteIcon />}
                  variant="outlined"
                />
              ))}
            </Box>
          </Box>

          <Alert severity="info">
            Загальна вартість проекту: <strong>${proposalData.totalPrice}</strong>
          </Alert>
        </Stack>
      </Box>
    );
  }

  return null;
};

export default ProposalForm; 