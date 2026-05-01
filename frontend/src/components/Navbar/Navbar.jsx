import { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { clearCachedSearch } from '../../utils/jobsSearchCache'
import './Navbar.css'

const links = [
  { to: '/', label: 'Home' },
  { to: '/cv', label: 'Upload CV' },
  { to: '/preferences', label: 'Preferences' },
  { to: '/jobs', label: 'Find Jobs' },
  { to: '/tailored-cvs', label: 'Tailored CVs' },
  { to: '/cover-letters', label: 'Cover Letters' },
  { to: '/applications', label: 'My Applications' },
];

export default function Navbar() {
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);

  function handleLogout() {
    localStorage.removeItem('access_token')
    clearCachedSearch()
    navigate('/login')
  }

  function toggleMenu() {
    setIsOpen(!isOpen);
  }

  function closeMenu() {
    setIsOpen(false);
  }

  return (
    <nav className="navbar">
      <div className="navbar-header">
        <span className="navbar-brand">FindMyJob</span>
        <button className="hamburger-btn" onClick={toggleMenu} aria-label="Toggle navigation">
          ☰
        </button>
      </div>

      <div className={`navbar-menu ${isOpen ? 'open' : ''}`}>
        <ul className="navbar-links">
          {links.map((l) => (
            <li key={l.to}>
              <NavLink
                to={l.to}
                end={l.to === '/'}
                className={({ isActive }) => (isActive ? 'active' : '')}
                onClick={closeMenu}
              >
                {l.label}
              </NavLink>
            </li>
          ))}
        </ul>

        <button className="logout-btn" onClick={handleLogout}>
          Log out
        </button>
      </div>
    </nav>
  );
}
