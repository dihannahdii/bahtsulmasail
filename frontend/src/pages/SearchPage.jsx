import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  TextField,
  Card,
  CardContent,
  Typography,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  OutlinedInput,
  Grid,
  Button,
  Paper,
  IconButton,
  InputAdornment,
  CircularProgress
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import FilterListIcon from '@mui/icons-material/FilterList';
import axios from 'axios';

const SearchPage = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [madhabs, setMadhabs] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedMadhabs, setSelectedMadhabs] = useState([]);
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    // Fetch madhabs and categories on component mount
    const fetchFilters = async () => {
      try {
        const [madhabsRes, categoriesRes] = await Promise.all([
          axios.get('http://localhost:8000/api/madhabs'),
          axios.get('http://localhost:8000/api/categories')
        ]);
        setMadhabs(madhabsRes.data);
        setCategories(categoriesRes.data);
      } catch (error) {
        console.error('Error fetching filters:', error);
      }
    };
    fetchFilters();
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/api/documents/search', {
        query: searchQuery,
        madhab_ids: selectedMadhabs,
        category_ids: selectedCategories
      });
      setSearchResults(response.data);
    } catch (error) {
      console.error('Error searching documents:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', mt: 4 }}>
      <Paper elevation={0} sx={{ p: 4, backgroundColor: 'transparent' }}>
        <Typography
          variant="h3"
          align="center"
          sx={{ mb: 4, fontWeight: 'bold', color: 'primary.main' }}
        >
          Bahtsul Masail Search
        </Typography>
        
        <form onSubmit={handleSearch}>
          <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
            <TextField
              fullWidth
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search for questions, answers, or topics..."
              variant="outlined"
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    {loading ? (
                      <CircularProgress size={24} />
                    ) : (
                      <IconButton type="submit">
                        <SearchIcon />
                      </IconButton>
                    )}
                  </InputAdornment>
                )
              }}
            />
            <Button
              variant="outlined"
              startIcon={<FilterListIcon />}
              onClick={() => setShowFilters(!showFilters)}
            >
              Filters
            </Button>
          </Box>

          {showFilters && (
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Madhabs</InputLabel>
                  <Select
                    multiple
                    value={selectedMadhabs}
                    onChange={(e) => setSelectedMadhabs(e.target.value)}
                    input={<OutlinedInput label="Madhabs" />}
                    renderValue={(selected) => (
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {selected.map((value) => (
                          <Chip
                            key={value}
                            label={madhabs.find(m => m.id === value)?.name}
                            size="small"
                          />
                        ))}
                      </Box>
                    )}
                  >
                    {madhabs.map((madhab) => (
                      <MenuItem key={madhab.id} value={madhab.id}>
                        {madhab.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Categories</InputLabel>
                  <Select
                    multiple
                    value={selectedCategories}
                    onChange={(e) => setSelectedCategories(e.target.value)}
                    input={<OutlinedInput label="Categories" />}
                    renderValue={(selected) => (
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {selected.map((value) => (
                          <Chip
                            key={value}
                            label={categories.find(c => c.id === value)?.name}
                            size="small"
                          />
                        ))}
                      </Box>
                    )}
                  >
                    {categories.map((category) => (
                      <MenuItem key={category.id} value={category.id}>
                        {category.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          )}
        </form>

        <Box sx={{ mt: 4 }}>
          {searchResults.map((document) => (
            <Card
              key={document.id}
              sx={{
                mb: 2,
                cursor: 'pointer',
                '&:hover': { boxShadow: 3 },
                transition: 'box-shadow 0.2s'
              }}
              onClick={() => navigate(`/document/${document.id}`)}
            >
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {document.title}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  {document.question.length > 200
                    ? `${document.question.substring(0, 200)}...`
                    : document.question}
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {document.madhabs.map((madhab) => (
                    <Chip
                      key={madhab.id}
                      label={madhab.name}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  ))}
                  {document.categories.map((category) => (
                    <Chip
                      key={category.id}
                      label={category.name}
                      size="small"
                      color="secondary"
                      variant="outlined"
                    />
                  ))}
                </Box>
              </CardContent>
            </Card>
          ))}
          {searchResults.length === 0 && searchQuery && !loading && (
            <Typography align="center" color="text.secondary">
              No results found. Try different keywords or filters.
            </Typography>
          )}
        </Box>
      </Paper>
    </Box>
  );
};

export default SearchPage;