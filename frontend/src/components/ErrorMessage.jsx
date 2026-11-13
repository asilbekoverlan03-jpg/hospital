export default function ErrorMessage({ error }) {
  if (!error) return null

  let message = 'Произошла ошибка.'

  if (typeof error === 'string') {
    message = error
  } else if (error.response?.data) {
    const data = error.response.data
    if (typeof data === 'string') {
      message = data
    } else if (data.detail) {
      message = data.detail
    } else if (data.error) {
      message = data.error
    } else {
      // Собираем ошибки полей
      const msgs = Object.entries(data)
        .map(([field, errs]) => {
          const errText = Array.isArray(errs) ? errs.join(', ') : String(errs)
          return `${field}: ${errText}`
        })
        .join('\n')
      message = msgs || JSON.stringify(data)
    }
  } else if (error.message) {
    message = error.message
  }

  return (
    <div className="alert alert-error" role="alert">
      {message.split('\n').map((line, i) => (
        <div key={i}>{line}</div>
      ))}
    </div>
  )
}
