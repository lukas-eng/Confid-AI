import React, { useState, useRef } from 'react';
// IMPORTANTE: Según tu error, pusiste la función en AuthService. Cámbialo si es necesario.
import { enviarRespuestaVoz } from '../Services/InterviewService'; 

const Avatar = () => {
    const [grabando, setGrabando] = useState(false);
    const [historial, setHistorial] = useState([]);
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);

    const iniciarGrabacion = async () => {
        try {
            // 1. Solicitamos el micrófono (Aquí manejamos el NotAllowedError)
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
                
                try {
                    // 2. Enviamos al backend (Aquí es donde choca con tu error 500)
                    const respuesta = await enviarRespuestaVoz(audioBlob, historial);
                    
                    const nuevoHistorial = [
                        ...historial,
                        { rol: 'usuario', contenido: respuesta.texto_usuario },
                        { rol: 'entrevistador', contenido: respuesta.respuesta_texto }
                    ];
                    setHistorial(nuevoHistorial);

                    // 3. Reproducimos el audio que devuelve Gemini
                    const audioIA = new Audio(`http://localhost:8000/${respuesta.audio_url}`);
                    audioIA.play();
                    
                } catch (error) {
                    console.error("Error en el servidor backend:", error);
                    alert("El servidor falló al procesar el audio (Error 500). Revisa la terminal de Python.");
                }
            };

            audioChunksRef.current = [];
            mediaRecorderRef.current.start();
            setGrabando(true);

        } catch (error) {
            // Esto atrapa el error de permisos que me mostraste
            console.error("Error de permisos de micrófono:", error);
            alert("¡Necesitamos acceso a tu micrófono para simular la entrevista en ConfidAI! Por favor, revisa los permisos.");
        }
    };

    const detenerGrabacion = () => {
        if (mediaRecorderRef.current && grabando) {
            mediaRecorderRef.current.stop();
            setGrabando(false);
        }
    };

    return (
        <div>
            <h1>Simulador ConfidAI</h1>
            <button 
                onClick={grabando ? detenerGrabacion : iniciarGrabacion}
                style={{ backgroundColor: grabando ? 'red' : 'green', color: 'white', padding: '10px', marginTop: '20px' }}
            >
                {grabando ? 'Detener Grabación y Enviar' : 'Hablar'}
            </button>
        </div>
    );
};

export default Avatar;