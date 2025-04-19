import { Routes, Route } from 'react-router-dom'
import { Box, Container } from '@mui/material'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Comparison from './pages/Comparison'
import NotFound from './pages/NotFound'

function App() {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navbar />
      <Container component="main" sx={{ flex: 1, py: 4 }}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/comparison" element={<Comparison />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Container>
    </Box>
  )
}

export default App 