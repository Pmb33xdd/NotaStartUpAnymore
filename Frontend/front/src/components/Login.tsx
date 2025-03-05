import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './auth_context'; // Asegúrate de que la ruta sea correcta

const Login: React.FC = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const { login } = useAuth(); // Accede a la función login del contexto

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setError('');
    
        try {
            const response = await fetch('http://localhost:8000/users/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            });
    
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error al iniciar sesión');
            }
    
            // Analiza la respuesta como JSON
            const data = await response.json(); 
    
            console.log('Inicio de sesión exitoso');
            localStorage.setItem('token', data.access_token); // Accede al token desde data

            // Llama a la función login del contexto con el nombre de usuario o email
            login({ username: data.username || email });

            // Redirige al perfil
            navigate('/profile');

        } catch (error: any) {
            console.error('Error:', error);
            setError(error.message);
        }
    };

    return (
        <div className="flex h-screen">
            <div className="w-1/2 bg-[url('/images/Imagen_login1.jpg')] bg-cover bg-no-repeat">
                {/* Puedes agregar contenido adicional aquí si lo deseas */}
            </div>
            <div className="w-1/2 flex justify-center items-center bg-green-100">
                <div className="bg-white p-8 rounded-lg shadow-md w-96">
                    <h2 className="text-2xl font-bold mb-4 text-center">Iniciar Sesión</h2>
                    <form onSubmit={handleSubmit}>
                        <div className="mb-4">
                            <label htmlFor="email" className="block text-gray-700 font-bold mb-2">
                                Correo electrónico:
                            </label>
                            <input
                                type="email"
                                id="email"
                                value={email}
                                onChange={(event) => setEmail(event.target.value)}
                                className="border border-gray-300 rounded px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
                                required
                            />
                        </div>

                        <div className="mb-6">
                            <label htmlFor="password" className="block text-gray-700 font-bold mb-2">
                                Contraseña:
                            </label>
                            <input
                                type="password"
                                id="password"
                                value={password}
                                onChange={(event) => setPassword(event.target.value)}
                                className="border border-gray-300 rounded px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
                                required
                            />
                        </div>

                        {error && <p className="text-red-500 mt-2">{error}</p>}

                        <button
                            type="submit"
                            className="bg-purple-900 hover:bg-yellow-500 text-white font-bold py-2 px-4 rounded w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
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