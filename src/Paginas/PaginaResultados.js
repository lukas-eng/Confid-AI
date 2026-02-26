import React, { useEffect, useState } from "react";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  ResponsiveContainer,
} from "recharts";
import "../Style/Resultados.css";
import EncabezadoResultados from "../Componentes/EncabezadoResultados";

const radarData = [
  { skill: "Empatía", value: 80 },
  { skill: "Escucha Activa", value: 85 },
  { skill: "Resiliencia", value: 75 },
  { skill: "Comunicación No Verbal", value: 70 },
  { skill: "Asertividad", value: 78 },
];

const nonverbalItems = [
  { icon: "👁️", label: "Contacto Visual", value: "Constante", status: "Excelente", color: "#00ff88" },
  { icon: "🎙️", label: "Tono de Voz", value: "Seguro y firme", status: "Óptimo", color: "#00d4ff" },
  { icon: "😌", label: "Expresiones Faciales", value: "Naturales", status: "Normal", color: "#ffb800" },
];

const feedbackItems = [
  { label: "Situación difícil en equipo", value: "Buen uso del método STAR. Respuesta estructurada y clara.", score: 92 },
  { label: "Manejo de conflictos", value: "Enfoque colaborativo y asertivo. Muy bien articulado.", score: 88 },
  { label: "Liderazgo bajo presión", value: "Demuestra capacidad de decisión con empatía hacia el equipo.", score: 81 },
  { label: "Adaptabilidad", value: "Ejemplos concretos y relevantes con buena narrativa.", score: 79 },
];

const actionItems = [
  { icon: "🧘", text: "Respiración diafragmática para reducir ansiedad ante auditorios" },
  { icon: "🎤", text: "Ejercicios de oratoria: debates y presentaciones cronometradas" },
  { icon: "🤝", text: "Role-play de negociación en escenarios de alta presión" },
  { icon: "📖", text: "Lectura activa sobre inteligencia emocional aplicada" },
  { icon: "📹", text: "Grabación y análisis de tus propias presentaciones" },
  { icon: "🔄", text: "Práctica de reformulación positiva ante críticas" },
  { icon: "💬", text: "Sesiones de feedback 360° con pares y mentores" },
];

function AnimatedNumber({ target, suffix = "" }) {
  const [count, setCount] = useState(0);
  useEffect(() => {
    let start = 0;
    const duration = 1800;
    const step = (timestamp) => {
      if (!start) start = timestamp;
      const progress = Math.min((timestamp - start) / duration, 1);
      const ease = 1 - Math.pow(1 - progress, 4);
      setCount(Math.floor(ease * target));
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [target]);
  return <>{count}{suffix}</>;
}

function GlowCard({ children, delay = 0, accentGreen = false }) {
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const timer = setTimeout(() => setVisible(true), delay);
    return () => clearTimeout(timer);
  }, [delay]);
  return (
    <div
      className={`glow-card${accentGreen ? " glow-card--green" : ""}${visible ? " glow-card--visible" : ""}`}
      style={{ transitionDelay: `${delay}ms` }}
    >
      <div className="glow-card__top-line" />
      {children}
    </div>
  );
}

