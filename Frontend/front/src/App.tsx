import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Login from './components/Login';
import Register from './components/Register';
import Home from './components/Home';
import Profile from './components/Profile';
import './App.css';
import { AuthProvider } from './components/auth_context';

const App: React.FC = () => {
  return (
    <Router>
      <AuthProvider>
      <div className="flex flex-col min-h-screen"> {/* Asegura que el div ocupa al menos toda la pantalla */}
        <Navbar />
        <main className="flex-grow"> {/* main ocupa el espacio restante */}
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/profile" element={<Profile />} />
          </Routes>
        </main>
      </div>
      </AuthProvider>
    </Router>
  );
};

export default App;