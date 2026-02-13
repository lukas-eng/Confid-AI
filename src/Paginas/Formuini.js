import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import '../Style/FormuRegis.css';
import ElectricBorder from '../Componentes/ElectricBorder';
import { login } from '../Services/AuthService';

const Formuini = () => {
  const navigate = useNavigate();

  const [correo, setCorreo] = useState("");
  const [password, setPassword] = useState("");

  const irRegistro = () => {
    navigate('/registro');
  };

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
    <div className='contenedorformu'>
      <ElectricBorder
        color="#49faa7"
        speed={1}
        chaos={0.12}
        borderRadius={20}
        style={{ borderRadius: 20 }}
      >
        <div className='formularioregis'>
          <h1 className='tituloregis'>Inicio de Sesión</h1>

          <form onSubmit={handleSubmit}>
            <div>
              <label className="nombre">Correo:</label>
              <input
                type="email"
                value={correo}
                onChange={(e) => setCorreo(e.target.value)}
                required
              />
            </div>

            <div>
              <label className="password">Contraseña:</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <div className='contenedorbtn'>
              <button className='inicio' type="submit">
                Iniciar sesión
              </button>

              <button className='inicio' type="button" onClick={irRegistro}>
                Registrarse
              </button>
            </div>
          </form>
        </div>
      </ElectricBorder>
      <img
        className='imgformu'
        src="https://img.freepik.com/foto-gratis/concepto-ser-humano-generado-ia_23-2150688377.jpg"
        alt="Registro de Usuario"
      />
    </div>
  );
};

export default Formuini;
