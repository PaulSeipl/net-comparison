import { useState } from 'react'
import {
  Box,
  Typography,
  TextField,
  Button,
  CircularProgress,
  Alert,
} from '@mui/material'
import { useQuery } from 'react-query'
import axios from 'axios'

function Comparison() {
  const [address, setAddress] = useState('')
  const [isSubmitted, setIsSubmitted] = useState(false)

  const { data, isLoading, error } = useQuery(
    ['offers', address],
    async () => {
      const response = await axios.get(`/api/offers?address=${address}`)
      return response.data
    },
    {
      enabled: isSubmitted && address.length > 0,
      retry: false,
    }
  )

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitted(true)
  }

  return (
    <Box sx={{ maxWidth: 600, mx: 'auto' }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Compare Offers
      </Typography>
      <Box component="form" onSubmit={handleSubmit} sx={{ mb: 4 }}>
        <TextField
          fullWidth
          label="Enter your address"
          value={address}
          onChange={(e) => setAddress(e.target.value)}
          placeholder="street;house number;city;plz"
          sx={{ mb: 2 }}
        />
        <Button type="submit" variant="contained" disabled={!address}>
          Search
        </Button>
      </Box>

      {isLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center' }}>
          <CircularProgress />
        </Box>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error instanceof Error ? error.message : 'An error occurred'}
        </Alert>
      )}

      {data && (
        <Box>
          <Typography variant="h6" gutterBottom>
            Available Offers
          </Typography>
          {/* Add offer comparison table/component here */}
        </Box>
      )}
    </Box>
  )
}

export default Comparison 