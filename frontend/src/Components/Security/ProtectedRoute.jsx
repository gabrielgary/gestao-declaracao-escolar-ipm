import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../Context/AuthContext';
import Loading from '../Elements/Loading/Loading';

/**
 * Componente para proteger rotas baseado em autenticação e tipo de usuário
 * 
 * @param {Array} allowedTypes - Lista de tipos permitidos (ex: ['aluno', 'funcionario'])
 * @param {children} children - Componente a ser renderizado
 */
const ProtectedRoute = ({ allowedTypes, children }) => {
    const { user, loading } = useAuth();
    const location = useLocation();

    if (loading) {
        return (
            <div style={{
                height: '100vh',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                background: 'var(--bg-main)',
                color: 'var(--primary)'
            }}>
                <Loading/>
            </div>
        );
    }

    if (!user) {
        // Redireciona para o login correspondente ao tipo de rota tentada
        let loginPath = '/public/site';
        if (location.pathname.startsWith('/admin')) loginPath = '/admin/auth';
        else if (location.pathname.startsWith('/student')) loginPath = '/student/auth';
        else if (location.pathname.startsWith('/parent')) loginPath = '/parent/auth';

        return <Navigate to={loginPath} state={{ from: location }} replace />;
    }

    if (allowedTypes && !allowedTypes.includes(user.tipo)) {
        // Se estiver logado mas não tiver permissão para esta área específica
        return <Navigate to="/" replace />;
    }

    return children;
};

export default ProtectedRoute;
