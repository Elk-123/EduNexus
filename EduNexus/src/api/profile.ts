import apiClient from './client'
import type { OnboardingSubmission, ProfileResponse, OnboardingChatRequest, OnboardingChatResponse } from '@/types/profile'

export async function submitOnboarding(payload: OnboardingSubmission): Promise<ProfileResponse> {
  const { data } = await apiClient.post<ProfileResponse>('/profile/onboarding', payload)
  return data
}

export async function onboardingChat(payload: OnboardingChatRequest): Promise<OnboardingChatResponse> {
  const { data } = await apiClient.post<OnboardingChatResponse>('/profile/onboarding/chat', payload)
  return data
}

export async function getMyProfile(): Promise<ProfileResponse> {
  const { data } = await apiClient.get<ProfileResponse>('/profile/me')
  return data
}

export async function updateMyProfile(payload: OnboardingSubmission): Promise<ProfileResponse> {
  const { data } = await apiClient.put<ProfileResponse>('/profile/me', payload)
  return data
}
