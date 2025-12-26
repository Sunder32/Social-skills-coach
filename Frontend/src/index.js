import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import { HashRouter } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import App from './App';
import getTheme from './theme';
import './index.css';

function Root() {
  const [darkMode, setDarkMode] = useState(
    localStorage.getItem('darkMode') === 'true' || false
  );

  useEffect(() => {
    const handleThemeChange = (event) => {
      setDarkMode(event.detail);
    };

    window.addEventListener('themeChange', handleThemeChange);
    return () => window.removeEventListener('themeChange', handleThemeChange);
  }, []);

  return (
    <React.StrictMode>
      <HashRouter>
        <ThemeProvider theme={getTheme(darkMode ? 'dark' : 'light')}>
          <CssBaseline />
          <App />
        </ThemeProvider>
      </HashRouter>
    </React.StrictMode>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<Root />);
