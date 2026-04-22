import client from './client'

export interface ModelInfo {
  detection: {
    name: string
    version: string
    accuracy: string
    last_updated: string
    description: string
  }
  classification: Record<string, {
    name: string
    version: string
    accuracy: string
    last_updated: string
  }>
}

export async function getModelInfo(): Promise<ModelInfo> {
  const { data } = await client.get('/system/model-info')
  return data
}