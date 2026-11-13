import client from './client'

export const getDoctors = (params) => client.get('/doctors/', { params })
export const getDoctor = (id) => client.get(`/doctors/${id}/`)
export const getSpecializations = () => client.get('/specializations/')
export const getSchedules = (doctorId) => client.get('/schedules/', { params: { doctor: doctorId } })
export const getReviews = (doctorId) => client.get('/reviews/', { params: { doctor: doctorId } })
export const createReview = (data) => client.post('/reviews/', data)
