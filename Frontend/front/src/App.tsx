import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import Home from './components/Home';
import Profile from './components/Profile';
import VerifyAccount from './components/VerifyAccount';
import { AuthProvider } from './components/auth_context';
import DefaultLayout from './layouts/DefaultLayout';
import NoNavbarLayout from './layouts/NoNavbarLayout';

const App: React.FC = () => {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/" element={
              <DefaultLayout>
                <Home />
              </DefaultLayout>
            }
          />
          <Route path="/login" element={
              <DefaultLayout>
                <Login />
              </DefaultLayout>
            }
          />
          <Route path="/register" element={
              <DefaultLayout>
                <Register />
              </DefaultLayout>
            }
          />
          <Route path="/profile" element={
              <DefaultLayout>
                <Profile />
              </DefaultLayout>
            }
          />
          <Route path="/verify" element={
              <NoNavbarLayout>
                <VerifyAccount />
              </NoNavbarLayout>
            }
          />
        </Routes>
      </AuthProvider>
    </Router>
  );
};

export default App;
