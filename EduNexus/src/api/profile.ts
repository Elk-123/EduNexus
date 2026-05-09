import apiClient from './client'
import type { OnboardingSubmission, ProfileResponse } from '@/types/profile'

export async function submitOnboarding(payload: OnboardingSubmission): Promise<ProfileResponse> {
  const { data } = await apiClient.post<ProfileResponse>('/profile/onboarding', payload)
  return data
}

export async function getMyProfile(): Promise<ProfileResponse> {
  const { data } = await apiClient.get<ProfileResponse>('/profile/me')
  return data
}
