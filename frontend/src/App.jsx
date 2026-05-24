import React from 'react';
import './assets/style/global.style.css';
import Routers from "./Router";
import { ThemeProvider } from './Context/ThemeContext.jsx';
import { AuthProvider } from './Context/AuthContext.jsx';

import { BrowserRouter as BRouter } from 'react-router-dom';

function App() {
  return (
    <BRouter>
      <ThemeProvider>
        <AuthProvider>
          <Routers />
        </AuthProvider>
      </ThemeProvider>
    </BRouter>
  )
}

export default App
