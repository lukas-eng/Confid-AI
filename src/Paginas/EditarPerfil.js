import { useState, useRef } from "react";
import "../Style/EditarPerfil.css";

const EyeIcon = ({ open }) =>
  open ? (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94" />
      <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19" />
      <line x1="1" y1="1" x2="23" y2="23" />
    </svg>
  ) : (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  );

const UserIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor" width="28" height="28">
    <path d="M12 12c2.7 0 4.8-2.1 4.8-4.8S14.7 2.4 12 2.4 7.2 4.5 7.2 7.2 9.3 12 12 12zm0 2.4c-3.2 0-9.6 1.6-9.6 4.8v2.4h19.2v-2.4c0-3.2-6.4-4.8-9.6-4.8z" />
  </svg>
);

const CameraIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor" width="14" height="14">
    <path d="M12 15.5A3.5 3.5 0 0 1 8.5 12 3.5 3.5 0 0 1 12 8.5a3.5 3.5 0 0 1 3.5 3.5 3.5 3.5 0 0 1-3.5 3.5m7-10.5h-1.38l-1.65-2H8.03L6.38 5H5A3 3 0 0 0 2 8v11a3 3 0 0 0 3 3h14a3 3 0 0 0 3-3V8a3 3 0 0 0-3-3z" />
  </svg>
);

const EditarPerfil = () => {
  const [avatar,      setAvatar]      = useState(null);
  const [showPwd,     setShowPwd]     = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const fileRef = useRef();

  const handleAvatar = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => setAvatar(ev.target.result);
    reader.readAsDataURL(file);
  };

  return (
    <div className="ep-page">
      <div className="ep-card">

        {/* ══ PANEL IZQUIERDO ══ */}
        <div className="ep-left">
          <div className="img-izq" />
          <img
            src="https://png.pngtree.com/png-vector/20250128/ourmid/pngtree-artificial-intelligence-png-image_15351542.png"
            alt="ilustración"
            className="ep-left-img"
          />
        </div>

        {/* ══ PANEL DERECHO ══ */}
        <div className="ep-right">

          <h1 className="ep-title">Editar perfil</h1>
          <p className="ep-subtitle">
            Actualiza tu información personal y credenciales de acceso.
          </p>

          {/* Avatar */}
          <div className="ep-avatar-row">
            <div className="ep-avatar-wrap" onClick={() => fileRef.current.click()}>
              <div className="ep-avatar-circle">
                {avatar
                  ? <img src={avatar} alt="foto de perfil" />
                  : <UserIcon />
                }
              </div>
              <div className="ep-camera-btn"><CameraIcon /></div>
            </div>

            <input
              ref={fileRef}
              type="file"
              accept="image/*"
              className="ep-hidden"
              onChange={handleAvatar}
            />

            <div className="ep-avatar-meta">
              <strong>Foto de perfil</strong>
              JPG, PNG o GIF — máx. 5 MB
              <button
                type="button"
                className="ep-upload-btn"
                onClick={() => fileRef.current.click()}
              >
                {avatar ? "Cambiar foto" : "Subir foto"}
              </button>
            </div>
          </div>

          {/* Formulario */}
          <form>
            <div className="ep-grid">

              <div className="ep-group">
                <label className="ep-label">Nombre</label>
                <input
                  className="ep-input"
                  type="text"
                  name="firstName"
                  placeholder="Pedro"
                  autoComplete="given-name"
                />
              </div>

              <div className="ep-group">
                <label className="ep-label">Apellido</label>
                <input
                  className="ep-input"
                  type="text"
                  name="lastName"
                  placeholder="Deltondo"
                  autoComplete="family-name"
                />
              </div>

              <div className="ep-group ep-group--full">
                <label className="ep-label">Correo electrónico</label>
                <input
                  className="ep-input"
                  type="email"
                  name="email"
                  placeholder="pedro@bluerise.com"
                  autoComplete="email"
                />
              </div>

              <div className="ep-group ep-group--full">
                <label className="ep-label">Contraseña</label>
                <div className="ep-pwd-wrap">
                  <input
                    className="ep-input"
                    type={showPwd ? "text" : "password"}
                    name="password"
                    placeholder="••••••••"
                    autoComplete="new-password"
                  />
                  <button
                    type="button"
                    className="ep-pwd-toggle"
                    onClick={() => setShowPwd((v) => !v)}
                    aria-label="Mostrar contraseña"
                  >
                    <EyeIcon open={showPwd} />
                  </button>
                </div>
              </div>

              <div className="ep-group ep-group--full">
                <label className="ep-label">Confirmar contraseña</label>
                <div className="ep-pwd-wrap">
                  <input
                    className="ep-input"
                    type={showConfirm ? "text" : "password"}
                    name="confirmPassword"
                    placeholder="••••••••"
                    autoComplete="new-password"
                  />
                  <button
                    type="button"
                    className="ep-pwd-toggle"
                    onClick={() => setShowConfirm((v) => !v)}
                    aria-label="Mostrar contraseña"
                  >
                    <EyeIcon open={showConfirm} />
                  </button>
                </div>
              </div>

            </div>

            <button type="submit" className="ep-submit-btn">
              Guardar cambios
            </button>
            <p className="ep-already">
          <a href="principal" className="ep-link">Cancelar</a>
          </p>
          </form>

        </div>
      </div>
    </div>
  );
};

export default EditarPerfil;