import React, { createContext, useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_KEY, DATOS_DE_USUARIO_URL } from '../urls';

interface AuthContextType {
    isLoggedIn: boolean;
    username: string;
    login: (userData: { username: string }) => void;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
    isLoggedIn: false,
    username: '',
    login: () => {},
    logout: () => {}
});

export const AuthProvider: React.FC<{ children?: React.ReactNode }> = ({ children }) => {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [username, setUsername] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        const checkAuth = async () => {
            const token = localStorage.getItem('token');
            if (token) {
                try {
                    const response = await fetch(DATOS_DE_USUARIO_URL, {
                        headers: {
                            'Authorization': `Bearer ${token}`,
                            'access_token': API_KEY,
                        }
                    });

                    if (response.ok) {
                        const data = await response.json();
                        setIsLoggedIn(true);
                        setUsername(data.username);
                    } else if (response.status === 401) {
                        localStorage.removeItem('token');
                        setIsLoggedIn(false);
                        setUsername('');
                        navigate('/login');
                    } else {
                        console.error('Error en la solicitud:', response.status);
                        localStorage.removeItem('token');
                        setIsLoggedIn(false);
                        setUsername('');
                        navigate('/login');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    localStorage.removeItem('token');
                    setIsLoggedIn(false);
                    setUsername('');
                    navigate('/login');
                }
            } else {
                setIsLoggedIn(false);
                setUsername('');
            }
        };

        checkAuth();
    }, [username]);

    const login = (userData: { username: string }) => {
        setIsLoggedIn(true);
        setUsername(userData.username);
    };

    const logout = () => {
        localStorage.removeItem('token');
        setIsLoggedIn(false);
        setUsername('');
        navigate('/login');
    };

    const value = { isLoggedIn, username, login, logout };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);

export default AuthContext;