import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/')
  }

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/">🏥 МедКлиника</Link>
      </div>
      <div className="navbar-links">
        <NavLink to="/doctors">Врачи</NavLink>
        {user && <NavLink to="/my-appointments">Мои записи</NavLink>}
        {user && <NavLink to="/profile">Профиль</NavLink>}
      </div>
      <div className="navbar-auth">
        {user ? (
          <>
            <span className="navbar-username">
              👤 {user.first_name || user.username}
            </span>
            <button className="btn btn-outline" onClick={handleLogout}>
              Выйти
            </button>
          </>
        ) : (
          <>
            <Link to="/login" className="btn btn-outline">Войти</Link>
            <Link to="/register" className="btn btn-primary">Регистрация</Link>
          </>
        )}
      </div>
    </nav>
  )
}
