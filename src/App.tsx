import React, { useState } from 'react';
import { ThemeProvider } from 'styled-components';
import GlobalStyle from './GlobalStyle';
import { lightTheme, darkTheme } from './theme';
import MainLayout from './components/MainLayout';
import RegistrationForm from './components/RegistrationForm';
import LoginForm from './components/LoginForm';
import Header from './components/Header';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';

const App: React.FC = () => {
  const [theme, setTheme] = useState(lightTheme);

  const toggleTheme = () => {
    setTheme(theme === lightTheme ? darkTheme : lightTheme);
  };

  return (
    <ThemeProvider theme={theme}>
      <GlobalStyle />
      <Router>
        <Header toggleTheme={toggleTheme} />
        <Routes>
          <Route path="/" element={<MainLayout />} />
          <Route path="/register" element={<RegistrationForm />} />
          <Route path="/login" element={<LoginForm />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
};

export default App;
