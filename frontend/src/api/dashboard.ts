import client from './client'

export interface DashboardStats {
  total_detections: number
  total_fruits: number
  fruit_distribution: Record<string, number>
  maturity_distribution: Record<string, number>
  daily_trend: Array<{ date: string; count: number }>
}

export async function getDashboardStats(): Promise<DashboardStats> {
  const { data } = await client.get('/dashboard/stats')
  return data
}