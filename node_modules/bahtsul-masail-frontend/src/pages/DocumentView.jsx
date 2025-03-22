import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Paper,
  Typography,
  Chip,
  Divider,
  Skeleton,
  Alert,
  Container
} from '@mui/material';
import axios from 'axios';
import { API_ENDPOINTS } from '../config/api';

const DocumentView = () => {
  const { id } = useParams();
  const [document, setDocument] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDocument = async () => {
      try {
        const response = await axios.get(`${API_ENDPOINTS.documents}/${id}`);
        setDocument(response.data);
        setError(null);
      } catch (error) {
        setError('Error loading document. Please try again later.');
        console.error('Error fetching document:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchDocument();
  }, [id]);

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Skeleton variant="text" height={60} />
        <Skeleton variant="rectangular" height={200} sx={{ my: 2 }} />
        <Skeleton variant="text" height={40} />
        <Skeleton variant="rectangular" height={100} sx={{ my: 2 }} />
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  if (!document) return null;

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper elevation={2} sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ color: 'primary.main', fontWeight: 'bold' }}>
          {document.title}
        </Typography>

        <Box sx={{ display: 'flex', gap: 1, mb: 3, flexWrap: 'wrap' }}>
          {document.madhabs?.map((madhab) => (
            <Chip
              key={madhab.id}
              label={madhab.name}
              color="primary"
              variant="outlined"
              size="small"
            />
          ))}
          {document.categories?.map((category) => (
            <Chip
              key={category.id}
              label={category.name}
              color="secondary"
              variant="outlined"
              size="small"
            />
          ))}
        </Box>

        {document.prolog && (
          <Box sx={{ mb: 4 }}>
            <Typography variant="h6" gutterBottom color="text.secondary">
              Prolog
            </Typography>
            <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>
              {document.prolog}
            </Typography>
          </Box>
        )}

        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" gutterBottom color="text.secondary">
            Question
          </Typography>
          <Typography
            variant="body1"
            sx={{
              backgroundColor: 'grey.50',
              p: 2,
              borderRadius: 1,
              whiteSpace: 'pre-line'
            }}
          >
            {document.question}
          </Typography>
        </Box>

        <Divider sx={{ my: 4 }} />

        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" gutterBottom color="text.secondary">
            Answer
          </Typography>
          <Typography
            variant="body1"
            sx={{
              backgroundColor: 'primary.50',
              p: 2,
              borderRadius: 1,
              whiteSpace: 'pre-line'
            }}
          >
            {document.answer}
          </Typography>
        </Box>

        {document.mushoheh && (
          <Box sx={{ mb: 4 }}>
            <Typography variant="h6" gutterBottom color="text.secondary">
              Mushoheh
            </Typography>
            <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>
              {document.mushoheh}
            </Typography>
          </Box>
        )}

        {document.source_document && (
          <Box sx={{ mt: 4 }}>
            <Typography variant="h6" gutterBottom color="text.secondary">
              Source Document
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {document.source_document}
            </Typography>
          </Box>
        )}

        {(document.historical_context || document.geographical_context || document.publication_date) && (
          <Box sx={{ mt: 4, pt: 2, borderTop: 1, borderColor: 'divider' }}>
            <Typography variant="overline" display="block" gutterBottom>
              Additional Information
            </Typography>
            {document.historical_context && (
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Historical Context: {document.historical_context}
              </Typography>
            )}
            {document.geographical_context && (
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Geographical Context: {document.geographical_context}
              </Typography>
            )}
            {document.publication_date && (
              <Typography variant="body2" color="text.secondary">
                Publication Date: {new Date(document.publication_date).toLocaleDateString()}
              </Typography>
            )}
          </Box>
        )}
      </Paper>
    </Container>
  );
};

export default DocumentView;