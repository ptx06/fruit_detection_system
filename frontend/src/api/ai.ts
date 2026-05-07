import client from './client'

export interface AiSummaryRequest {
  start_date?: string
  end_date?: string
  fruit_types?: string[]
  maturity_levels?: string[]
}

export interface AiSummaryResponse {
  code: number
  message: string
  data: {
    summary: string
    key_insights: string[]
    recommendations: string[]
    statistics: {
      total_detections: number
      total_fruits: number
      most_common_fruit: string
      most_common_maturity: string
    }
  }
}

export async function generateAiSummary(params: AiSummaryRequest): Promise<AiSummaryResponse> {
  const { data } = await client.post('/ai/summary', params)
  return data
}