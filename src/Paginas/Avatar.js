import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { enviarRespuestaVoz, avisarSilencio, generarReporte } from '../Services/InterviewService';
import "../Style/Avatar.css";

const DURACION_MAX_SEGUNDOS = 15 * 60; // 15 minutos
const SILENCIO_MAX_SEG = 15;           // 1 minuto sin grabar = Luvani reactiva
const DELAY_REDIRECCION_MS = 4000;     // esperar 4s después del audio de cierre antes de redirigir

const Avatar = () => {

    // states: 'idle', 'listening', 'processing', 'speaking', 'finished'
    const [status, setStatus] = useState('idle');
    const [historial, setHistorial] = useState([]);
    const [errorMsg, setErrorMsg] = useState('');
    const [metricasVoz, setMetricasVoz] = useState([]);

    const navigate = useNavigate(); // ← para redirigir al home

    const mediaRecorderRef    = useRef(null);
    const audioChunksRef      = useRef([]);
    const chatEndRef          = useRef(null);
    const audioPlayerRef      = useRef(null);
    const localVideoRef       = useRef(null);
    const inicioEntrevistaRef = useRef(null);
    const silencioTimerRef    = useRef(null);
    const redireccionTimerRef = useRef(null); // ← timer para redirigir después del audio

    const [cameraError, setCameraError] = useState(false);

    const micImages = {
        idle: "https://cdn.pixabay.com/photo/2022/10/06/12/14/microphone-7502540_1280.png",
        listening: "https://cdn-icons-png.flaticon.com/512/1828/1828843.png"
    };

    // ============================================
    // CALCULAR SEGUNDOS RESTANTES
    // ============================================
    const calcularSegundosRestantes = () => {
        if (!inicioEntrevistaRef.current) return DURACION_MAX_SEGUNDOS;
        const transcurridos = Math.floor((Date.now() - inicioEntrevistaRef.current) / 1000);
        return Math.max(0, DURACION_MAX_SEGUNDOS - transcurridos);
    };

    // ============================================
    // FINALIZAR ENTREVISTA Y REDIRIGIR
    // Se llama siempre que entrevista_finalizada === true
    // Espera a que termine el audio de despedida, luego redirige
    // ============================================
    const finalizarYRedirigir = async (audioUrl, historyToEvaluate, metricsToEvaluate) => {
        setStatus('finished');

        if (!audioPlayerRef.current) {
            audioPlayerRef.current = new Audio(audioUrl);
        } else {
            audioPlayerRef.current.src = audioUrl;
        }

        audioPlayerRef.current.play().catch(() => {});

        try {
            const metricasM = metricsToEvaluate || metricasVoz;
            const avgSpeed = metricasM.length ? metricasM.reduce((acc, curr) => acc + (curr.velocidad_palabras_segundo || 0), 0) / metricasM.length : 0;
            const totalMule = metricasM.reduce((acc, curr) => acc + (curr.muletillas_detectadas || 0), 0);
            const maxPause = metricasM.length ? Math.max(...metricasM.map(m => m.pausa_maxima || 0)) : 0;

            const metricasResumen = {
               velocidad_promedio: avgSpeed.toFixed(2),
               total_muletillas: totalMule,
               pausa_maxima_extrema: maxPause
            };

            const reporte = await generarReporte(historyToEvaluate || historial, metricasResumen);
            localStorage.setItem("reporte_entrevista", JSON.stringify(reporte));
            
            navigate('/resultados');

        } catch (e) {
            console.error("Error generando reporte:", e);
            setErrorMsg("No se pudo generar el reporte. Redirigiendo...");
            setTimeout(() => {
                navigate('/resultados');
            }, 3000);
        }
    };

    // ============================================
    // REPRODUCIR AUDIO NORMAL (sin finalizar)
    // ============================================
    const reproducirAudio = (audioUrl, onEnded) => {
        if (!audioPlayerRef.current) {
            audioPlayerRef.current = new Audio(audioUrl);
            audioPlayerRef.current.addEventListener('ended', onEnded);
        } else {
            audioPlayerRef.current.onended = null;
            audioPlayerRef.current.src = audioUrl;
            audioPlayerRef.current.addEventListener('ended', onEnded);
        }
        setStatus('speaking');
        audioPlayerRef.current.play().catch(e => {
            console.error("Error reproduciendo audio:", e);
            setStatus('idle');
            setErrorMsg("No se pudo reproducir el audio de respuesta.");
        });
    };

    // ============================================
    // TIMER DE SILENCIO
    // ============================================
    const limpiarTimerSilencio = () => {
        if (silencioTimerRef.current) {
            clearTimeout(silencioTimerRef.current);
            silencioTimerRef.current = null;
        }
    };

    const iniciarTimerSilencio = (historialActual) => {
        limpiarTimerSilencio();

        silencioTimerRef.current = setTimeout(async () => {
            setStatus(currentStatus => {
                if (currentStatus !== 'idle') return currentStatus;

                (async () => {
                    try {
                        const segundosRestantes = calcularSegundosRestantes();
                        if (segundosRestantes <= 60) return;

                        console.log("🔇 Silencio detectado — Luvani reactivando...");

                        const respuesta = await avisarSilencio(historialActual, segundosRestantes);

                        setHistorial(prev => [
                            ...prev,
                            { rol: 'entrevistador', contenido: respuesta.respuesta_texto }
                        ]);

                        const audioUrl = `http://localhost:8000/${respuesta.audio_url}`;

                        // 3 silencios → finalizar y redirigir
                        if (respuesta.entrevista_finalizada) {
                            finalizarYRedirigir(audioUrl, historialActual, metricasVoz);
                            return;
                        }

                        reproducirAudio(audioUrl, handleAudioEnded);

                    } catch (e) {
                        console.error("Error al avisar silencio:", e);
                        setStatus('idle');
                    }
                })();

                return 'processing';
            });

        }, SILENCIO_MAX_SEG * 1000);
    };

    // ============================================
    // ACTIVAR CÁMARA + GUARDAR INICIO
    // ============================================
    useEffect(() => {
    inicioEntrevistaRef.current = Date.now();

    let intervaloEmocion = null;

    const initCamera = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            const video = localVideoRef.current;

            if (video) video.srcObject = stream;

           

        } catch (err) {
            console.error("No se pudo acceder a la cámara:", err);
            setCameraError(true);
        }
    };

    initCamera();

    const video = localVideoRef.current;

    return () => {
        limpiarTimerSilencio();

        if (intervaloEmocion) clearInterval(intervaloEmocion);

        if (redireccionTimerRef.current) clearTimeout(redireccionTimerRef.current);

        if (video && video.srcObject) {
            video.srcObject.getTracks().forEach(track => track.stop());
        }
    };
}, [status]);


    // ============================================
    // ARRANCAR / CANCELAR TIMER SEGÚN ESTADO
    // ============================================
    useEffect(() => {
        if (status === 'idle') {
            iniciarTimerSilencio(historial);
        } else {
            limpiarTimerSilencio();
        }
    }, [status, historial]);

    // Auto-scroll chat
    useEffect(() => {
        if (chatEndRef.current) {
            chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [historial, status]);

    const handleAudioEnded = () => {
        if (status !== 'finished') setStatus('idle');
    };

    // ============================================
    // INICIAR GRABACIÓN
    // ============================================
    const iniciarGrabacion = async () => {
        setErrorMsg('');
        audioChunksRef.current = [];
        limpiarTimerSilencio();

        if (audioPlayerRef.current) {
            audioPlayerRef.current.pause();
            audioPlayerRef.current.currentTime = 0;
        }

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorderRef.current = new MediaRecorder(stream);

            mediaRecorderRef.current.ondataavailable = (event) => {
                if (event.data.size > 0) audioChunksRef.current.push(event.data);
            };

            mediaRecorderRef.current.onstop = async () => {
                const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
                audioChunksRef.current = [];

                setStatus('processing');

                const segundosRestantes = calcularSegundosRestantes();

                try {
                    const respuesta = await enviarRespuestaVoz(audioBlob, historial, segundosRestantes);

                    const nuevoHistorial = [
                        ...historial,
                        { rol: 'usuario', contenido: respuesta.texto_usuario },
                        { rol: 'entrevistador', contenido: respuesta.respuesta_texto }
                    ];

                    setHistorial(nuevoHistorial);

                    const audioUrl = `http://localhost:8000/${respuesta.audio_url}`;

                    const nuevasMetricas = respuesta.analisis_voz 
                        ? [...metricasVoz, respuesta.analisis_voz] 
                        : metricasVoz;
                        
                    if(respuesta.analisis_voz) {
                        setMetricasVoz(nuevasMetricas);
                    }

                    // Tiempo agotado → finalizar y redirigir
                    if (respuesta.entrevista_finalizada) {
                        finalizarYRedirigir(audioUrl, nuevoHistorial, nuevasMetricas);
                        return;
                    }

                    reproducirAudio(audioUrl, handleAudioEnded);

                } catch (error) {
                    console.error("Error en backend:", error);
                    setStatus('idle');
                    if (error.response?.status === 500) {
                        setErrorMsg("Error 500 en el servidor.");
                    } else {
                        setErrorMsg("No se pudo conectar con el servidor.");
                    }
                }
            };

            mediaRecorderRef.current.start();
            setStatus('listening');

        } catch (error) {
            console.error("Error micrófono:", error);
            setErrorMsg("Debes permitir el acceso al micrófono.");
        }
    };

    // ============================================
    // DETENER GRABACIÓN
    // ============================================
    const detenerGrabacion = () => {
        if (mediaRecorderRef.current && status === 'listening') {
            mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
            mediaRecorderRef.current.stop();
        }
    };

    // ============================================
    // ETIQUETA DE ESTADO
    // ============================================
    const getStatusLabel = () => {
        switch (status) {
            case 'idle':       return 'Esperando...';
            case 'listening':  return 'Te estoy escuchando...';
            case 'processing': return 'Analizando respuesta...';
            case 'speaking':   return 'Entrevistadora hablando...';
            case 'finished':   return 'Redirigiendo...';
            default:           return '';
        }
    };

    // ============================================
    // ESTILO DINÁMICO DEL AVATAR
    // ============================================
    const getImageContainerStyle = () => {
        let baseStyle = {
            width: '100%',
            height: '100%',
            borderRadius: '16px',
            overflow: 'hidden',
            transition: 'all 0.5s',
            position: 'absolute',
            top: 0,
            left: 0,
            zIndex: 10,
            backgroundImage: "url('/entrevistadora.jpg')",
            backgroundSize: 'cover',
            backgroundPosition: 'center top'
        };

        if (status === 'listening')  baseStyle.boxShadow = '0 0 40px rgba(236,72,153,0.6) inset';
        if (status === 'processing') baseStyle.boxShadow = '0 0 30px rgba(245,158,11,0.5) inset';
        if (status === 'speaking')   baseStyle.boxShadow = '0 0 50px rgba(16,185,129,0.6) inset';
        if (status === 'finished') {
            baseStyle.boxShadow = '0 0 40px rgba(100,116,139,0.5) inset';
            baseStyle.filter = 'grayscale(30%)';
        }

        return baseStyle;
    };

    // ============================================
    // RENDER
    // ============================================
    return (
        <div className="avatar-container split-layout">

            <div className="grid-texture"></div>

            {errorMsg && (
                <div className="error-toast">
                    <span>{errorMsg}</span>
                </div>
            )}

            <div>
                <h1 className="logo_text">
                    Confid<span className="highlight">AI</span>
                </h1>
                <div className={`status-badge ${status}`}>
                    <div className="status-dot"></div>
                    {getStatusLabel()}
                </div>
            </div>

            <div className="video-call-grid">

                {/* IA */}
                <div className="video-pane ai-pane">
                    <div style={getImageContainerStyle()}></div>
                    <div className="name-tag">Entrevistadora AI</div>
                </div>

                {/* USUARIO */}
                <div className="video-pane user-pane">
                    <video
                        ref={localVideoRef}
                        autoPlay
                        playsInline
                        muted
                        className="pane-video-feed"
                    />
                    
                    {cameraError && (
                        <div className="camera-error-overlay">
                            Cámara no disponible
                        </div>
                    )}
                    <div className="name-tag">Tú</div>
                </div>

            </div>

            {/* BOTÓN MICRÓFONO */}
            <div className="split-controls">
                {status === 'finished' ? (
                    <div className="finished-message">
                        Entrevista finalizada. Redirigiendo...
                    </div>
                ) : (
                    <button
                        className={`mic-button ${status === 'listening' ? 'recording' : 'idle'}`}
                        onClick={status === 'listening' ? detenerGrabacion : iniciarGrabacion}
                        disabled={status === 'processing' || status === 'speaking'}
                    >
                        <img
                            src={status === "listening" ? micImages.listening : micImages.idle}
                            alt="mic"
                            className="mic-icon"
                        />
                        {status === "listening" ? "Detener Grabación" : "Responder"}
                    </button>
                )}
            </div>

            {/* CHAT */}
            <div className="chat-container split-chat-container">
                <div className="chat-messages horizontal-chat">

                    {historial.length === 0 ? (
                        <div style={{ textAlign: 'center', color: '#64748b', margin: 'auto' }}>
                            El historial de la entrevista aparecerá aquí.
                        </div>
                    ) : (
                        historial.map((msg, index) => (
                            <div key={index} className={`message ${msg.rol === 'usuario' ? 'usuario' : 'entrevistador'}`}>
                                <div className="message-role">
                                    {msg.rol === 'usuario' ? 'Tú' : 'Entrevistadora'}
                                </div>
                                <div className="message-content">
                                    {msg.contenido}
                                </div>
                            </div>
                        ))
                    )}

                    {status === 'processing' && (
                        <div className="message entrevistador">
                            <div className="message-content">...</div>
                        </div>
                    )}

                    <div ref={chatEndRef} />
                </div>
            </div>

        </div>
    );
};

export default Avatar;