import client from './client'

export interface HistoryRecord {
  id: number
  original_filename: string
  fruit_count: number
  created_at: string
}

export interface HistoryDetail extends HistoryRecord {
  result_json: any[]
  image_base64: string | null
}

export interface HistoryListResponse {
  records: HistoryRecord[]
  total: number
}

export interface HistoryFilter {
  keyword?: string
  fruit_type?: string
  maturity?: string
  start_date?: string
  end_date?: string
}

export async function getHistoryList(
  skip = 0,
  limit = 20,
  filter?: HistoryFilter
): Promise<HistoryListResponse> {
  const params = { skip, limit, ...filter }
  const { data } = await client.get('/history', { params })
  return data
}

export async function getHistoryDetail(id: number): Promise<HistoryDetail> {
  const { data } = await client.get(`/history/${id}`)
  return data
}