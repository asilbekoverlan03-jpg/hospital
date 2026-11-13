import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { updateProfile } from '../api/auth'
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

export default function ProfilePage() {
  const { user, updateUser } = useAuth()
  const [form, setForm] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    email: user?.email || '',
    birth_date: user?.birth_date || '',
    phone_number: user?.phone_number || '',
    address: user?.address || '',
    blood_group: user?.blood_group || '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))
    setSuccess(false)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setSuccess(false)
    try {
      const res = await updateProfile(form)
      updateUser(res.data)
      setSuccess(true)
    } catch (err) {
      setError(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <h1 className="page-title">Мой профиль</h1>
      <div className="profile-card">
        <div className="profile-avatar">
          <span>👤</span>
          <div>
            <strong>{user?.username}</strong>
            <p>Зарегистрирован: {user?.date_register
              ? new Date(user.date_register).toLocaleDateString('ru-RU')
              : '—'}</p>
          </div>
        </div>

        {success && <div className="alert alert-success">Профиль успешно обновлён!</div>}
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
            <label htmlFor="email">Email</label>
            <input id="email" name="email" type="email" className="form-control"
              value={form.email} onChange={handleChange} />
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
              value={form.phone_number} onChange={handleChange} />
          </div>

          <div className="form-group">
            <label htmlFor="address">Адрес</label>
            <textarea id="address" name="address" className="form-control" rows={2}
              value={form.address} onChange={handleChange} />
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Сохранение...' : 'Сохранить изменения'}
          </button>
        </form>
      </div>
    </div>
  )
}
