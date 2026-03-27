import axios from 'axios';

const API_URL = 'http://localhost:8000/interview';

// ============================================
// ENVIAR RESPUESTA DE VOZ NORMAL
// ============================================
export const enviarRespuestaVoz = async (audioBlob, historial, segundosRestantes = 900) => {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'grabacion.webm');
    formData.append('historial', JSON.stringify(historial));
    formData.append('segundos_restantes', segundosRestantes);

    const response = await axios.post(`${API_URL}/responder-voz`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

// ============================================
// AVISAR SILENCIO — usuario lleva 1 min sin grabar
// ============================================
export const avisarSilencio = async (historial, segundosRestantes = 900) => {
    const formData = new FormData();
    formData.append('historial', JSON.stringify(historial));
    formData.append('segundos_restantes', segundosRestantes);

    const response = await axios.post(`${API_URL}/silencio`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

// ============================================
// GENERAR REPORTE FINAL DE LA ENTREVISTA
// ============================================
export const generarReporte = async (historial, metricasVoz) => {
    const formData = new FormData();
    formData.append('historial', JSON.stringify(historial));
    formData.append('metricas_voz', JSON.stringify(metricasVoz));

    const response = await axios.post(`${API_URL}/generar-reporte`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};