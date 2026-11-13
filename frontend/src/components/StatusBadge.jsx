const STATUS_LABELS = {
  pending: 'Ожидает',
  confirmed: 'Подтверждён',
  cancelled: 'Отменён',
  completed: 'Завершён',
}

export default function StatusBadge({ status }) {
  return (
    <span className={`badge badge-${status}`}>
      {STATUS_LABELS[status] || status}
    </span>
  )
}
