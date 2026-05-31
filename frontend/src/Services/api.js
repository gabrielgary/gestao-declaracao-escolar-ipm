import axios from 'axios';

/**
 * Instância do Axios para a API do Backend (Django)
 * A baseURL deve apontar para o endpoint /api/v1/ do Django
 * Em desenvolvimento, geralmente é http://localhost:8000/api/v1/
 */
const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'https://gestao-declaracao-escolar-ipm.onrender.com/api/v1/',
    headers: {
        'Content-Type': 'application/json',
    },
});

/**
 * Interceptor para adicionar o token JWT em cada requisição
 */
api.interceptors.request.use(
    (config) => {
        // Tenta obter o token do localStorage
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

/**
 * Interceptor para lidar com erros de resposta
 * Especialmente erro 401 (Não autorizado), que pode indicar token expirado
 */
api.interceptors.response.use(
    (response) => {
        return response;
    },
    async (error) => {
        const originalRequest = error.config;

        // Se o erro for 401 e não for uma tentativa de login ou refresh
        if (error.response && error.response.status === 401 && !originalRequest._retry && !originalRequest.url.includes('/auth/login/')) {
            originalRequest._retry = true;
            const refreshToken = localStorage.getItem('refresh_token');

            if (refreshToken) {
                try {
                    // Tentar obter novo access token usando a baseURL da própria instância
                    const refreshUrl = `${api.defaults.baseURL}auth/token/refresh/`;
                    const response = await axios.post(refreshUrl, {
                        refresh: refreshToken
                    });

                    if (response.status === 200) {
                        const { access } = response.data;
                        localStorage.setItem('access_token', access);
                        // Atualizar cabeçalhos para requisições futuras e para a requisição atual
                        api.defaults.headers.Authorization = `Bearer ${access}`;
                        originalRequest.headers.Authorization = `Bearer ${access}`;
                        return api(originalRequest);
                    }
                } catch (refreshError) {
                    console.error("Erro ao renovar sessão (Refresh Token):", refreshError);
                    // Se o refresh falhar, limpamos os tokens para forçar login no próximo carregamento
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    // Não chamamos logout() ou redirecionamos aqui para evitar loops, 
                    // o AuthContext lidará com o erro 401 original se este retry falhar.
                }
            }
        }

        // Retorna o erro para ser tratado no componente/serviço
        return Promise.reject(error);
    }
);

export const MEDIA_URL = import.meta.env.VITE_MEDIA_URL || 'https://gestao-declaracao-escolar-ipm.onrender.com/media/';
export default api;
