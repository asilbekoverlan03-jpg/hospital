import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import PrivateRoute from './components/PrivateRoute'

import HomePage from './pages/HomePage'
import DoctorsPage from './pages/DoctorsPage'
import DoctorDetailPage from './pages/DoctorDetailPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ProfilePage from './pages/ProfilePage'
import NewAppointmentPage from './pages/NewAppointmentPage'
import MyAppointmentsPage from './pages/MyAppointmentsPage'

export default function App() {
  return (
    <>
      <Navbar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/doctors" element={<DoctorsPage />} />
          <Route path="/doctors/:id" element={<DoctorDetailPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Защищённые маршруты */}
          <Route path="/profile" element={
            <PrivateRoute><ProfilePage /></PrivateRoute>
          } />
          <Route path="/appointments/new" element={
            <PrivateRoute><NewAppointmentPage /></PrivateRoute>
          } />
          <Route path="/my-appointments" element={
            <PrivateRoute><MyAppointmentsPage /></PrivateRoute>
          } />

          {/* 404 */}
          <Route path="*" element={
            <div className="container" style={{ textAlign: 'center', padding: '4rem 0' }}>
              <h1>404</h1>
              <p>Страница не найдена.</p>
              <a href="/" className="btn btn-primary">На главную</a>
            </div>
          } />
        </Routes>
      </main>
      <footer className="footer">
        <div className="container">
          <p>© 2024 МедКлиника. Все права защищены.</p>
        </div>
      </footer>
    </>
  )
}
