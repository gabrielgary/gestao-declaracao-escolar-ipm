import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api from '../Services/api';

const AuthContext = createContext();

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    const logout = useCallback(async () => {
        try {
            const userType = localStorage.getItem('user_type');
            if (user && userType) {
                await api.post('auth/logout/', {
                    user_id: user.id,
                    user_type: userType
                });
            }
        } catch {
            // Ignora erro no logout
        } finally {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user_type');
            setUser(null);
        }
    }, [user]);

    useEffect(() => {
        const loadUser = async () => {
            const token = localStorage.getItem('access_token');
            const userType = localStorage.getItem('user_type');

            console.log("Iniciando loadUser. Token presente:", !!token, "Tipo:", userType);

            if (token) {
                try {
                    const response = await api.get('auth/me/');
                    console.log("Resposta me_view:", response.data);
                    setUser(response.data.user || response.data);
                } catch (error) {
                    console.error("Erro no me_view:", error.response?.status, error.response?.data);

                    if (error.response && [401, 403].includes(error.response.status)) {
                        console.warn("Sessão inválida. Executando logout...");
                        logout();
                    }
                }
            }
            setLoading(false);
        };

        loadUser();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const login = async (email, senha, tipo_usuario) => {
        try {
            const response = await api.post('auth/login/', {
                email,
                senha,
                tipo_usuario
            });

            const { access, refresh, user } = response.data;

            localStorage.setItem('access_token', access);
            localStorage.setItem('refresh_token', refresh);
            localStorage.setItem('user_type', tipo_usuario);

            setUser(user);
            return { success: true };
        } catch (error) {
            console.log("Login error:", error);
            return {
                success: false,
                message: error.response?.data?.error || "Falha na autenticação"
            };
        }
    };

    const forgotPassword = async (email) => {
        try {
            const response = await api.post('auth/forgot-password/', { email });
            return { success: true, message: response.data.message };
        } catch (error) {
            return {
                success: false,
                message: error.response?.data?.error || "Falha ao enviar e-mail de recuperação"
            };
        }
    };

    const resetPassword = async (token, nova_senha) => {
        try {
            const response = await api.post('auth/reset-password/', { token, nova_senha });
            return { success: true, message: response.data.message };
        } catch (error) {
            return {
                success: false,
                message: error.response?.data?.error || "Falha ao redefinir senha"
            };
        }
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, logout, forgotPassword, resetPassword }}>
            {children}
        </AuthContext.Provider>
    );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
    return useContext(AuthContext);
}
