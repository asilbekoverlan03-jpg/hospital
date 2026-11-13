import client from './client'

export const register = (data) => client.post('/auth/register/', data)
export const login = (data) => client.post('/auth/login/', data)
export const logout = (refresh) => client.post('/auth/logout/', { refresh })
export const getProfile = () => client.get('/profile/')
export const updateProfile = (data) => client.patch('/profile/', data)
