import React, { useState } from 'react';
import { API_KEY, REGISTER_URL } from '../urls';

const Register: React.FC = () => {
  const nombreExpressionRegex = /^[a-z0-9_]+$/;
  const patternComprobation = /(select|insert|delete|update|drop|--|'|"|;)/i;

  const [username, setUsername] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError('');
    setSuccess(false);

    if (password !== confirmPassword) {
      setError('Las contraseñas no coinciden');
      return;
    }

    if (!nombreExpressionRegex.test(username)) {
      setError('El nombre de usuario solo puede contener letras minúsculas, números y guiones bajos');
      return;
    }

    if (patternComprobation.test(username) || patternComprobation.test(firstName) || patternComprobation.test(lastName)) {
      setError('El nombre de usuario, nombre o apellido no puede contener palabras reservadas o caracteres especiales');
      return;
    }

    try {
      const response = await fetch(REGISTER_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'access_token': API_KEY,
        },
        body: JSON.stringify({
          username,
          name: firstName,
          surname: lastName,
          email,
          password,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al registrar usuario');
      }

      setSuccess(true);
      setUsername('');
      setFirstName('');
      setLastName('');
      setEmail('');
      setPassword('');
      setConfirmPassword('');
    } catch (error: any) {
      console.error('Error:', error);
      setError(error.message);
    }
  };

  return (
    <div className="flex min-h-screen">

      <div className="hidden lg:block lg:w-1/2 bg-[url('/images/Imagen_login2.jpg')] bg-cover bg-center" />

      <div className="flex flex-1 justify-center items-center bg-green-100 p-8">
        <div className="bg-white p-10 rounded-lg shadow-lg max-w-md w-full">
          <h2 className="text-3xl font-bold mb-6 text-center text-gray-800">
            Registrarse
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4 text-sm">
            <div>
              <label htmlFor="username" className="block font-semibold mb-1 text-gray-700">
                Nombre de Usuario:
              </label>
              <input
                type="text"
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label htmlFor="firstName" className="block font-semibold mb-1 text-gray-700">
                Nombre:
              </label>
              <input
                type="text"
                id="firstName"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label htmlFor="lastName" className="block font-semibold mb-1 text-gray-700">
                Apellido:
              </label>
              <input
                type="text"
                id="lastName"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label htmlFor="email" className="block font-semibold mb-1 text-gray-700">
                Correo electrónico:
              </label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label htmlFor="password" className="block font-semibold mb-1 text-gray-700">
                Contraseña:
              </label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
                minLength={6}
              />
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block font-semibold mb-1 text-gray-700">
                Confirmar Contraseña:
              </label>
              <input
                type="password"
                id="confirmPassword"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            {error && <p className="text-red-600 font-semibold text-center">{error}</p>}
            {success && (
              <p className="text-green-600 font-semibold text-center">
                ¡Registro exitoso! Verifica tu correo para completar el registro.
              </p>
            )}

            <button
              type="submit"
              className="w-full bg-purple-900 hover:bg-yellow-500 text-white font-bold py-3 rounded transition-colors duration-300"
            >
              Registrarse
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Register;
