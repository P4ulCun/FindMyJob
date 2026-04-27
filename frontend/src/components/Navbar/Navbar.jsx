import { NavLink, useNavigate } from 'react-router-dom';
import './Navbar.css';

const links = [
  { to: '/', label: 'Home' },
  { to: '/cv', label: 'Upload CV' },
  { to: '/preferences', label: 'Preferences' },
  { to: '/jobs', label: 'Find Jobs' },
  { to: '/tailored-cvs', label: 'Tailored CVs' },
];

export default function Navbar() {
  const navigate = useNavigate();

  function handleLogout() {
    localStorage.removeItem('access_token');
    navigate('/login');
  }

  return (
    <nav className="navbar">
      <span className="navbar-brand">FindMyJob</span>

      <ul className="navbar-links">
        {links.map((l) => (
          <li key={l.to}>
            <NavLink
              to={l.to}
              end={l.to === '/'}
              className={({ isActive }) => (isActive ? 'active' : '')}
            >
              {l.label}
            </NavLink>
          </li>
        ))}
      </ul>

      <button className="logout-btn" onClick={handleLogout}>
        Log out
      </button>
    </nav>
  );
}
