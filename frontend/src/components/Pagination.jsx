export default function Pagination({ count, page, pageSize = 10, onPage }) {
  const total = Math.ceil(count / pageSize)
  if (total <= 1) return null

  const pages = []
  for (let i = 1; i <= total; i++) pages.push(i)

  return (
    <div className="pagination">
      <button
        className="btn btn-outline btn-sm"
        disabled={page <= 1}
        onClick={() => onPage(page - 1)}
      >
        ‹ Назад
      </button>
      {pages.map((p) => (
        <button
          key={p}
          className={`btn btn-sm ${p === page ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => onPage(p)}
        >
          {p}
        </button>
      ))}
      <button
        className="btn btn-outline btn-sm"
        disabled={page >= total}
        onClick={() => onPage(page + 1)}
      >
        Вперёд ›
      </button>
    </div>
  )
}
