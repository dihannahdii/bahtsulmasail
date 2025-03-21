import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import SearchIcon from '@mui/icons-material/Search';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import PendingActionsIcon from '@mui/icons-material/PendingActions';

const Navbar = () => {
  const navigate = useNavigate();
  const { isAuthenticated, logout } = useAuth();

  return (
    <AppBar position="sticky" elevation={1} sx={{ backgroundColor: 'white' }}>
      <Toolbar>
        <MenuBookIcon sx={{ mr: 2, color: 'primary.main' }} />
        <Typography
          variant="h6"
          component="div"
          sx={{
            flexGrow: 1,
            color: 'primary.main',
            fontWeight: 'bold',
            cursor: 'pointer'
          }}
          onClick={() => navigate('/')}
        >
          Bahtsul Masail
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            color="primary"
            startIcon={<SearchIcon />}
            onClick={() => navigate('/')}
          >
            Search
          </Button>
          {isAuthenticated ? (
            <>
              <Button
                color="primary"
                startIcon={<AdminPanelSettingsIcon />}
                onClick={() => navigate('/admin')}
              >
                Dashboard
              </Button>
              <Button
                color="primary"
                startIcon={<UploadFileIcon />}
                onClick={() => navigate('/admin/upload')}
              >
                Upload
              </Button>
              <Button
                color="primary"
                startIcon={<PendingActionsIcon />}
                onClick={() => navigate('/admin/approval')}
              >
                Approvals
              </Button>
              <Button
                color="primary"
                onClick={logout}
              >
                Logout
              </Button>
            </>
          ) : (
            <Button
              color="primary"
              startIcon={<AdminPanelSettingsIcon />}
              onClick={() => navigate('/admin/login')}
            >
              Admin Login
            </Button>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;