export default function PaginaPerfil() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => { setMounted(true); }, []);

  return (
    <div className="pagina-perfil">
      <EncabezadoResultados />

      <div className="orb orb--blue" />
      <div className="orb orb--cyan" />
      <div className="orb orb--green" />
      <div className="grid-texture" />

      <div className={`perfil-inner${mounted ? " perfil-inner--visible" : ""}`}>

        <div className="perfil-header">
          <div>
            <h1 className="perfil-title">
              Resultados de tu<br />Entrevista
            </h1>
          </div>
          <div className="perfil-header-right">
            <button className="btn-download">↓ &nbsp; Descargar Reporte PDF</button>

          </div>
        </div>

        <div className="results-grid">

          <GlowCard delay={100}>
            <div className="section-label">PUNTUACIÓN GLOBAL</div>
            <div className="card-title">Inteligencia Emocional</div>
            <div className="score-ring">
              <svg width="140" height="140" viewBox="0 0 140 140">
                <defs>  
                  <linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#0057ff" />
                    <stop offset="100%" stopColor="#00d4ff" />
                  </linearGradient>
                </defs>
                <circle className="ring-bg" cx="70" cy="70" r="60" />
                <circle className="ring-fill" cx="70" cy="70" r="60" />
              </svg>
              <div className="score-center">
                <div className="score-number">
                  <AnimatedNumber target={85} suffix="%" />
                </div>
                <div className="score-label">Puntuación</div>
              </div>
            </div>
            <div className="info-box">
              <p>Buen manejo del estrés. Comunicación clara, con signos leves de ansiedad al hablar de conflictos.</p>
            </div>
            <div className="tag-row">
              <span className="tag tag--green">Empatía Alta</span>
              <span className="tag tag--cyan">Resiliente</span>
            </div>
          </GlowCard>

          <GlowCard delay={200}>
            <div className="section-label">EVALUACIÓN MULTIDIMENSIONAL</div>
            <div className="card-title">Habilidades Blandas</div>
            <ResponsiveContainer width="100%" height={220}>
              <RadarChart data={radarData} margin={{ top: 10, right: 20, bottom: 10, left: 20 }}>
                <PolarGrid stroke="rgba(255,255,255,0.08)" />
                <PolarAngleAxis
                  dataKey="skill"
                  tick={{ fill: "rgba(255,255,255,0.55)", fontSize: 11, fontFamily: "DM Sans" }}
                />
                <defs>
                  <linearGradient id="radarGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#0057ff" stopOpacity={0.8} />
                    <stop offset="100%" stopColor="#00d4ff" stopOpacity={0.4} />
                  </linearGradient>
                </defs>
                <Radar
                  dataKey="value"
                  stroke="#00d4ff"
                  strokeWidth={2}
                  fill="url(#radarGrad)"
                  fillOpacity={0.5}
                  dot={{ r: 4, fill: "#00d4ff", stroke: "#020b18", strokeWidth: 2 }}
                />
              </RadarChart>
            </ResponsiveContainer>
            <div className="radar-scores">
              {radarData.map((d) => (
                <div key={d.skill} className="radar-score-item">
                  <div className="radar-score-number">{d.value}</div>
                  <div className="radar-score-label">{d.skill.split(" ")[0].toUpperCase()}</div>
                </div>
              ))}
            </div>
          </GlowCard>

          <GlowCard delay={300} accentGreen>
            <div className="section-label">ANÁLISIS CONDUCTUAL</div>
            <div className="card-title">Lenguaje No Verbal</div>
            {nonverbalItems.map((item) => (
              <div key={item.label} className="nonverbal-item">
                <div
                  className="nonverbal-icon"
                  style={{ background: `${item.color}18`, border: `1px solid ${item.color}40` }}
                >
                  {item.icon}
                </div>
                <div className="nonverbal-text">
                  <div className="nonverbal-sublabel">{item.label}</div>
                  <div className="nonverbal-value">{item.value}</div>
                </div>
                <span
                  className="tag"
                  style={{ background: `${item.color}18`, color: item.color, border: `1px solid ${item.color}40` }}
                >
                  {item.status}
                </span>
              </div>
            ))}
          </GlowCard>
        </div>

        <div className="bottom-grid">

          <GlowCard delay={400}>
            <div className="section-label">EVALUACIÓN CUALITATIVA</div>
            <div className="card-title">Feedback Detallado</div>
            {feedbackItems.map((item, i) => (
              <div key={item.label} className="feedback-item">
                <div className="feedback-header">
                  <div className="feedback-label">{item.label}</div>
                  <div
                    className="feedback-score"
                    style={{
                      color: item.score >= 90 ? "#00ff88" : item.score >= 80 ? "#00d4ff" : "#ffb800",
                    }}
                  >
                    {item.score}<span className="feedback-score-pct">%</span>
                  </div>
                </div>
                <div className="feedback-bar-track">
                  <div
                    className="feedback-bar-fill"
                    style={{
                      width: `${item.score}%`,
                      background:
                        item.score >= 90
                          ? "linear-gradient(90deg,#00b090,#00ff88)"
                          : item.score >= 80
                          ? "linear-gradient(90deg,#0057ff,#00d4ff)"
                          : "linear-gradient(90deg,#ff8c00,#ffb800)",
                      transitionDelay: `${0.8 + i * 0.2}s`,
                    }}
                  />
                </div>
                <p className="feedback-text">{item.value}</p>
              </div>
            ))}
          </GlowCard>

          <GlowCard delay={500} accentGreen>
            <div className="section-label">HOJA DE RUTA</div>
            <div className="card-title">Plan de Acción</div>
            {actionItems.map((item, i) => (
              <div key={i} className="action-item">
                <div className="action-icon">{item.icon}</div>
                <p className="action-text">{item.text}</p>
              </div>
            ))}
          </GlowCard>
        </div>
      </div>
    </div>
  );
}