import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Divider,
  Grid,
  Chip,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Alert,
} from '@mui/material';
import {
  Work as WorkIcon,
  Payment as PaymentIcon,
  Schedule as ScheduleIcon,
  Star as StarIcon,
  Link as LinkIcon,
} from '@mui/icons-material';

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

interface ProposalTemplateProps {
  proposalData: ProposalData;
}

const ProposalTemplate: React.FC<ProposalTemplateProps> = ({ proposalData }) => {
  return (
    <Box>
      <Typography variant="h5" gutterBottom align="center">
        Пропозиція для завдання
      </Typography>
      
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom color="primary">
          {proposalData.proposalTitle || 'Професійна пропозиція'}
        </Typography>
        
        <Divider sx={{ my: 2 }} />
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Typography variant="h6" gutterBottom>
              Супровідний лист
            </Typography>
            <Paper variant="outlined" sx={{ p: 2, backgroundColor: '#fafafa' }}>
              <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                {proposalData.coverLetter || 'Тут буде ваш супровідний лист...'}
              </Typography>
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <PaymentIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Фінансові деталі
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemIcon>
                      <PaymentIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary="Годинна ставка"
                      secondary={`$${proposalData.hourlyRate}/год`}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <ScheduleIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary="Очікувані години"
                      secondary={`${proposalData.estimatedHours} годин`}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon>
                      <StarIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary="Загальна вартість"
                      secondary={`$${proposalData.totalPrice}`}
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Paper>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <WorkIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Інформація про завдання
              </Typography>
              <Typography variant="subtitle1" gutterBottom>
                {proposalData.jobTitle || 'Назва завдання'}
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                {proposalData.jobDescription || 'Опис завдання...'}
              </Typography>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Бюджет клієнта: {proposalData.clientBudget}
                </Typography>
                <Typography variant="subtitle2" gutterBottom>
                  Терміни клієнта: {proposalData.clientTimeline}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <ScheduleIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Ваші умови
              </Typography>
              <Typography variant="subtitle2" gutterBottom>
                Терміни виконання: {proposalData.timeline}
              </Typography>
              
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Необхідні навички:
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {proposalData.skills.map((skill, index) => (
                    <Chip key={index} label={skill} size="small" />
                  ))}
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {proposalData.portfolio.length > 0 && (
        <Paper sx={{ p: 3, mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            <LinkIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Портфоліо
          </Typography>
          <List>
            {proposalData.portfolio.map((item, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  <LinkIcon />
                </ListItemIcon>
                <ListItemText
                  primary={item}
                  secondary="Посилання на роботу"
                />
              </ListItem>
            ))}
          </List>
        </Paper>
      )}

      <Alert severity="success" sx={{ mt: 3 }}>
        <Typography variant="body1">
          <strong>Пропозиція готова до відправки!</strong>
        </Typography>
        <Typography variant="body2">
          Перевірте всі деталі та натисніть "Відправити пропозицію"
        </Typography>
      </Alert>
    </Box>
  );
};

export default ProposalTemplate; 