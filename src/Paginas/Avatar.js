import React, { useState, useRef, useEffect } from 'react';
import { enviarRespuestaVoz } from '../Services/InterviewService';
import "../Style/Avatar.css";
import * as faceapi from "face-api.js";

const Avatar = () => {

    // states: 'idle', 'listening', 'processing', 'speaking'
    const [status, setStatus] = useState('idle');
    const [historial, setHistorial] = useState([]);
    const [errorMsg, setErrorMsg] = useState('');

    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);
    const chatEndRef = useRef(null);
    const audioPlayerRef = useRef(null);
    const localVideoRef = useRef(null);
    const [cameraError, setCameraError] = useState(false);
    const intervalRef = useRef(null);

    // IMÁGENES DEL MICRÓFONO (DESDE INTERNET)
    const micImages = {
        idle: "https://cdn.pixabay.com/photo/2022/10/06/12/14/microphone-7502540_1280.png",
        listening: "https://cdn-icons-png.flaticon.com/512/1828/1828843.png"
    };
    const iniciarAnalisis = () => {
        console.log("Analisis iniciado");


    if (intervalRef.current) return; // evita duplicados


    intervalRef.current = setInterval(async () => {

        const video = localVideoRef.current;
if (
    !video ||
    video.readyState !== 4 ||
    !video.videoWidth ||
    !video.videoHeight
) {
    console.log("Video aún no listo");
    return;
}
        try {

            const deteccion = await faceapi
                .detectSingleFace(
                    video,
                    new faceapi.TinyFaceDetectorOptions({
                        inputSize: 416,
                        scoreThreshold: 0.3
                    })
                )
                .withFaceExpressions();

            if (!deteccion) return;

            console.log("Emociones:", deteccion.expressions);

        } catch (err) {
            return;
        }

    }, 2000);
};

    // Activar camara web al entrar a la entrevista
    useEffect(() => {
        const initCamera = async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                if (localVideoRef.current) {
                    localVideoRef.current.srcObject = stream;
                    
                }
            } catch (err) {
                console.error("No se pudo acceder a la cámara:", err);
                setCameraError(true);
            }
        };
        initCamera();

        return () => {

    if (intervalRef.current) {
        clearInterval(intervalRef.current);
    }

    if (localVideoRef.current && localVideoRef.current.srcObject) {
        const tracks = localVideoRef.current.srcObject.getTracks();
        tracks.forEach(track => track.stop());
    }
};
        
    }, []);
    useEffect(() => {

    const cargarModelos = async () => {

        await faceapi.nets.tinyFaceDetector.loadFromUri("/models");
        await faceapi.nets.faceExpressionNet.loadFromUri("/models");
        console.log("Modelos cargados");

        const video = localVideoRef.current;

        if (video) {
            video.addEventListener("loadeddata", () => {
                
            });
        }

    };

    cargarModelos();

}, []);

    // Auto-scroll chat
    useEffect(() => {
        if (chatEndRef.current) {
            chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [historial, status]);

    const handleAudioEnded = () => {
        setStatus('idle');
    };

    const iniciarGrabacion = async () => {

        setErrorMsg('');
        audioChunksRef.current = [];

        if (audioPlayerRef.current) {
            audioPlayerRef.current.pause();
            audioPlayerRef.current.currentTime = 0;
        }

        try {

            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            mediaRecorderRef.current = new MediaRecorder(stream);

            mediaRecorderRef.current.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunksRef.current.push(event.data);
                }
            };

            mediaRecorderRef.current.onstop = async () => {

                const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
                audioChunksRef.current = [];

                setStatus('processing');

                try {

                    const respuesta = await enviarRespuestaVoz(audioBlob, historial);

                    const nuevoHistorial = [
                        ...historial,
                        { rol: 'usuario', contenido: respuesta.texto_usuario },
                        { rol: 'entrevistador', contenido: respuesta.respuesta_texto }
                    ];

                    setHistorial(nuevoHistorial);

                    const audioUrl = `http://localhost:8000/${respuesta.audio_url}`;

                    if (!audioPlayerRef.current) {
                        audioPlayerRef.current = new Audio(audioUrl);
                        audioPlayerRef.current.addEventListener('ended', handleAudioEnded);
                    } else {
                        audioPlayerRef.current.src = audioUrl;
                    }

                    setStatus('speaking');

                    audioPlayerRef.current.play().catch(e => {
                        console.error("Error reproduciendo audio:", e);
                        setStatus('idle');
                        setErrorMsg("No se pudo reproducir el audio de respuesta.");
                    });

                } catch (error) {

                    console.error("Error en backend:", error);
                    setStatus('idle');

                    if (error.response && error.response.status === 500) {
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

    const detenerGrabacion = () => {

        if (mediaRecorderRef.current && status === 'listening') {
            mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
            mediaRecorderRef.current.stop();
        }

    };

    const getStatusLabel = () => {

        switch (status) {
            case 'idle': return 'Esperando...';
            case 'listening': return 'Te estoy escuchando...';
            case 'processing': return 'Analizando respuesta...';
            case 'speaking': return 'Entrevistadora hablando...';
            default: return '';
        }

    };

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

        if (status === 'listening') {
            baseStyle.boxShadow = '0 0 40px rgba(236,72,153,0.6) inset';
        }

        if (status === 'processing') {
            baseStyle.boxShadow = '0 0 30px rgba(245,158,11,0.5) inset';
        }

        if (status === 'speaking') {
            baseStyle.boxShadow = '0 0 50px rgba(16,185,129,0.6) inset';
        }

        return baseStyle;
    };

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

                    <div className="name-tag">
                        Entrevistadora AI
                    </div>

                </div>

                {/* USUARIO */}
                <div className="video-pane user-pane">

                <video
                ref={localVideoRef}
                autoPlay
                playsInline
                muted
                className="pane-video-feed"
                onLoadedData={iniciarAnalisis}
                />

                    {cameraError && (
                        <div className="camera-error-overlay">
                            Cámara no disponible
                        </div>
                    )}

                    <div className="name-tag">
                        Tú
                    </div>

                </div>

            </div>

            {/* BOTÓN MICRÓFONO */}

            <div className="split-controls">

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

                            <div className="message-content">
                                ...
                            </div>

                        </div>

                    )}

                    <div ref={chatEndRef} />

                </div>

            </div>

        </div>

    );

};

export default Avatar;