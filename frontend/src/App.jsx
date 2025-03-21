import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';
import { rtlCache } from './rtlCache';

// Components
import Navbar from './components/Navbar';
import SearchPage from './pages/SearchPage';
import DocumentView from './pages/DocumentView';
import AdminDashboard from "./pages/AdminDashboard.jsx";
import AdminLogin from "./pages/AdminLogin.jsx";
import UploadDocument from "./pages/UploadDocument.jsx";
import ApprovalQueue from "./pages/ApprovalQueue.jsx";
import ErrorBoundary from './components/ErrorBoundary';
import ProtectedRoute from './components/ProtectedRoute';

const theme = createTheme({
  direction: 'ltr',
  typography: {
    fontFamily: '"Roboto", "Noto Kufi Arabic", sans-serif',
  },
  palette: {
    primary: {
      main: '#47A447', // NU Green color
      light: '#68B568',
      dark: '#327832'
    },
    secondary: {
      main: '#2E7D32',
      light: '#4C9A50',
      dark: '#1B5E20'
    },
    background: {
      default: '#F5F5F5',
      paper: '#FFFFFF'
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none'
        }
      }
    }
  }
});


import { AuthProvider } from './hooks/useAuth.jsx';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <ErrorBoundary>
          <Router>
            <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
              <Navbar />
              <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
                <Routes>
                  <Route path="/" element={<SearchPage />} />
                  <Route path="/document/:id" element={<DocumentView />} />
                  <Route path="/admin/login" element={<AdminLogin />} />
                  <Route path="/admin" element={
                    <ProtectedRoute>
                      <AdminDashboard />
                    </ProtectedRoute>
                  } />
                  <Route path="/admin/upload" element={
                    <ProtectedRoute>
                      <UploadDocument />
                    </ProtectedRoute>
                  } />
                  <Route path="/admin/approval" element={
                    <ProtectedRoute>
                      <ApprovalQueue />
                    </ProtectedRoute>
                  } />
                </Routes>
              </Box>
            </Box>
          </Router>
        </ErrorBoundary>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;