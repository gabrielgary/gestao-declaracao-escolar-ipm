import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FiHome, FiAlertCircle } from 'react-icons/fi';
import styles from './NotFound.module.css';

const NotFound = () => {
    const navigate = useNavigate();

    return (
        <div className={styles.container}>
            <div className={styles.content}>
                <div className={styles.errorIcon}>
                    <FiAlertCircle className={styles.icon} />
                    <div className={styles.pulse}></div>
                </div>
                
                <h1 className={styles.title}>404</h1>
                <div className={styles.divider}></div>
                <h2 className={styles.subtitle}>Oops! Página não encontrada</h2>
                <p className={styles.description}>
                    Parece que o caminho que seguiu não existe ou foi movido para uma nova morada académica.
                </p>

                <button 
                    className={styles.backButton}
                    onClick={() => navigate('/')}
                >
                    <FiHome className={styles.btnIcon} />
                    Voltar ao Início
                </button>
            </div>

            {/* Elementos Decorativos Animados */}
            <div className={styles.decoration1}></div>
            <div className={styles.decoration2}></div>
            <div className={styles.decoration3}></div>
        </div>
    );
};

export default NotFound;
