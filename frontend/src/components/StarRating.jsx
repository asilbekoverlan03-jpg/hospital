export default function StarRating({ value, max = 5, onChange }) {
  const stars = Array.from({ length: max }, (_, i) => i + 1)

  if (onChange) {
    return (
      <div className="star-rating interactive">
        {stars.map((s) => (
          <button
            key={s}
            type="button"
            className={`star ${s <= value ? 'filled' : ''}`}
            onClick={() => onChange(s)}
            aria-label={`${s} звезда`}
          >
            ★
          </button>
        ))}
      </div>
    )
  }

  return (
    <div className="star-rating" aria-label={`Рейтинг: ${value} из ${max}`}>
      {stars.map((s) => (
        <span key={s} className={`star ${s <= (value || 0) ? 'filled' : ''}`}>
          ★
        </span>
      ))}
      {value !== null && value !== undefined && (
        <span className="star-value">{value}</span>
      )}
    </div>
  )
}
