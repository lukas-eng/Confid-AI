import { useNavigate } from 'react-router-dom';
import '../Style/FormuRegis.css';
import ElectricBorder from '../Componentes/ElectricBorder'; 

const Formuini = () => {
  const navigate = useNavigate();

  const irRegistro = () => {
    navigate('/registro');
  };

  return (
    <div className='contenedorformu'>

      <ElectricBorder
        color="#63fab4"
        speed={1}
        chaos={0.15}
        borderRadius={20}
        style={{ borderRadius: 20 }}
      >
        <div className='formularioregis'>
          <h1 className='tituloregis'>Inicio de Sesión</h1>

          <form>
            <div>
              <label className="nombre">Correo:</label>
              <input type="email" id="nombre" name="nombre" required />
            </div>

            <div>
              <label className="password">Contraseña:</label>
              <input type="password" id="password" name="password" required />
            </div>

            <div className='contenedorbtn'>
              <button type="submit">Iniciar sesión</button>
              <button type="button" onClick={irRegistro}>
                Registrarse
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

export default Formuini;