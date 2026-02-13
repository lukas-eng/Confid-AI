import React from "react";
import "../Style/Encabezado.css";
import { FaUserCircle } from "react-icons/fa";
import { Link } from "react-router-dom";

const Header = () => {
  return (
    <header className="header">
      <div className="header-left">
        <div className="logo-box">
          <div className="logo-square"></div>
        </div>
        <h1 className="logo-text">
          Confid<span className="highlight">AI</span>
        </h1>
      </div>

      <nav className="nav">
        <a href="principal">Inicio</a>
      </nav>

      <div className="header-right">
        <Link to="/editarperfil" className="profile-link">
          <FaUserCircle className="user-icon" />
        </Link>

        <div className="user-info">
          <span>Hola, Carlos</span>
          <small>(Estudiante ADSO)</small>
        </div>
      </div>
    </header>
  );
};

export default Header;