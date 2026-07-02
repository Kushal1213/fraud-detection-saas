import React, { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  Container,
  Paper,
  Typography,
  Box,
  Button,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Chip,
  Divider,
} from '@mui/material'
import {
  ArrowBack as ArrowBackIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
} from '@mui/icons-material'
import { datasetService, Analysis } from '../api/datasets'
import { toast } from 'react-toastify'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts'

const AnalysisResultsPage: React.FC = () => {
  const navigate = useNavigate()
  const { analysisId } = useParams<{ analysisId: string }>()
  const [analysis, setAnalysis] = useState<Analysis | null>(null)
  const [loading, setLoading] = useState(true)
  const [polling, setPolling] = useState(false)

  useEffect(() => {
    fetchAnalysis()
  }, [analysisId])

  useEffect(() => {
    let interval: NodeJS.Timeout
    
    if (analysis?.status === 'processing' || analysis?.status === 'pending') {
      setPolling(true)
      interval = setInterval(() => {
        fetchAnalysis()
      }, 3000) // Poll every 3 seconds
    } else {
      setPolling(false)
    }

    return () => {
      if (interval) clearInterval(interval)
    }
  }, [analysis?.status])

  const fetchAnalysis = async () => {
    try {
      const data = await datasetService.getAnalysis(Number(analysisId))
      setAnalysis(data)
      setLoading(false)
    } catch (error) {
      toast.error('Failed to fetch analysis results')
      setLoading(false)
    }
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
    return (
      <Container maxWidth="lg" sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    )
  }

  if (!analysis) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">Analysis not found</Alert>
      </Container>
    )
  }

  // Prepare chart data
  const pieData = analysis.total_transactions
    ? [
        { name: 'Fraud', value: analysis.fraud_count || 0, color: '#ef4444' },
        { name: 'Legitimate', value: (analysis.total_transactions - (analysis.fraud_count || 0)), color: '#22c55e' },
      ]
    : []

  const fraudDistribution = analysis.results?.predictions
    ? (() => {
        const predictions = analysis.results.predictions
        const ranges = {
          '0-0.2': 0,
          '0.2-0.4': 0,
          '0.4-0.6': 0,
          '0.6-0.8': 0,
          '0.8-1.0': 0,
        }
        
        predictions.forEach((prob: number) => {
          if (prob < 0.2) ranges['0-0.2']++
          else if (prob < 0.4) ranges['0.2-0.4']++
          else if (prob < 0.6) ranges['0.4-0.6']++
          else if (prob < 0.8) ranges['0.6-0.8']++
          else ranges['0.8-1.0']++
        })
        
        return Object.entries(ranges).map(([name, value]) => ({ name, value }))
      })()
    : []

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Button
        startIcon={<ArrowBackIcon />}
        onClick={() => navigate('/dashboard')}
        sx={{ mb: 2 }}
      >
        Back to Dashboard
      </Button>

      <Paper elevation={3} sx={{ p: 4, mb: 4 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4" component="h1">
            Analysis Results #{analysis.id}
          </Typography>
          <Chip
            label={analysis.status.toUpperCase()}
            color={getStatusColor(analysis.status) as any}
            icon={analysis.status === 'completed' ? <CheckCircleIcon /> : analysis.status === 'failed' ? <ErrorIcon /> : undefined}
          />
        </Box>

        {analysis.status === 'processing' || analysis.status === 'pending' ? (
          <Box display="flex" flexDirection="column" alignItems="center" py={4}>
            <CircularProgress size={60} sx={{ mb: 2 }} />
            <Typography variant="h6">
              {analysis.status === 'processing' ? 'Processing your dataset...' : 'Starting analysis...'}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              This may take a few moments
            </Typography>
          </Box>
        ) : analysis.status === 'failed' ? (
          <Alert severity="error">
            Analysis failed: {analysis.error_message || 'Unknown error'}
          </Alert>
        ) : (
          <Grid container spacing={3}>
            {/* Summary Stats */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Summary Statistics
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <Box>
                      <Typography color="textSecondary">Total Transactions</Typography>
                      <Typography variant="h4">{analysis.total_transactions?.toLocaleString()}</Typography>
                    </Box>
                    <Box>
                      <Typography color="textSecondary">Fraudulent Transactions</Typography>
                      <Typography variant="h4" color="error">{analysis.fraud_count?.toLocaleString()}</Typography>
                    </Box>
                    <Box>
                      <Typography color="textSecondary">Fraud Rate</Typography>
                      <Typography variant="h4">{(analysis.fraud_rate * 100).toFixed(2)}%</Typography>
                    </Box>
                    <Box>
                      <Typography color="textSecondary">Average Fraud Score</Typography>
                      <Typography variant="h4">{analysis.avg_fraud_score?.toFixed(4)}</Typography>
                    </Box>
                    <Box>
                      <Typography color="textSecondary">Processing Time</Typography>
                      <Typography variant="h4">{analysis.processing_time?.toFixed(2)}s</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Pie Chart */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Fraud vs Legitimate
                  </Typography>
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {pieData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>

            {/* Fraud Score Distribution */}
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Fraud Score Distribution
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={fraudDistribution}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="value" fill="#1976d2" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>

            {/* SHAP Explanations */}
            {analysis.shap_explanations && (
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Feature Importance (SHAP)
                    </Typography>
                    <Box sx={{ mt: 2 }}>
                      {Object.entries(analysis.shap_explanations)
                        .sort(([, a], [, b]) => Math.abs(b as number) - Math.abs(a as number))
                        .slice(0, 10)
                        .map(([feature, importance]) => (
                          <Box key={feature} sx={{ mb: 1 }}>
                            <Box display="flex" justifyContent="space-between">
                              <Typography variant="body2">{feature}</Typography>
                              <Typography variant="body2" color={(importance as number) > 0 ? 'error' : 'success'}>
                                {(importance as number).toFixed(4)}
                              </Typography>
                            </Box>
                            <Box
                              sx={{
                                height: 8,
                                backgroundColor: '#e0e0e0',
                                borderRadius: 4,
                                overflow: 'hidden',
                              }}
                            >
                              <Box
                                sx={{
                                  height: '100%',
                                  width: `${Math.abs(importance as number) * 100}%`,
                                  backgroundColor: (importance as number) > 0 ? '#ef4444' : '#22c55e',
                                }}
                              />
                            </Box>
                          </Box>
                        ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            )}
          </Grid>
        )}
      </Paper>
    </Container>
  )
}

export default AnalysisResultsPage
