import axios from 'axios';

const API_URL = 'http://localhost:8000/interview';

export const enviarRespuestaVoz = async (audioBlob, historial) => {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'grabacion.webm');
    formData.append('historial', JSON.stringify(historial));

    const response = await axios.post(`${API_URL}/responder-voz`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};