import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Container,
  Paper,
  Typography,
  Box,
  Button,
  TextField,
  CircularProgress,
  Alert,
} from '@mui/material'
import { CloudUpload as CloudUploadIcon } from '@mui/icons-material'
import { datasetService } from '../api/datasets'
import { toast } from 'react-toastify'

const DatasetUploadPage: React.FC = () => {
  const navigate = useNavigate()
  const [file, setFile] = useState<File | null>(null)
  const [name, setName] = useState('')
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      if (!name) {
        setName(e.target.files[0].name.replace(/\.[^/.]+$/, ''))
      }
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!file) {
      setError('Please select a file to upload')
      return
    }

    if (!name) {
      setError('Please provide a name for the dataset')
      return
    }

    setUploading(true)

    try {
      const dataset = await datasetService.uploadDataset(file, name)
      toast.success('Dataset uploaded successfully!')
      
      // Automatically create analysis
      const analysis = await datasetService.createAnalysis(dataset.id)
      toast.success('Analysis started!')
      
      navigate(`/analysis/${analysis.id}`)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed')
      toast.error('Upload failed')
    } finally {
      setUploading(false)
    }
  }

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 4 }}>
        <Button
          onClick={() => navigate('/dashboard')}
          sx={{ mb: 2 }}
        >
          ← Back to Dashboard
        </Button>
        
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography component="h1" variant="h5" gutterBottom>
            Upload Dataset
          </Typography>
          <Typography variant="body2" color="textSecondary" gutterBottom>
            Upload your transaction data (CSV, XLSX, or JSON format)
          </Typography>

          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

          <Box component="form" onSubmit={handleSubmit}>
            <Box
              sx={{
                border: '2px dashed',
                borderColor: 'primary.main',
                borderRadius: 2,
                p: 4,
                textAlign: 'center',
                mb: 2,
                cursor: 'pointer',
                '&:hover': {
                  backgroundColor: 'action.hover',
                },
              }}
              onClick={() => document.getElementById('file-input')?.click()}
            >
              <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
              <Typography variant="body1">
                {file ? file.name : 'Click to select a file'}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                CSV, XLSX, or JSON (max 10MB)
              </Typography>
              <input
                id="file-input"
                type="file"
                accept=".csv,.xlsx,.json"
                onChange={handleFileChange}
                style={{ display: 'none' }}
              />
            </Box>

            <TextField
              margin="normal"
              required
              fullWidth
              id="name"
              label="Dataset Name"
              name="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              sx={{ mb: 2 }}
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={uploading || !file}
              startIcon={uploading ? <CircularProgress size={20} /> : <CloudUploadIcon />}
            >
              {uploading ? 'Uploading...' : 'Upload and Analyze'}
            </Button>
          </Box>
        </Paper>
      </Box>
    </Container>
  )
}

export default DatasetUploadPage
