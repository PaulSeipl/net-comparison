import { Typography, Button, Box } from '@mui/material'
import { useNavigate } from 'react-router-dom'

function Home() {
  const navigate = useNavigate()

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 4,
        py: 8,
      }}
    >
      <Typography variant="h3" component="h1" align="center">
        Compare Internet Providers
      </Typography>
      <Typography variant="h6" align="center" color="text.secondary">
        Find the best internet provider for your needs
      </Typography>
      <Button
        variant="contained"
        size="large"
        onClick={() => navigate('/comparison')}
      >
        Start Comparison
      </Button>
    </Box>
  )
}

export default Home 