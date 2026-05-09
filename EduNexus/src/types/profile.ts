/** 前端提交的破冰对话原始数据：4 维度多选 + 备注 */
export interface OnboardingSubmission {
  responses: {
    knowledge_base: string[]
    cognitive_style: string[]
    learning_goals: string[]
    time_distribution: string[]
    notes: string[]
  }
}

/** AI 分析后返回的 6 维度结构化画像 */
export interface ProfileDimensions {
  knowledge_base_score: number
  cognitive_style: string
  error_preference: string
  learning_goals: string
  focus_duration: number
  stress_resistance: number
}

/** GET /profile/me 或 POST /profile/onboarding 的响应 */
export interface ProfileResponse {
  student_id: string
  profile_data: ProfileDimensions
  version: number
}
