import React, { useState } from "react";
import "../Style/Encabezado.css";
import { FaUserCircle, FaBars, FaTimes } from "react-icons/fa";
import { Link } from "react-router-dom";

const Header = () => {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="header">
      <div className="header-left">
        <div className="logo">
          <img
            className="logito"
            src="https://assets-v2.lottiefiles.com/a/97fc9faa-117f-11ee-a3b3-5fb6ab9865dc/vR6mwrGRsr.gif"
            alt="logo"
          />
        </div>
        <h1 className="logo-text">
          Confid<span className="highlight">AI</span>
        </h1>
      </div>

      {/* Botón hamburguesa */}
      <button
        className="menu-toggle"
        onClick={() => setMenuOpen(!menuOpen)}
        aria-label="Abrir menú"
      >
        {menuOpen ? <FaTimes /> : <FaBars />}
      </button>

      {/* Nav: clase "open" cuando el menú está activo */}
      <nav className={`nav ${menuOpen ? "open" : ""}`}>
        <Link to="/resultados" onClick={() => setMenuOpen(false)}>
          Mis Resultados
        </Link>
      </nav>

      <div className="header-right">
        <Link to="/perfil" className="profile-link">
          <FaUserCircle className="user-icon" />
        </Link>
        <div className="user-info">
          <span>Hola, Carlos</span>
          <h5>Mi perfil</h5>
        </div>
      </div>
    </header>
  );
};

export default Header;