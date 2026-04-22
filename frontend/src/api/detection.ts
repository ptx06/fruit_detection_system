import client from './client'

export interface DetectionResult {
  bbox: number[]
  fruit_type: string
  fruit_conf: number
  maturity: string
  maturity_id: number
  maturity_conf: number
}

export interface DetectResponse {
  code: number
  message: string
  data: {
    image_base64: string
    detections: DetectionResult[]
    count: number
  }
}

export async function detectFruitMaturity(file: File): Promise<DetectResponse> {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await client.post<DetectResponse>('/detect', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return data
}