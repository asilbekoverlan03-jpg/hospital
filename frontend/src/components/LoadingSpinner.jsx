export default function LoadingSpinner({ text = 'Загрузка...' }) {
  return (
    <div className="loading-container">
      <div className="spinner" />
      <p>{text}</p>
    </div>
  )
}
