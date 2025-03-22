import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Grid, Paper, Typography, Button, Card, CardContent, CircularProgress } from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import AssignmentIcon from '@mui/icons-material/Assignment';
import PendingActionsIcon from '@mui/icons-material/PendingActions';
import axios from 'axios';
import { API_ENDPOINTS } from '../config/api';

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    totalDocuments: 0,
    pendingApprovals: 0,
    recentUploads: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(API_ENDPOINTS.admin.stats, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setStats(response.data);
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const DashboardCard = ({ title, value, icon, color }) => (
    <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        {icon}
        <Typography variant="h6" sx={{ ml: 1 }}>
          {title}
        </Typography>
      </Box>
      <Typography variant="h4" sx={{ color: color }}>
        {value}
      </Typography>
    </Paper>
  );

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" sx={{ color: 'primary.main' }}>
          Admin Dashboard
        </Typography>
        <Box>
          <Button
            variant="contained"
            startIcon={<UploadFileIcon />}
            onClick={() => navigate('/admin/upload')}
            sx={{ mr: 2 }}
          >
            Upload Document
          </Button>
          <Button
            variant="outlined"
            startIcon={<PendingActionsIcon />}
            onClick={() => navigate('/admin/approval')}
          >
            Pending Approvals
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <DashboardCard
            title="Total Documents"
            value={stats.totalDocuments}
            icon={<AssignmentIcon color="primary" />}
            color="primary.main"
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <DashboardCard
            title="Pending Approvals"
            value={stats.pendingApprovals}
            icon={<PendingActionsIcon color="warning" />}
            color="warning.main"
          />
        </Grid>
      </Grid>

      <Typography variant="h5" sx={{ mb: 3 }}>
        Recent Uploads
      </Typography>
      <Grid container spacing={3}>
        {stats.recentUploads.map((doc, index) => (
          <Grid item xs={12} md={6} key={index}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {doc.title}
                </Typography>
                <Typography color="textSecondary">
                  Uploaded: {new Date(doc.uploadDate).toLocaleDateString()}
                </Typography>
                <Typography color="textSecondary">
                  Status: {doc.status}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default AdminDashboard;