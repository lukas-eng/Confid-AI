import { useState } from 'react';
import '../Style/FormuRegis.css';
import { useNavigate } from 'react-router-dom';
import ElectricBorder from '../Componentes/ElectricBorder';
import { registro } from '../Services/AuthService';

const FormuRegis = () => {

  const [nombre, setNombre] = useState("");
  const [apellido, setApellido] = useState("");
  const [correo, setCorreo] = useState("");
  const [telefono, setTelefono] = useState("");
  const [password, setPassword] = useState("");

  const navigate = useNavigate();

  const irInicio = () => {
    navigate('/');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      await registro({
        nombre,
        apellido,
        correo,
        telefono,
        password
      });

      alert("Registro exitoso");
      navigate("/");

    } catch (error) {
      alert("Error al registrar");
      console.log(error);
    }
  };

  return (
    <div className='contenedorformu'>

      <ElectricBorder
        color="#7df9ff"
        speed={1}
        chaos={0.12}
        thickness={2}
        style={{ borderRadius: 16 }}
      >
        <div className='formularioregis'>
          <h1 className='tituloregis'>Formulario de Registro</h1>

          <form onSubmit={handleSubmit}>

            <div>
              <label className="nombre">Nombre:</label>
              <input
                type="text"
                value={nombre}
                onChange={(e) => setNombre(e.target.value)}
                required
              />
            </div>

            <div>
              <label className="apellido">Apellido:</label>
              <input
                type="text"
                value={apellido}
                onChange={(e) => setApellido(e.target.value)}
                required
              />
            </div>

            <div>
              <label className="email">Correo electrónico:</label>
              <input
                type="email"
                value={correo}
                onChange={(e) => setCorreo(e.target.value)}
                required
              />
            </div>

            <div>
              <label className="telefono">Telefono:</label>
              <input
                type="text"
                value={telefono}
                onChange={(e) => setTelefono(e.target.value)}
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
              <button type="submit">Registrarse</button>
              <button type="button" onClick={irInicio}>
                Iniciar sesión
              </button>
            </div>

          </form>
        </div>
      </ElectricBorder>

      <img
        className='imgformu'
        src="https://img.freepik.com/foto-gratis/concepto-ser-humano-generado-ia_23-2150688377.jpg?semt=ais_hybrid&w=740&q=80"
        alt="Registro de Usuario"
      />

    </div>
  );
};

export default FormuRegis;
