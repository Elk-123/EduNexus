/** 通用 API 错误响应格式，对应后端 HTTPException */
export interface ApiError {
  detail: string
}

/** 分页响应格式 */
export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  page_size: number
}
