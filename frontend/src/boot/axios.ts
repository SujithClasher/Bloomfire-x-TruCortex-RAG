import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8010',
  timeout: 180000, // 3 minutes for local LLM CPU inference
})

export default api
export { api }
