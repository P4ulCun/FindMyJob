import { NavLink } from 'react-router-dom';
import './Navbar.css';

const links = [
  { to: '/', label: 'Home' },
  { to: '/cv', label: 'Upload CV' },
  { to: '/preferences', label: 'Preferences' },
];

export default function Navbar() {
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
    </nav>
  );
}
