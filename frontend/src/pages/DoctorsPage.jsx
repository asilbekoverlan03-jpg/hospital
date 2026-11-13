import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { getDoctors, getSpecializations } from '../api/doctors'
import DoctorCard from '../components/DoctorCard'
import Pagination from '../components/Pagination'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

export default function DoctorsPage() {
  const [searchParams, setSearchParams] = useSearchParams()

  const [doctors, setDoctors] = useState([])
  const [count, setCount] = useState(0)
  const [specializations, setSpecializations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const page = parseInt(searchParams.get('page') || '1', 10)
  const search = searchParams.get('search') || ''
  const specialization = searchParams.get('specialization') || ''
  const ordering = searchParams.get('ordering') || ''

  useEffect(() => {
    getSpecializations()
      .then((res) => setSpecializations(res.data))
      .catch(() => {})
  }, [])

  useEffect(() => {
    setLoading(true)
    setError(null)
    const params = { page }
    if (search) params.search = search
    if (specialization) params.specialization = specialization
    if (ordering) params.ordering = ordering

    getDoctors(params)
      .then((res) => {
        setDoctors(res.data.results)
        setCount(res.data.count)
      })
      .catch(setError)
      .finally(() => setLoading(false))
  }, [page, search, specialization, ordering])

  const setParam = (key, value) => {
    const next = new URLSearchParams(searchParams)
    if (value) {
      next.set(key, value)
    } else {
      next.delete(key)
    }
    next.delete('page')
    setSearchParams(next)
  }

  return (
    <div className="container">
      <h1 className="page-title">Наши врачи</h1>

      {/* Фильтры */}
      <div className="filters-bar">
        <input
          type="text"
          className="form-control"
          placeholder="Поиск по имени или фамилии..."
          value={search}
          onChange={(e) => setParam('search', e.target.value)}
        />
        <select
          className="form-control"
          value={specialization}
          onChange={(e) => setParam('specialization', e.target.value)}
        >
          <option value="">Все специализации</option>
          {specializations.map((s) => (
            <option key={s.id} value={s.id}>{s.name}</option>
          ))}
        </select>
        <select
          className="form-control"
          value={ordering}
          onChange={(e) => setParam('ordering', e.target.value)}
        >
          <option value="">Сортировка</option>
          <option value="price">Цена: по возрастанию</option>
          <option value="-price">Цена: по убыванию</option>
          <option value="experience_years">Опыт: по возрастанию</option>
          <option value="-experience_years">Опыт: по убыванию</option>
          <option value="last_name">По фамилии</option>
        </select>
      </div>

      {loading && <LoadingSpinner />}
      {error && <ErrorMessage error={error} />}

      {!loading && !error && (
        <>
          <p className="results-count">Найдено врачей: {count}</p>
          {doctors.length === 0 ? (
            <div className="empty-state">
              <p>Врачи не найдены. Попробуйте изменить параметры поиска.</p>
            </div>
          ) : (
            <div className="doctors-grid">
              {doctors.map((doc) => (
                <DoctorCard key={doc.id} doctor={doc} />
              ))}
            </div>
          )}
          <Pagination
            count={count}
            page={page}
            onPage={(p) => {
              const next = new URLSearchParams(searchParams)
              next.set('page', p)
              setSearchParams(next)
            }}
          />
        </>
      )}
    </div>
  )
}
