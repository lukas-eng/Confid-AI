import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import '../Style/FormuRegis.css';
import ElectricBorder from '../Componentes/ElectricBorder';
import { login } from '../Services/AuthService';

const Formuini = () => {
  const navigate = useNavigate();

  const [correo, setCorreo] = useState("");
  const [password, setPassword] = useState("");

  const irRegistro = () => navigate('/registro');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await login({ correo, password });
      alert("Inicio de sesión exitoso");
      navigate('/principal');
    } catch (error) {
      alert("Datos incorrectos");
    }
  };

  return (
    <div className="contenedorformu">

      <div className="grid-texture" />

      <ElectricBorder
        color="#00d4ff"
        speed={1}
        chaos={0.12}
        borderRadius={20}
        style={{ borderRadius: 20 }}
      >
        <div className="formularioregis">
          <h1 className="tituloregis">Inicio de Sesión</h1>
          <p className="tituloregis-sub">Plataforma ConfidAI · Acceso seguro</p>

          <form onSubmit={handleSubmit}>
            <div>
              <label htmlFor="correo">Correo</label>
              <input
                id="correo"
                type="email"
                placeholder="usuario@gmail.com"
                value={correo}
                onChange={(e) => setCorreo(e.target.value)}
                required
              />
            </div>

            <div>
              <label htmlFor="password">Contraseña</label>
              <input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <div className="contenedorbtn">
              <button className="inicio" type="submit">
              &nbsp; Iniciar Sesión
              </button>
              <button className="inicio" type="button" onClick={irRegistro}>
                Registrarse
              </button>
            </div>
          </form>
        </div>
      </ElectricBorder>

      <img
        className="imgformu"
        src="https://static.wixstatic.com/media/55d1d0_774dd340d53b43fab4182fd4f484fcb0~mv2.gif"
        alt="Registro de Usuario"
      />
    </div>
  );
};

export default Formuini;