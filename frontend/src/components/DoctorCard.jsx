import { Link } from 'react-router-dom'
import StarRating from './StarRating'
import { getMediaUrl } from '../api/mediaUrl'

export default function DoctorCard({ doctor }) {
  const photoUrl = getMediaUrl(doctor.photo)

  return (
    <div className="doctor-card">
      <div className="doctor-card-photo">
        {photoUrl ? (
          <img src={photoUrl} alt={`${doctor.last_name} ${doctor.first_name}`} />
        ) : (
          <div className="doctor-card-photo-placeholder">👨‍⚕️</div>
        )}
      </div>
      <div className="doctor-card-body">
        <h3 className="doctor-card-name">
          {doctor.last_name} {doctor.first_name} {doctor.patronymic}
        </h3>
        <p className="doctor-card-spec">{doctor.specialization_name}</p>
        <div className="doctor-card-meta">
          <span>🎓 {doctor.experience_years} лет опыта</span>
          <span>💰 {Number(doctor.price).toLocaleString('ru-RU')} ₽</span>
        </div>
        <div className="doctor-card-rating">
          <StarRating value={doctor.avg_rating} />
          <span className="doctor-card-appointments">
            {doctor.appointment_count} приёмов
          </span>
        </div>
        <Link to={`/doctors/${doctor.id}`} className="btn btn-primary btn-sm">
          Подробнее
        </Link>
      </div>
    </div>
  )
}
