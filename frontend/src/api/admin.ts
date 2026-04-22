import client from './client'

export interface UserItem {
  id: number
  username: string
  role: string
  created_at: string
}

export async function getUsers(): Promise<UserItem[]> {
  const { data } = await client.get('/admin/users')
  return data
}

export async function updateUserRole(userId: number, role: string): Promise<void> {
  await client.put(`/admin/users/${userId}/role`, { role })
}

export async function deleteUser(userId: number): Promise<void> {
  await client.delete(`/admin/users/${userId}`)
}