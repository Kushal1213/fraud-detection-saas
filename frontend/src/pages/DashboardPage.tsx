import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { datasetService, Dataset, Analysis } from '../api/datasets'

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
      console.error('Failed to fetch data')
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

  if (loading) {
    return <div style={{ padding: '20px' }}>Loading...</div>
  }

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h1>Welcome, {user?.username}!</h1>
        <button onClick={logout} style={{ padding: '10px 20px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
          Logout
        </button>
      </div>

      {/* Stats Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '30px' }}>
        <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px', backgroundColor: '#f8f9fa' }}>
          <h3>Total Datasets</h3>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#1976d2' }}>{datasets.length}</p>
        </div>
        <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px', backgroundColor: '#f8f9fa' }}>
          <h3>Total Analyses</h3>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#dc004e' }}>{analyses.length}</p>
        </div>
        <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px', backgroundColor: '#f8f9fa' }}>
          <h3>Account Type</h3>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#4caf50', textTransform: 'capitalize' }}>{user?.role}</p>
        </div>
      </div>

      {/* Quick Actions */}
      <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px', marginBottom: '30px' }}>
        <h2>Quick Actions</h2>
        <button
          onClick={handleUpload}
          style={{ width: '100%', padding: '15px', backgroundColor: '#1976d2', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '16px' }}
        >
          Upload New Dataset
        </button>
      </div>

      {/* Recent Analyses */}
      <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '8px' }}>
        <h2>Recent Analyses</h2>
        {analyses.length === 0 ? (
          <p style={{ color: '#666' }}>No analyses yet. Upload a dataset to get started!</p>
        ) : (
          <div>
            {analyses.slice(0, 5).map((analysis) => (
              <div key={analysis.id} style={{ padding: '15px', border: '1px solid #eee', borderRadius: '4px', marginBottom: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h3>Analysis #{analysis.id}</h3>
                  <p style={{ color: '#666', fontSize: '14px' }}>{new Date(analysis.created_at).toLocaleString()}</p>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ padding: '5px 10px', borderRadius: '4px', fontSize: '12px', backgroundColor: analysis.status === 'completed' ? '#4caf50' : analysis.status === 'processing' ? '#ff9800' : '#f44336', color: 'white' }}>
                    {analysis.status.toUpperCase()}
                  </span>
                  {analysis.status === 'completed' && (
                    <button
                      onClick={() => handleViewAnalysis(analysis.id)}
                      style={{ padding: '8px 16px', backgroundColor: '#1976d2', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                    >
                      View Results
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default DashboardPage
