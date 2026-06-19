import axios from 'axios'

const API_KEY_STORAGE = 'chrony_api_key'

export function getApiKey() {
  return localStorage.getItem(API_KEY_STORAGE) || ''
}

export function setApiKey(key) {
  localStorage.setItem(API_KEY_STORAGE, key)
}

const http = axios.create({ baseURL: '' })

http.interceptors.request.use(cfg => {
  const key = getApiKey()
  if (key) cfg.headers['X-API-Key'] = key
  return cfg
})

export const api = {
  status:     () => http.get('/api/status').then(r => r.data),
  sources:    () => http.get('/api/sources').then(r => r.data),
  getConfig:  () => http.get('/api/config').then(r => r.data),
  putConfig:  (body) => http.put('/api/config', body).then(r => r.data),
  health:     () => http.get('/health').then(r => r.data),
}
