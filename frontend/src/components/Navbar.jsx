import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <header className="navbar">
      <div className="navbar-brand">
        Foresight <span>Provider Match</span>
      </div>
      <nav className="navbar-links">
        <NavLink to="/" end>
          Find a Provider
        </NavLink>
        {user && <NavLink to="/match">Get Matched</NavLink>}
        {user && <NavLink to="/appointments">My Appointments</NavLink>}
        {user?.role === "admin" && <NavLink to="/admin">Admin</NavLink>}
      </nav>
      <div className="navbar-user">
        {user ? (
          <>
            <span className="navbar-username">
              {user.full_name} <em>({user.role})</em>
            </span>
            <button type="button" className="btn btn-secondary" onClick={handleLogout}>
              Log out
            </button>
          </>
        ) : (
          <NavLink to="/login" className="btn btn-primary">
            Log in
          </NavLink>
        )}
      </div>
    </header>
  );
}
