export interface User {
    id: string
    email: string
    username: string
    onboarding_completed: boolean
  }
  
  export interface AuthResponse {
    access_token: string
    refresh_token: string
    token_type: string
    user: User
  }