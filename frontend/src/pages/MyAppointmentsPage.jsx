import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getAppointments, cancelAppointment } from '../api/appointments'
import { getMediaUrl } from '../api/mediaUrl'
import StatusBadge from '../components/StatusBadge'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

export default function MyAppointmentsPage() {
  const [appointments, setAppointments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [cancellingId, setCancellingId] = useState(null)

  const load = () => {
    setLoading(true)
    setError(null)
    getAppointments()
      .then((res) => setAppointments(res.data.results || res.data))
      .catch(setError)
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const handleCancel = async (id) => {
    if (!window.confirm('Отменить запись?')) return
    setCancellingId(id)
    try {
      const res = await cancelAppointment(id)
      setAppointments((prev) =>
        prev.map((a) => (a.id === id ? res.data : a))
      )
    } catch (err) {
      alert(
        err.response?.data?.error ||
        err.response?.data?.detail ||
        'Ошибка при отмене записи.'
      )
    } finally {
      setCancellingId(null)
    }
  }

  if (loading) return <LoadingSpinner />

  return (
    <div className="container">
      <div className="page-header">
        <h1 className="page-title">Мои записи</h1>
        <Link to="/appointments/new" className="btn btn-primary">
          + Новая запись
        </Link>
      </div>

      {error && <ErrorMessage error={error} />}

      {!loading && !error && appointments.length === 0 && (
        <div className="empty-state">
          <p>У вас пока нет записей на приём.</p>
          <Link to="/doctors" className="btn btn-primary">Найти врача</Link>
        </div>
      )}

      <div className="appointments-list">
        {appointments.map((apt) => {
          const doctor = apt.doctor_info
          const photoUrl = getMediaUrl(doctor?.photo)
          const canCancel = ['pending', 'confirmed'].includes(apt.status)

          return (
            <div key={apt.id} className="appointment-card">
              <div className="appointment-card-header">
                <div className="appointment-doctor">
                  {photoUrl ? (
                    <img src={photoUrl} alt="" className="appointment-doctor-photo" />
                  ) : (
                    <div className="appointment-doctor-photo-placeholder">👨‍⚕️</div>
                  )}
                  <div>
                    <Link to={`/doctors/${doctor?.id}`} className="appointment-doctor-name">
                      {doctor?.last_name} {doctor?.first_name} {doctor?.patronymic}
                    </Link>
                    <p className="appointment-doctor-spec">{doctor?.specialization_name}</p>
                  </div>
                </div>
                <StatusBadge status={apt.status} />
              </div>

              <div className="appointment-card-body">
                <div className="appointment-info-row">
                  <span className="appointment-label">📅 Дата и время:</span>
                  <span>
                    {new Date(apt.date_time).toLocaleString('ru-RU', {
                      day: '2-digit', month: '2-digit', year: 'numeric',
                      hour: '2-digit', minute: '2-digit',
                    })}
                  </span>
                </div>
                <div className="appointment-info-row">
                  <span className="appointment-label">💬 Жалоба:</span>
                  <span>{apt.complaint}</span>
                </div>

                {apt.medical_record && (
                  <div className="medical-record">
                    <h4>📋 Медицинская карта</h4>
                    <div className="appointment-info-row">
                      <span className="appointment-label">Диагноз:</span>
                      <span>{apt.medical_record.diagnosis}</span>
                    </div>
                    <div className="appointment-info-row">
                      <span className="appointment-label">Назначения:</span>
                      <span>{apt.medical_record.prescription}</span>
                    </div>
                  </div>
                )}
              </div>

              {canCancel && (
                <div className="appointment-card-footer">
                  <button
                    className="btn btn-danger btn-sm"
                    onClick={() => handleCancel(apt.id)}
                    disabled={cancellingId === apt.id}
                  >
                    {cancellingId === apt.id ? 'Отмена...' : 'Отменить запись'}
                  </button>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
