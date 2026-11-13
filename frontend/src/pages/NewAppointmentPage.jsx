import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { getDoctors, getSchedules } from '../api/doctors'
import { createAppointment } from '../api/appointments'
import ErrorMessage from '../components/ErrorMessage'
import LoadingSpinner from '../components/LoadingSpinner'

const DAY_NAMES = {
  1: 'Пн', 2: 'Вт', 3: 'Ср', 4: 'Чт', 5: 'Пт', 6: 'Сб', 7: 'Вс',
}

// Генерируем слоты по 30 минут в рамках расписания
function generateSlots(schedules, selectedDate) {
  if (!selectedDate || !schedules.length) return []

  const date = new Date(selectedDate)
  // isoWeekday: 1=пн ... 7=вс
  const dayOfWeek = date.getDay() === 0 ? 7 : date.getDay()

  const schedule = schedules.find((s) => s.day_of_week === dayOfWeek)
  if (!schedule) return []

  const slots = []
  const [startH, startM] = schedule.start_time.split(':').map(Number)
  const [endH, endM] = schedule.end_time.split(':').map(Number)

  let h = startH
  let m = startM
  while (h < endH || (h === endH && m < endM)) {
    slots.push(`${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`)
    m += 30
    if (m >= 60) { h++; m -= 60 }
  }
  return slots
}

// Минимальная дата — завтра
function getMinDate() {
  const d = new Date()
  d.setDate(d.getDate() + 1)
  return d.toISOString().split('T')[0]
}

export default function NewAppointmentPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const preselectedDoctor = searchParams.get('doctor') || ''

  const [doctors, setDoctors] = useState([])
  const [schedules, setSchedules] = useState([])
  const [doctorsLoading, setDoctorsLoading] = useState(true)

  const [form, setForm] = useState({
    doctor: preselectedDoctor,
    date: '',
    time: '',
    complaint: '',
  })
  const [slots, setSlots] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    getDoctors({ page: 1 })
      .then((res) => setDoctors(res.data.results))
      .catch(() => {})
      .finally(() => setDoctorsLoading(false))
  }, [])

  useEffect(() => {
    if (form.doctor) {
      getSchedules(form.doctor)
        .then((res) => setSchedules(res.data))
        .catch(() => setSchedules([]))
    } else {
      setSchedules([])
    }
    setForm((prev) => ({ ...prev, date: '', time: '' }))
  }, [form.doctor])

  useEffect(() => {
    setSlots(generateSlots(schedules, form.date))
    setForm((prev) => ({ ...prev, time: '' }))
  }, [form.date, schedules])

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.doctor || !form.date || !form.time || !form.complaint) {
      setError('Пожалуйста, заполните все поля.')
      return
    }
    setLoading(true)
    setError(null)

    const date_time = `${form.date}T${form.time}:00`

    try {
      await createAppointment({
        doctor: parseInt(form.doctor),
        date_time,
        complaint: form.complaint,
      })
      navigate('/my-appointments')
    } catch (err) {
      setError(err)
    } finally {
      setLoading(false)
    }
  }

  // Рабочие дни выбранного врача
  const workDays = schedules.map((s) => s.day_of_week)

  // Проверяем, работает ли врач в выбранную дату
  const selectedDateWorkday = form.date
    ? (() => {
        const d = new Date(form.date)
        return d.getDay() === 0 ? 7 : d.getDay()
      })()
    : null

  const dateError = form.date && selectedDateWorkday && !workDays.includes(selectedDateWorkday)

  return (
    <div className="container">
      <h1 className="page-title">Запись на приём</h1>
      <div className="form-card">
        {doctorsLoading ? (
          <LoadingSpinner />
        ) : (
          <form onSubmit={handleSubmit} noValidate>
            <ErrorMessage error={error} />

            <div className="form-group">
              <label htmlFor="doctor">Врач *</label>
              <select
                id="doctor"
                name="doctor"
                className="form-control"
                value={form.doctor}
                onChange={handleChange}
                required
              >
                <option value="">— Выберите врача —</option>
                {doctors.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.last_name} {d.first_name} {d.patronymic} — {d.specialization_name}
                  </option>
                ))}
              </select>
            </div>

            {schedules.length > 0 && (
              <div className="alert alert-info" style={{ marginBottom: '1rem' }}>
                Врач принимает: {schedules.map((s) => DAY_NAMES[s.day_of_week]).join(', ')},
                с {schedules[0]?.start_time} до {schedules[0]?.end_time}
              </div>
            )}

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="date">Дата *</label>
                <input
                  id="date"
                  name="date"
                  type="date"
                  className={`form-control ${dateError ? 'input-error' : ''}`}
                  value={form.date}
                  min={getMinDate()}
                  onChange={handleChange}
                  required
                  disabled={!form.doctor}
                />
                {dateError && (
                  <span className="field-error">
                    Врач не принимает в этот день. Рабочие дни:{' '}
                    {workDays.map((d) => DAY_NAMES[d]).join(', ')}
                  </span>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="time">Время *</label>
                {slots.length > 0 ? (
                  <select
                    id="time"
                    name="time"
                    className="form-control"
                    value={form.time}
                    onChange={handleChange}
                    required
                    disabled={!form.date || dateError}
                  >
                    <option value="">— Выберите время —</option>
                    {slots.map((slot) => (
                      <option key={slot} value={slot}>{slot}</option>
                    ))}
                  </select>
                ) : (
                  <input
                    id="time"
                    name="time"
                    type="time"
                    className="form-control"
                    value={form.time}
                    onChange={handleChange}
                    required
                    disabled={!form.date || dateError}
                  />
                )}
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="complaint">Жалоба *</label>
              <textarea
                id="complaint"
                name="complaint"
                className="form-control"
                rows={4}
                value={form.complaint}
                onChange={handleChange}
                required
                placeholder="Опишите ваши жалобы и симптомы..."
              />
            </div>

            <div className="form-actions">
              <button
                type="button"
                className="btn btn-outline"
                onClick={() => navigate(-1)}
              >
                Отмена
              </button>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading || dateError}
              >
                {loading ? 'Запись...' : 'Записаться на приём'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}
