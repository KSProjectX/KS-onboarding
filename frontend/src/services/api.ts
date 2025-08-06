import axios, { AxiosInstance, AxiosResponse } from 'axios'
import toast from 'react-hot-toast'

// Types for API responses
export interface ApiResponse<T = any> {
  status: 'success' | 'error'
  data?: T
  message?: string
  workflow_id?: string
  execution_time?: number
}

export interface ProgrammeData {
  client_name: string
  industry: string
  problem_statement: string
  tech_stack: string[]
  budget_range?: string
  timeline?: string
  stakeholders?: string[]
  requirements?: string
  goals?: string
}

export interface ValidationResult {
  is_valid: boolean
  completeness_score: number
  missing_fields: string[]
  suggestions: string[]
}

export interface DashboardData {
  use_cases: any[]
  client_profiles: any[]
  insights: any[]
  meetings: any[]
  validations: any[]
  system_metrics?: {
    total_workflows: number
    active_workflows: number
    completed_workflows: number
    failed_workflows: number
  }
}

export interface WorkflowResult {
  workflow_id: string
  status: string
  execution_time: number
  client_name: string
  summary: {
    programme_setup: any
    domain_knowledge: any
    client_profile: any
    meetings: any
    actionable_insights: any
  }
  full_results: any
}

export interface SearchResult {
  search_results: {
    database_results: any[]
    domain_insights: any
    query: string
    industry_filter?: string
  }
}

// Create axios instance with default configuration
const createApiInstance = (): AxiosInstance => {
  const instance = axios.create({
    baseURL: (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000',
    timeout: 30000, // 30 seconds
    headers: {
      'Content-Type': 'application/json',
    },
  })

  // Request interceptor
  instance.interceptors.request.use(
    (config) => {
      // Add any auth headers here if needed
      return config
    },
    (error) => {
      return Promise.reject(error)
    }
  )

  // Response interceptor
  instance.interceptors.response.use(
    (response: AxiosResponse) => {
      return response
    },
    (error) => {
      // Handle common errors
      if (error.response?.status === 404) {
        toast.error('Resource not found')
      } else if (error.response?.status === 500) {
        toast.error('Server error. Please try again later.')
      } else if (error.code === 'ECONNABORTED') {
        toast.error('Request timeout. Please try again.')
      } else if (!error.response) {
        toast.error('Network error. Please check your connection.')
      }
      
      return Promise.reject(error)
    }
  )

  return instance
}

const api = createApiInstance()

// API service class
export class ApiService {
  // Health check
  static async healthCheck(): Promise<ApiResponse> {
    try {
      const response = await api.get('/health')
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  // Programme setup endpoints
  static async setupProgramme(data: ProgrammeData): Promise<ApiResponse<WorkflowResult>> {
    try {
      const response = await api.post('/api/setup', data)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  static async validateProgramme(data: ProgrammeData): Promise<ApiResponse<ValidationResult>> {
    try {
      const response = await api.post('/api/validate', data)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  // Dashboard endpoints
  static async getDashboardData(clientName?: string): Promise<ApiResponse<DashboardData>> {
    try {
      const params = clientName ? { client_name: clientName } : {}
      const response = await api.get('/api/dashboard', { params })
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  // Knowledge base endpoints
  static async searchKnowledgeBase(
    query: string,
    industry?: string
  ): Promise<ApiResponse<SearchResult>> {
    try {
      const params: any = { query }
      if (industry) params.industry = industry
      
      const response = await api.get('/api/knowledge/search', { params })
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  // Workflow management
  static async getWorkflowStatus(workflowId: string): Promise<ApiResponse> {
    try {
      const response = await api.get(`/api/workflow/${workflowId}/status`)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  static async executeAgent(
    agentName: string,
    params: Record<string, any>
  ): Promise<ApiResponse> {
    try {
      const response = await api.post(`/api/agent/${agentName}`, params)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  // Client profile endpoints
  static async getClientProfiles(): Promise<ApiResponse> {
    try {
      const response = await api.get('/api/clients')
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  static async getClientProfile(clientName: string): Promise<ApiResponse> {
    try {
      const response = await api.get(`/api/clients/${encodeURIComponent(clientName)}`)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  static async createClientProfile(profileData: any): Promise<ApiResponse> {
    try {
      const response = await api.post('/api/clients', profileData)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  static async updateClientProfile(id: string, profileData: any): Promise<ApiResponse> {
    try {
      const response = await api.put(`/api/clients/${id}`, profileData)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  static async deleteClientProfile(id: string): Promise<ApiResponse> {
    try {
      const response = await api.delete(`/api/clients/${id}`)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  // Insights endpoints
  static async getInsights(clientName?: string): Promise<ApiResponse> {
    try {
      const params = clientName ? { client_name: clientName } : {}
      const response = await api.get('/api/insights', { params })
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  static async getInsightsSummary(): Promise<ApiResponse> {
    try {
      const response = await api.get('/api/insights/summary')
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  static async generateInsights(): Promise<ApiResponse> {
    try {
      const response = await api.post('/api/insights/generate')
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  static async updateInsightStatus(id: string, status: string): Promise<ApiResponse> {
    try {
      const response = await api.patch(`/api/insights/${id}`, { status })
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  // Meetings endpoints
  static async getMeetings(clientName?: string): Promise<ApiResponse> {
    try {
      const params = clientName ? { client_name: clientName } : {}
      const response = await api.get('/api/meetings', { params })
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  static async getMeetingsSummary(): Promise<ApiResponse> {
    try {
      const response = await api.get('/api/meetings/summary')
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  static async uploadMeeting(meetingData: any): Promise<ApiResponse> {
    try {
      const response = await api.post('/api/meetings/upload', meetingData)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  static async exportInsights(format: string): Promise<ApiResponse> {
    try {
      const response = await api.get(`/api/insights/export?format=${format}`)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  static async analyzeMeeting(
    meetingId: string,
    transcript: string
  ): Promise<ApiResponse> {
    try {
      const response = await api.post('/api/meetings/analyze', {
        meeting_id: meetingId,
        transcript,
      })
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  // File upload endpoints
  static async uploadFile(file: File, type: 'transcript' | 'document'): Promise<ApiResponse> {
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('type', type)

      const response = await api.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  // Export data endpoints
  static async exportData(format: 'json' | 'csv', type: 'dashboard' | 'insights'): Promise<Blob> {
    try {
      const response = await api.get(`/api/export/${type}`, {
        params: { format },
        responseType: 'blob',
      })
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  // Error handling
  private static handleError(error: any): Error {
    if (error.response?.data?.message) {
      return new Error(error.response.data.message)
    } else if (error.message) {
      return new Error(error.message)
    } else {
      return new Error('An unexpected error occurred')
    }
  }
}

// Export the axios instance for direct use if needed
export { api }
export default ApiService