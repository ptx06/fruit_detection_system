import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1/auth',
  timeout: 10000,
})

export interface LoginParams {
  username: string
  password: string
}

export interface RegisterParams {
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  username: string
  role: string
}

export interface UserInfo {
  id: number
  username: string
  role: string
  created_at: string
}

export async function login(params: LoginParams): Promise<TokenResponse> {
  const { data } = await api.post<TokenResponse>('/login', params)
  return data
}

export async function register(params: RegisterParams): Promise<TokenResponse> {
  const { data } = await api.post<TokenResponse>('/register', params)
  return data
}

export async function getCurrentUser(token: string): Promise<UserInfo> {
  const { data } = await api.get<UserInfo>('/me', {
    headers: { Authorization: `Bearer ${token}` }
  })
  return data
}