import React, { useEffect, useRef } from "react";
import Encabezado from "../Componentes/Encabezado";
import { useNavigate } from "react-router-dom";
import "../Style/Paginaprincipal.css";

export default function PaginaPrincipal() {
  const imageRef = useRef(null);
  const containerRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (imageRef.current && containerRef.current) {
        const { clientX, clientY } = e;
        const { innerWidth, innerHeight } = window;

        const xPos = (clientX / innerWidth - 0.5) * 20;
        const yPos = (clientY / innerHeight - 0.5) * 20;

        imageRef.current.style.transform = `translate(${xPos}px, ${yPos}px)`;
      }
    };

    const container = containerRef.current;
    if (container) container.addEventListener("mousemove", handleMouseMove);
    return () => { if (container) container.removeEventListener("mousemove", handleMouseMove); };
  }, []);

  return (
    <div className="contenedor">
      <Encabezado />
      <div className="principal" ref={containerRef}>

        {/* Grid texture overlay */}
        <div className="grid-texture" />

        <div className="principal-contenedor">
          <div className="principal-eyebrow"></div>

          <h1>
            Bienvenido a <span>ConfidAI</span>. Supera el miedo, domina tu confianza.
          </h1>

          <p>
            Entrena tu mente para entrevistas reales. Nuestro evaluador de IA te ayuda
            a gestionar la ansiedad, mejorar tu comunicación no verbal y proyectar seguridad.
          </p>

          <button
      className="btn-principal"
      onClick={() => navigate("/avatar")}
    >
      ▶ INICIAR ENTREVISTA DE CONFIANZA
    </button>
        </div>

        <div className="principal-imagen" ref={imageRef}>
          <img
            src="https://png.pngtree.com/png-clipart/20240829/original/pngtree-isolated-on-white-ai-robot-analyzing-through-3d-transparent-background-png-image_15878991.png"
            alt="IA"
          />
        </div>

        <div className="principal-cartas">
          <div className="carta" data-stat="progress">
            <strong>Última Sesión</strong>
            <p>Hace 2 días · 78/100 (Confianza)</p>
          </div>
          <div className="carta">
            <strong>Entrevistas Completadas</strong>
            <p>4 Sesiones (Nivel Inicial)</p>
          </div>
          <div className="carta">
            <strong>Área Principal a Mejorar</strong>
            <p>Manejo de la Ansiedad (Nerviosismo)</p>
          </div>
        </div>
      </div>
    </div>
  );
}