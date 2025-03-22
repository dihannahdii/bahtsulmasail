import { useState, useEffect } from 'react';
import { Box, Typography, Card, CardContent, Button, Grid, Chip, CircularProgress, Alert } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import axios from 'axios';
import { API_ENDPOINTS } from '../config/api';

const ApprovalQueue = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchPendingDocuments();
  }, []);

  const fetchPendingDocuments = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(API_ENDPOINTS.admin.pendingDocuments, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDocuments(response.data);
    } catch (error) {
      setError('Failed to fetch pending documents');
      console.error('Error fetching documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApproval = async (documentId, approved) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(API_ENDPOINTS.admin.approveDocument(documentId), 
        { approved },
        { headers: { Authorization: `Bearer ${token}` }}
      );
      
      // Remove the approved/rejected document from the list
      setDocuments(documents.filter(doc => doc.id !== documentId));
    } catch (error) {
      setError('Failed to process approval');
      console.error('Error processing approval:', error);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ mb: 4, color: 'primary.main' }}>
        Document Approval Queue
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {documents.length === 0 ? (
        <Typography variant="h6" color="textSecondary" sx={{ textAlign: 'center', mt: 4 }}>
          No documents pending approval
        </Typography>
      ) : (
        <Grid container spacing={3}>
          {documents.map((doc) => (
            <Grid item xs={12} key={doc.id}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Typography variant="h6" gutterBottom>
                      {doc.title}
                    </Typography>
                    <Chip
                      label="Pending Review"
                      color="warning"
                      size="small"
                    />
                  </Box>

                  <Typography variant="body1" sx={{ mb: 2 }}>
                    <strong>Question:</strong> {doc.question}
                  </Typography>

                  <Typography variant="body1" sx={{ mb: 2 }}>
                    <strong>Answer:</strong> {doc.answer}
                  </Typography>

                  {doc.mushoheh && (
                    <Typography variant="body1" sx={{ mb: 2 }}>
                      <strong>Mushoheh:</strong> {doc.mushoheh}
                    </Typography>
                  )}

                  <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2, mt: 2 }}>
                    <Button
                      variant="outlined"
                      color="error"
                      startIcon={<CancelIcon />}
                      onClick={() => handleApproval(doc.id, false)}
                    >
                      Reject
                    </Button>
                    <Button
                      variant="contained"
                      color="success"
                      startIcon={<CheckCircleIcon />}
                      onClick={() => handleApproval(doc.id, true)}
                    >
                      Approve
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
};

export default ApprovalQueue;