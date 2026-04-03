import axios from "axios"

const API_BASE_URL = "http://localhost:8000"

export const api = {
  uploadZip: async (file: File) => {
    const formData = new FormData()
    formData.append("file", file)
    const response = await axios.post(`${API_BASE_URL}/api/upload`, formData)
    return response.data
  },
  
  processUrl: async (url: string) => {
    const response = await axios.post(`${API_BASE_URL}/api/process-url`, null, {
      params: { url }
    })
    return response.data
  },
  
  getStatus: async (jobId: string) => {
    const response = await axios.get(`${API_BASE_URL}/api/status/${jobId}`)
    return response.data
  },
  
  getDownloadUrl: (jobId: string) => {
    return `${API_BASE_URL}/api/download/${jobId}`
  }
}
