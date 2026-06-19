import axios from 'axios'

const TOKEN_KEY  = 'chrony_auth_token'
const API_KEY_STORAGE = 'chrony_api_key'

export function getToken()  { return localStorage.getItem(TOKEN_KEY) || '' }
export function setToken(t) { localStorage.setItem(TOKEN_KEY, t) }
export function clearToken(){ localStorage.removeItem(TOKEN_KEY) }
export function isLoggedIn(){ return !!getToken() }

export function getApiKey()  { return localStorage.getItem(API_KEY_STORAGE) || '' }
export function setApiKey(k) { localStorage.setItem(API_KEY_STORAGE, k) }

const http = axios.create({ baseURL: '' })

http.interceptors.request.use(cfg => {
  const token = getToken()
  if (token) cfg.headers['X-Auth-Token'] = token
  const key = getApiKey()
  if (key) cfg.headers['X-API-Key'] = key
  return cfg
})

export const api = {
  // Auth
  login:      (username, password) => http.post('/auth/login', { username, password }).then(r => r.data),
  logout:     ()                   => http.post('/auth/logout').then(r => r.data),
  me:         ()                   => http.get('/auth/me').then(r => r.data),

  // NTP (public)
  status:     () => http.get('/api/status').then(r => r.data),
  sources:    () => http.get('/api/sources').then(r => r.data),

  // Config (auth)
  getConfig:  ()     => http.get('/api/config').then(r => r.data),
  putConfig:  (body) => http.put('/api/config', body).then(r => r.data),
  getRawConf: ()     => http.get('/api/chrony-conf').then(r => r.data),
  putRawConf: (content) => http.put('/api/chrony-conf', { content }).then(r => r.data),

  // Service (auth)
  serviceStatus:  () => http.get('/api/service/status').then(r => r.data),
  serviceRestart: () => http.post('/api/service/restart').then(r => r.data),

  changePassword: (current_password, new_password) =>
    http.post('/auth/change-password', { current_password, new_password }).then(r => r.data),

  health: () => http.get('/health').then(r => r.data),
}
