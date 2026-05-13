import apiClient from './client'
import type { AuthResponse, LoginRequest, RegisterRequest } from '@/types/auth'

export async function login(payload: LoginRequest): Promise<AuthResponse> {
  const { data } = await apiClient.post<AuthResponse>('/auth/login', payload)
  return data
}

export async function register(payload: RegisterRequest): Promise<AuthResponse> {
  const { data } = await apiClient.post<AuthResponse>('/auth/register', payload)
  return data
}

export async function refreshToken(refreshToken: string): Promise<{ access_token: string }> {
  const { data } = await apiClient.post<{ access_token: string }>('/auth/refresh', { refresh_token: refreshToken })
  return data
}
