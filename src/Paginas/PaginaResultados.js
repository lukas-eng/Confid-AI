import React from "react";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  ResponsiveContainer,
} from "recharts";
import "../Style/Resultados.css";
import EncabezadoResultados from "../Componentes/EncabezadoResultados";

export default function PaginaPerfil() {
  const radarData = [
    { skill: "Empatía", value: 80 },
    { skill: "Escucha Activa", value: 85 },
    { skill: "Resiliencia", value: 75 },
    { skill: "Comunicación No Verbal", value: 70 },
    { skill: "Asertividad", value: 78 },
  ];

  return (
    <div>
      <EncabezadoResultados />
      <div className="pagina-resultados">
        <div className="resultados-header">
          <h2 className="resultados">Resultados de tu Entrevista</h2>
          <button className="botonreporte">Descargar Reporte PDF</button>
        </div>
        <div className="resultados-grid">
          {/* Inteligencia emocional */}
          <div className="card">
            <h3>Inteligencia Emocional</h3>
            <h1 className="numero">85%</h1>
            <p>
              Buen manejo del estrés. Comunicación clara, con signos leves de
              ansiedad al hablar de conflictos.
            </p>
          </div>

          {/* Gráfica radar */}
          <div className="card">
            <h3>Análisis de Habilidades Blandas</h3>
            <ResponsiveContainer width="100%" height={250}>
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="skill" />
                <Radar dataKey="value" fillOpacity={0.6} />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          {/* Lenguaje no verbal */}
          <div className="card">
            <h3>Análisis de Lenguaje No Verbal</h3>
            <ul>
              <li>Contacto visual: Constante (Bueno)</li>
              <li>Tono de voz: Seguro y firme</li>
              <li>Expresiones faciales: Normales</li>
            </ul>
          </div>
        </div>

        {/* Feedback */}
        <div className="card seccion">
          <h3>Feedback Detallado</h3>
          <p>
            <strong>Situación difícil en equipo:</strong> Buen uso del método
            STAR.
          </p>
          <p>
            <strong>Manejo de conflictos:</strong> Enfoque colaborativo y claro.
          </p>
            <p>
            <strong>Situación difícil en equipo:</strong> Buen uso del método
            STAR.
          </p>
          <p>
            <strong>Manejo de conflictos:</strong> Enfoque colaborativo y claro.
          </p>
        </div>

        {/* Plan de acción */}
        <div className="card seccion">
          <h3>Plan de Acción</h3>
          <ul>
            <li>Respiración para reducir ansiedad</li>
            <li>Ejercicios de oratoria</li>
            <li>Role-play de negociación</li>
            <li>Respiración para reducir ansiedad</li>
            <li>Ejercicios de oratoria</li>
            <li>Role-play de negociación</li>
            <li>Respiración para reducir ansiedad</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
