import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { register } from '../api/auth'
import { useAuth } from '../context/AuthContext'
import ErrorMessage from '../components/ErrorMessage'

const BLOOD_GROUPS = [
  { value: 'A+', label: 'A (I) Rh+' },
  { value: 'A-', label: 'A (I) Rh-' },
  { value: 'B+', label: 'B (II) Rh+' },
  { value: 'B-', label: 'B (II) Rh-' },
  { value: 'AB+', label: 'AB (IV) Rh+' },
  { value: 'AB-', label: 'AB (IV) Rh-' },
  { value: 'O+', label: 'O (I) Rh+' },
  { value: 'O-', label: 'O (I) Rh-' },
]

export default function RegisterPage() {
  const navigate = useNavigate()
  const { login } = useAuth()

  const [form, setForm] = useState({
    username: '', password: '', password2: '', email: '',
    first_name: '', last_name: '',
    birth_date: '', phone_number: '', address: '', blood_group: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (form.password !== form.password2) {
      setError('Пароли не совпадают.')
      return
    }
    setLoading(true)
    setError(null)
    try {
      await register(form)
      // Автоматический вход после регистрации
      await login(form.username, form.password)
      navigate('/', { replace: true })
    } catch (err) {
      setError(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card auth-card-wide">
        <h1>Регистрация</h1>
        <ErrorMessage error={error} />
        <form onSubmit={handleSubmit} noValidate>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="last_name">Фамилия</label>
              <input id="last_name" name="last_name" type="text" className="form-control"
                value={form.last_name} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label htmlFor="first_name">Имя</label>
              <input id="first_name" name="first_name" type="text" className="form-control"
                value={form.first_name} onChange={handleChange} />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="username">Логин *</label>
            <input id="username" name="username" type="text" className="form-control"
              value={form.username} onChange={handleChange} required />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email *</label>
            <input id="email" name="email" type="email" className="form-control"
              value={form.email} onChange={handleChange} required />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="password">Пароль *</label>
              <input id="password" name="password" type="password" className="form-control"
                value={form.password} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label htmlFor="password2">Повторите пароль *</label>
              <input id="password2" name="password2" type="password" className="form-control"
                value={form.password2} onChange={handleChange} required />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="birth_date">Дата рождения</label>
              <input id="birth_date" name="birth_date" type="date" className="form-control"
                value={form.birth_date} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label htmlFor="blood_group">Группа крови</label>
              <select id="blood_group" name="blood_group" className="form-control"
                value={form.blood_group} onChange={handleChange}>
                <option value="">Не указана</option>
                {BLOOD_GROUPS.map((bg) => (
                  <option key={bg.value} value={bg.value}>{bg.label}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="phone_number">Телефон</label>
            <input id="phone_number" name="phone_number" type="tel" className="form-control"
              value={form.phone_number} onChange={handleChange} placeholder="+7 (900) 000-00-00" />
          </div>

          <div className="form-group">
            <label htmlFor="address">Адрес</label>
            <textarea id="address" name="address" className="form-control" rows={2}
              value={form.address} onChange={handleChange} />
          </div>

          <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
            {loading ? 'Регистрация...' : 'Зарегистрироваться'}
          </button>
        </form>
        <p className="auth-footer">
          Уже есть аккаунт? <Link to="/login">Войти</Link>
        </p>
      </div>
    </div>
  )
}
