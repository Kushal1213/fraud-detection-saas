import React, { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { datasetService, Analysis } from '../api/datasets'

const AnalysisResultsPage: React.FC = () => {
  const navigate = useNavigate()
  const { analysisId } = useParams<{ analysisId: string }>()
  const [analysis, setAnalysis] = useState<Analysis | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAnalysis()
  }, [analysisId])

  useEffect(() => {
    let interval: NodeJS.Timeout
    
    if (analysis?.status === 'processing' || analysis?.status === 'pending') {
      interval = setInterval(() => {
        fetchAnalysis()
      }, 3000)
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
      console.error('Failed to fetch analysis results')
      setLoading(false)
    }
  }

  if (loading) {
    return <div style={{ padding: '20px', textAlign: 'center' }}>Loading...</div>
  }

  if (!analysis) {
    return <div style={{ padding: '20px' }}>Analysis not found</div>
  }

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      <button
        onClick={() => navigate('/dashboard')}
        style={{ padding: '10px 20px', backgroundColor: '#6c757d', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', marginBottom: '20px' }}
      >
        ← Back to Dashboard
      </button>

      <div style={{ padding: '30px', border: '1px solid #ddd', borderRadius: '8px', marginBottom: '30px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
          <h1>Analysis Results #{analysis.id}</h1>
          <span style={{
            padding: '10px 20px',
            borderRadius: '4px',
            fontSize: '14px',
            backgroundColor: analysis.status === 'completed' ? '#4caf50' : analysis.status === 'processing' ? '#ff9800' : '#f44336',
            color: 'white'
          }}>
            {analysis.status.toUpperCase()}
          </span>
        </div>

        {analysis.status === 'processing' || analysis.status === 'pending' ? (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>⏳</div>
            <h2>{analysis.status === 'processing' ? 'Processing your dataset...' : 'Starting analysis...'}</h2>
            <p style={{ color: '#666' }}>This may take a few moments</p>
          </div>
        ) : analysis.status === 'failed' ? (
          <div style={{ padding: '20px', backgroundColor: '#fee', borderRadius: '4px', color: '#c33' }}>
            Analysis failed: {analysis.error_message || 'Unknown error'}
          </div>
        ) : (
          <div>
            {/* Summary Stats */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '30px' }}>
              <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px', backgroundColor: '#f8f9fa' }}>
                <h3>Total Transactions</h3>
                <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#1976d2' }}>{analysis.total_transactions?.toLocaleString()}</p>
              </div>
              <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px', backgroundColor: '#f8f9fa' }}>
                <h3>Fraudulent Transactions</h3>
                <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#dc004e' }}>{analysis.fraud_count?.toLocaleString()}</p>
              </div>
              <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px', backgroundColor: '#f8f9fa' }}>
                <h3>Fraud Rate</h3>
                <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#ff9800' }}>{(analysis.fraud_rate * 100).toFixed(2)}%</p>
              </div>
              <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px', backgroundColor: '#f8f9fa' }}>
                <h3>Avg Fraud Score</h3>
                <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#4caf50' }}>{analysis.avg_fraud_score?.toFixed(4)}</p>
              </div>
            </div>

            {/* Simple visual representation */}
            <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px', marginBottom: '30px' }}>
              <h2>Fraud vs Legitimate</h2>
              <div style={{ marginTop: '20px' }}>
                <div style={{ marginBottom: '10px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                    <span>Fraudulent</span>
                    <span>{analysis.fraud_count} ({(analysis.fraud_rate * 100).toFixed(1)}%)</span>
                  </div>
                  <div style={{ height: '30px', backgroundColor: '#ef4444', borderRadius: '4px', width: `${analysis.fraud_rate * 100}%` }}></div>
                </div>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                    <span>Legitimate</span>
                    <span>{analysis.total_transactions - analysis.fraud_count} ({((1 - analysis.fraud_rate) * 100).toFixed(1)}%)</span>
                  </div>
                  <div style={{ height: '30px', backgroundColor: '#22c55e', borderRadius: '4px', width: `${(1 - analysis.fraud_rate) * 100}%` }}></div>
                </div>
              </div>
            </div>

            {/* SHAP Explanations */}
            {analysis.shap_explanations && (
              <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
                <h2>Feature Importance (SHAP)</h2>
                <div style={{ marginTop: '20px' }}>
                  {Object.entries(analysis.shap_explanations)
                    .sort(([, a], [, b]) => Math.abs(b as number) - Math.abs(a as number))
                    .slice(0, 10)
                    .map(([feature, importance]) => (
                      <div key={feature} style={{ marginBottom: '15px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                          <span>{feature}</span>
                          <span style={{ color: (importance as number) > 0 ? '#ef4444' : '#22c55e' }}>
                            {(importance as number).toFixed(4)}
                          </span>
                        </div>
                        <div style={{ height: '8px', backgroundColor: '#e0e0e0', borderRadius: '4px', overflow: 'hidden' }}>
                          <div style={{
                            height: '100%',
                            width: `${Math.abs(importance as number) * 100}%`,
                            backgroundColor: (importance as number) > 0 ? '#ef4444' : '#22c55e'
                          }}></div>
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default AnalysisResultsPage
