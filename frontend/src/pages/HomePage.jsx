import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getSpecializations } from '../api/doctors'
import { getMediaUrl } from '../api/mediaUrl'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

export default function HomePage() {
  const [specializations, setSpecializations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    getSpecializations()
      .then((res) => setSpecializations(res.data))
      .catch(setError)
      .finally(() => setLoading(false))
  }, [])

  return (
    <div>
      {/* Hero */}
      <section className="hero">
        <div className="hero-content">
          <h1>Забота о вашем здоровье — наш приоритет</h1>
          <p>
            Запишитесь на приём к лучшим специалистам нашей клиники.
            Быстро, удобно, без очередей.
          </p>
          <Link to="/doctors" className="btn btn-primary btn-lg">
            Найти врача
          </Link>
        </div>
      </section>

      {/* Специализации */}
      <section className="section">
        <div className="container">
          <h2 className="section-title">Наши специализации</h2>
          {loading && <LoadingSpinner />}
          {error && <ErrorMessage error={error} />}
          {!loading && !error && specializations.length === 0 && (
            <p className="empty-state">Специализации не найдены.</p>
          )}
          <div className="specs-grid">
            {specializations.map((spec) => (
              <Link
                key={spec.id}
                to={`/doctors?specialization=${spec.id}`}
                className="spec-card"
              >
                {spec.image ? (
                  <img
                    src={getMediaUrl(spec.image)}
                    alt={spec.name}
                    className="spec-card-image"
                  />
                ) : (
                  <div className="spec-card-icon">🏥</div>
                )}
                <h3>{spec.name}</h3>
                <p>{spec.description}</p>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Преимущества */}
      <section className="section section-gray">
        <div className="container">
          <h2 className="section-title">Почему выбирают нас</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">👨‍⚕️</div>
              <h3>Опытные специалисты</h3>
              <p>Врачи с многолетним стажем и подтверждённой квалификацией</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📅</div>
              <h3>Удобная запись</h3>
              <p>Запись онлайн в любое время, без звонков и очередей</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📋</div>
              <h3>Электронные карты</h3>
              <p>Все результаты и назначения в вашем личном кабинете</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">⭐</div>
              <h3>Реальные отзывы</h3>
              <p>Только от пациентов, прошедших приём у врача</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
