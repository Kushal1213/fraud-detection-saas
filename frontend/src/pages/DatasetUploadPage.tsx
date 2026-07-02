import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { datasetService } from '../api/datasets'

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
      
      // Automatically create analysis
      const analysis = await datasetService.createAnalysis(dataset.id)
      
      navigate(`/analysis/${analysis.id}`)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div style={{ maxWidth: '600px', margin: '50px auto', padding: '20px' }}>
      <button
        onClick={() => navigate('/dashboard')}
        style={{ padding: '10px 20px', backgroundColor: '#6c757d', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', marginBottom: '20px' }}
      >
        ← Back to Dashboard
      </button>
      
      <div style={{ padding: '30px', border: '1px solid #ddd', borderRadius: '8px' }}>
        <h1>Upload Dataset</h1>
        <p style={{ color: '#666' }}>Upload your transaction data (CSV, XLSX, or JSON format)</p>

        {error && <div style={{ color: 'red', marginBottom: '15px', padding: '10px', backgroundColor: '#fee', borderRadius: '4px' }}>{error}</div>}

        <form onSubmit={handleSubmit}>
          <div
            onClick={() => document.getElementById('file-input')?.click()}
            style={{
              border: '2px dashed #1976d2',
              borderRadius: '8px',
              padding: '40px',
              textAlign: 'center',
              marginBottom: '20px',
              cursor: 'pointer',
              backgroundColor: '#f8f9fa'
            }}
          >
            <div style={{ fontSize: '48px', marginBottom: '10px' }}>📁</div>
            <p>{file ? file.name : 'Click to select a file'}</p>
            <p style={{ color: '#666', fontSize: '14px' }}>CSV, XLSX, or JSON (max 10MB)</p>
            <input
              id="file-input"
              type="file"
              accept=".csv,.xlsx,.json"
              onChange={handleFileChange}
              style={{ display: 'none' }}
            />
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label>Dataset Name:</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              style={{ width: '100%', padding: '10px', marginTop: '5px', border: '1px solid #ddd', borderRadius: '4px' }}
            />
          </div>

          <button
            type="submit"
            disabled={uploading || !file}
            style={{
              width: '100%',
              padding: '15px',
              backgroundColor: uploading ? '#6c757d' : '#1976d2',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: uploading ? 'not-allowed' : 'pointer',
              fontSize: '16px'
            }}
          >
            {uploading ? 'Uploading...' : 'Upload and Analyze'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default DatasetUploadPage
