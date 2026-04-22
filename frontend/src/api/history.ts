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

export async function getHistoryList(skip = 0, limit = 20): Promise<HistoryRecord[]> {
  const { data } = await client.get('/history', { params: { skip, limit } })
  return data
}

export async function getHistoryDetail(id: number): Promise<HistoryDetail> {
  const { data } = await client.get(`/history/${id}`)
  return data
}