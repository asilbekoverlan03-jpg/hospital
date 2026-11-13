import client from './client'

export const getAppointments = (params) => client.get('/appointments/', { params })
export const createAppointment = (data) => client.post('/appointments/', data)
export const cancelAppointment = (id) => client.post(`/appointments/${id}/cancel/`)
export const getMedicalRecords = () => client.get('/medical-records/')
