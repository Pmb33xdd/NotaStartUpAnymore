import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './auth_context';
import { API_KEY, LOGIN_URL } from '../urls';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError('');

    try {
      const response = await fetch(LOGIN_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'access_token': API_KEY,
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al iniciar sesión');
      }

      const data = await response.json();

      localStorage.setItem('token', data.access_token);
      login({ username: data.username || email });
      navigate('/profile');
    } catch (error: any) {
      console.error('Error:', error);
      setError(error.message);
    }
  };

  return (
    <div className="flex min-h-screen">

      <div className="hidden lg:block lg:w-1/2 bg-[url('/images/Imagen_login1.jpg')] bg-cover bg-center" />

      <div className="flex flex-1 justify-center items-center bg-green-100 p-8">
        <div className="bg-white p-10 rounded-lg shadow-lg max-w-md w-full">
          <h2 className="text-3xl font-bold mb-6 text-center text-gray-800">
            Iniciar Sesión
          </h2>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label
                htmlFor="email"
                className="block text-gray-700 font-semibold mb-2"
              >
                Correo electrónico:
              </label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label
                htmlFor="password"
                className="block text-gray-700 font-semibold mb-2"
              >
                Contraseña:
              </label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            {error && (
              <p className="text-red-600 text-center font-semibold">{error}</p>
            )}

            <button
              type="submit"
              className="w-full bg-purple-900 hover:bg-yellow-500 text-white font-bold py-3 rounded transition-colors duration-300"
            >
              Iniciar Sesión
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;
