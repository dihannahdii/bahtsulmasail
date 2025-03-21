import { useState } from 'react';
import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  OutlinedInput,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  TextField
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

const SearchFilters = ({
  madhabs,
  categories,
  selectedMadhabs,
  selectedCategories,
  startDate,
  endDate,
  onMadhabChange,
  onCategoryChange,
  onStartDateChange,
  onEndDateChange
}) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <Accordion
      expanded={expanded}
      onChange={() => setExpanded(!expanded)}
      sx={{ mb: 2, backgroundColor: 'background.paper' }}
    >
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Typography>Advanced Filters</Typography>
      </AccordionSummary>
      <AccordionDetails>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <FormControl fullWidth>
            <InputLabel>Madhab</InputLabel>
            <Select
              multiple
              value={selectedMadhabs}
              onChange={onMadhabChange}
              input={<OutlinedInput label="Madhab" />}
              renderValue={(selected) => (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {selected.map((value) => {
                    const madhab = madhabs.find(m => m.id === value);
                    return madhab ? madhab.name : '';
                  })}
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

          <FormControl fullWidth>
            <InputLabel>Category</InputLabel>
            <Select
              multiple
              value={selectedCategories}
              onChange={onCategoryChange}
              input={<OutlinedInput label="Category" />}
              renderValue={(selected) => (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {selected.map((value) => {
                    const category = categories.find(c => c.id === value);
                    return category ? category.name : '';
                  })}
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

          <LocalizationProvider dateAdapter={AdapterDateFns}>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <DatePicker
                label="Start Date"
                value={startDate}
                onChange={onStartDateChange}
                renderInput={(params) => <TextField {...params} fullWidth />}
              />
              <DatePicker
                label="End Date"
                value={endDate}
                onChange={onEndDateChange}
                renderInput={(params) => <TextField {...params} fullWidth />}
              />
            </Box>
          </LocalizationProvider>
        </Box>
      </AccordionDetails>
    </Accordion>
  );
};

export default SearchFilters;