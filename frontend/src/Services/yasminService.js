import axios from 'axios';

const YASMIN_API_URL = 'https://yasmin-j7ie.onrender.com/;

const yasminApi = axios.create({
    baseURL: YASMIN_API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const yasminService = {
    /**
     * Envia uma mensagem para a Yasmin IA
     * @param {string} message - A mensagem do utilizador
     * @param {string} role - O papel do utilizador (student, admin, parent)
     * @param {string|null} userId - ID do utilizador
     * @param {string|null} userToken - Token JWT do utilizador logado
     */
    sendMessage: async (message, role = 'student', userId = null, userToken = null) => {
        try {
            const response = await yasminApi.post('/chat', {
                message,
                role,
                user_id: userId,
                user_token: userToken
            });
            return response.data;
        } catch (error) {
            console.error('Erro ao comunicar com Yasmin:', error);
            throw error;
        }
    },

    /**
     * Limpa o histórico de conversa de um utilizador
     * @param {string|null} userId - ID do utilizador
     */
    clearHistory: async (userId = null) => {
        try {
            const response = await yasminApi.post('/clear-history', {
                user_id: userId
            });
            return response.data;
        } catch (error) {
            console.error('Erro ao limpar histórico:', error);
            throw error;
        }
    },

    /**
     * Verifica se a Yasmin está online
     */
    checkStatus: async () => {
        try {
            const response = await yasminApi.get('/health');
            return response.data;
        } catch (error) {
            return { status: 'offline', error: error.message };
        }
    }
};

export default yasminService;
