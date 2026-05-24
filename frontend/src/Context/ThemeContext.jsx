import React, { useState, useEffect } from 'react';
import { ThemeContext } from './ThemeContextData';
import { useLocation } from 'react-router-dom';

export const ThemeProvider = ({ children }) => {
    const location = useLocation();

    // Check localStorage or system preference
    const [theme, setTheme] = useState(() => {
        // Modo Light forçado globalmente.
        // A lógica de dark mode foi removida conforme decisão de design premium-light.
        return 'light';
    });

    useEffect(() => {
        localStorage.setItem('site-theme', theme);
        // Ensure dark-mode class is always removed if it somehow got added.
        document.body.classList.remove('dark-mode');
    }, [theme, location.pathname]);

    const toggleTheme = () => {
        setTheme(prev => prev === 'light' ? 'dark' : 'light');
    };

    return (
        <ThemeContext.Provider value={{ theme, toggleTheme }}>
            {children}
        </ThemeContext.Provider>
    );
};


