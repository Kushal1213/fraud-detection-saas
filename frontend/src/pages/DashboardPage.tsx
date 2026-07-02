import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Container,
  Grid,
  Paper,
  Typography,
  Button,
  Box,
  Card,
  CardContent,
  Chip,
} from '@mui/material'
import {
  CloudUpload as CloudUploadIcon,
  Analytics as AnalyticsIcon,
  Storage as StorageIcon,
} from '@mui/icons-material'
import { useAuth } from '../contexts/AuthContext'
import { datasetService, Dataset, Analysis } from '../api/datasets'
import { toast } from 'react-toastify'

const DashboardPage: React.FC = () => {
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const [datasets, setDatasets] = useState<Dataset[]>([])
  const [analyses, setAnalyses] = useState<Analysis[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [datasetsData, analysesData] = await Promise.all([
        datasetService.getDatasets(),
        datasetService.getAnalyses(),
      ])
      setDatasets(datasetsData)
      setAnalyses(analysesData)
    } catch (error) {
      toast.error('Failed to fetch data')
    } finally {
      setLoading(false)
    }
  }

  const handleUpload = () => {
    navigate('/upload')
  }

  const handleViewAnalysis = (analysisId: number) => {
    navigate(`/analysis/${analysisId}`)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success'
      case 'processing':
        return 'warning'
      case 'failed':
        return 'error'
      default:
        return 'default'
    }
  }

  if (loading) {
    return <Container><Typography>Loading...</Typography></Container>
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h4" component="h1">
          Welcome, {user?.username}!
        </Typography>
        <Button variant="outlined" color="error" onClick={logout}>
          Logout
        </Button>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Datasets
                  </Typography>
                  <Typography variant="h4">{datasets.length}</Typography>
                </Box>
                <StorageIcon fontSize="large" color="primary" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Analyses
                  </Typography>
                  <Typography variant="h4">{analyses.length}</Typography>
                </Box>
                <AnalyticsIcon fontSize="large" color="secondary" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Account Type
                  </Typography>
                  <Typography variant="h4" textTransform="capitalize">
                    {user?.role}
                  </Typography>
                </Box>
                <CloudUploadIcon fontSize="large" color="success" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Quick Actions
        </Typography>
        <Button
          variant="contained"
          size="large"
          startIcon={<CloudUploadIcon />}
          onClick={handleUpload}
          fullWidth
        >
          Upload New Dataset
        </Button>
      </Paper>

      {/* Recent Analyses */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Recent Analyses
        </Typography>
        {analyses.length === 0 ? (
          <Typography color="textSecondary">
            No analyses yet. Upload a dataset to get started!
          </Typography>
        ) : (
          <Grid container spacing={2}>
            {analyses.slice(0, 5).map((analysis) => (
              <Grid item xs={12} key={analysis.id}>
                <Card variant="outlined">
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box>
                        <Typography variant="subtitle1">
                          Analysis #{analysis.id}
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                          {new Date(analysis.created_at).toLocaleString()}
                        </Typography>
                      </Box>
                      <Box display="flex" alignItems="center" gap={2}>
                        <Chip
                          label={analysis.status}
                          color={getStatusColor(analysis.status) as any}
                          size="small"
                        />
                        {analysis.status === 'completed' && (
                          <Button
                            size="small"
                            variant="outlined"
                            onClick={() => handleViewAnalysis(analysis.id)}
                          >
                            View Results
                          </Button>
                        )}
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Paper>
    </Container>
  )
}

export default DashboardPage
