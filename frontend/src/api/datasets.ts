import api from './client'

export interface Dataset {
  id: number
  name: string
  filename: string
  file_size?: number
  row_count?: number
  column_count?: number
  status: string
  error_message?: string
  created_at: string
}

export interface Analysis {
  id: number
  dataset_id: number
  status: string
  total_transactions?: number
  fraud_count?: number
  fraud_rate?: number
  avg_fraud_score?: number
  auroc_score?: number
  processing_time?: number
  error_message?: string
  results?: any
  shap_explanations?: any
  created_at: string
  completed_at?: string
}

export const datasetService = {
  async uploadDataset(file: File, name: string): Promise<Dataset> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('name', name)

    const response = await api.post('/datasets', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  async getDatasets(): Promise<Dataset[]> {
    const response = await api.get('/datasets')
    return response.data
  },

  async getDataset(id: number): Promise<Dataset> {
    const response = await api.get(`/datasets/${id}`)
    return response.data
  },

  async createAnalysis(datasetId: number): Promise<Analysis> {
    const response = await api.post('/analyses', { dataset_id: datasetId })
    return response.data
  },

  async getAnalyses(): Promise<Analysis[]> {
    const response = await api.get('/analyses')
    return response.data
  },

  async getAnalysis(id: number): Promise<Analysis> {
    const response = await api.get(`/analyses/${id}`)
    return response.data
  },
}
