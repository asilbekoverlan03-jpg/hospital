import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getDoctor, createReview } from '../api/doctors'
import { getMediaUrl } from '../api/mediaUrl'
import { useAuth } from '../context/AuthContext'
import StarRating from '../components/StarRating'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

const DAY_NAMES = {
  1: 'Понедельник', 2: 'Вторник', 3: 'Среда',
  4: 'Четверг', 5: 'Пятница', 6: 'Суббота', 7: 'Воскресенье',
}

export default function DoctorDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()

  const [doctor, setDoctor] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Форма отзыва
  const [reviewStars, setReviewStars] = useState(5)
  const [reviewComment, setReviewComment] = useState('')
  const [reviewLoading, setReviewLoading] = useState(false)
  const [reviewError, setReviewError] = useState(null)
  const [reviewSuccess, setReviewSuccess] = useState(false)

  useEffect(() => {
    setLoading(true)
    getDoctor(id)
      .then((res) => setDoctor(res.data))
      .catch(setError)
      .finally(() => setLoading(false))
  }, [id])

  const handleReview = async (e) => {
    e.preventDefault()
    setReviewLoading(true)
    setReviewError(null)
    try {
      const res = await createReview({ doctor: parseInt(id), stars: reviewStars, comment: reviewComment })
      setDoctor((prev) => ({
        ...prev,
        reviews: [res.data, ...prev.reviews],
      }))
      setReviewSuccess(true)
      setReviewComment('')
    } catch (err) {
      setReviewError(err)
    } finally {
      setReviewLoading(false)
    }
  }

  if (loading) return <LoadingSpinner />
  if (error) return <div className="container"><ErrorMessage error={error} /></div>
  if (!doctor) return null

  const photoUrl = getMediaUrl(doctor.photo)
  const userReview = doctor.reviews?.find((r) => r.patient_name === (user?.first_name || user?.username))
  const canReview = user && !reviewSuccess && !userReview

  return (
    <div className="container">
      {/* Шапка врача */}
      <div className="doctor-detail-header">
        <div className="doctor-detail-photo">
          {photoUrl ? (
            <img src={photoUrl} alt={`${doctor.last_name} ${doctor.first_name}`} />
          ) : (
            <div className="doctor-detail-photo-placeholder">👨‍⚕️</div>
          )}
        </div>
        <div className="doctor-detail-info">
          <h1>{doctor.last_name} {doctor.first_name} {doctor.patronymic}</h1>
          <p className="doctor-detail-spec">{doctor.specialization_name}</p>
          <div className="doctor-detail-meta">
            <div className="meta-item">
              <span className="meta-label">Опыт работы</span>
              <span className="meta-value">{doctor.experience_years} лет</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Стоимость</span>
              <span className="meta-value">{Number(doctor.price).toLocaleString('ru-RU')} ₽</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Рейтинг</span>
              <span className="meta-value">
                <StarRating value={doctor.avg_rating} />
              </span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Приёмов</span>
              <span className="meta-value">{doctor.appointment_count}</span>
            </div>
          </div>
          <button
            className="btn btn-primary btn-lg"
            onClick={() => navigate(`/appointments/new?doctor=${doctor.id}`)}
          >
            Записаться на приём
          </button>
        </div>
      </div>

      {/* Расписание */}
      {doctor.schedules?.length > 0 && (
        <section className="doctor-section">
          <h2>Расписание приёмов</h2>
          <div className="schedule-grid">
            {doctor.schedules.map((s) => (
              <div key={s.id} className="schedule-item">
                <span className="schedule-day">{DAY_NAMES[s.day_of_week]}</span>
                <span className="schedule-time">{s.start_time} – {s.end_time}</span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Отзывы */}
      <section className="doctor-section">
        <h2>Отзывы пациентов ({doctor.reviews?.length || 0})</h2>

        {doctor.reviews?.length === 0 && (
          <p className="empty-state">Отзывов пока нет.</p>
        )}

        <div className="reviews-list">
          {doctor.reviews?.map((review) => (
            <div key={review.id} className="review-card">
              <div className="review-header">
                <span className="review-author">👤 {review.patient_name}</span>
                <StarRating value={review.stars} />
                <span className="review-date">
                  {new Date(review.created_date).toLocaleDateString('ru-RU')}
                </span>
              </div>
              {review.comment && <p className="review-comment">{review.comment}</p>}
            </div>
          ))}
        </div>

        {/* Форма отзыва */}
        {!user && (
          <div className="alert alert-info">
            <a href="/login">Войдите</a>, чтобы оставить отзыв.
          </div>
        )}

        {reviewSuccess && (
          <div className="alert alert-success">Ваш отзыв успешно добавлен!</div>
        )}

        {userReview && !reviewSuccess && (
          <div className="alert alert-info">Вы уже оставили отзыв этому врачу.</div>
        )}

        {canReview && (
          <form className="review-form" onSubmit={handleReview}>
            <h3>Оставить отзыв</h3>
            <ErrorMessage error={reviewError} />
            <div className="form-group">
              <label>Оценка</label>
              <StarRating value={reviewStars} onChange={setReviewStars} />
            </div>
            <div className="form-group">
              <label htmlFor="review-comment">Комментарий</label>
              <textarea
                id="review-comment"
                className="form-control"
                rows={4}
                value={reviewComment}
                onChange={(e) => setReviewComment(e.target.value)}
                placeholder="Ваш опыт посещения..."
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={reviewLoading}>
              {reviewLoading ? 'Отправка...' : 'Отправить отзыв'}
            </button>
          </form>
        )}
      </section>
    </div>
  )
}
