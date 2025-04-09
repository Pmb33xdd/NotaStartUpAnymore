import React, { useState } from 'react';
// import { useNavigate } from 'react-router-dom';

const Register: React.FC = () => {
    const [username, setUsername] = useState('');
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);
//    const navigate = useNavigate(); // Crea una instancia de useNavigate

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setError('');
        setSuccess(false);

        if (password !== confirmPassword) {
            setError('Las contraseñas no coinciden');
            return;
        }

        try {
            const response = await fetch('https://notastartupanymore.onrender.com/users/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
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

            // Redirige al inicio de sesión
            //navigate('/login');

        } catch (error: any) {
            console.error('Error:', error);
            setError(error.message);
        }
    };

    return (
        <div className="flex h-screen">
            <div className="w-1/2 bg-[url('/images/Imagen_login2.jpg')] bg-cover bg-no-repeat">
                {/* Puedes agregar contenido adicional aquí si lo deseas */}
            </div>
            <div className="w-1/2 flex justify-center items-center bg-green-100">
                <div className="bg-white p-4 rounded-lg shadow-md w-80 h-fit">
                    <h2 className="text-xl font-bold mb-2 text-center">Registrarse</h2>
                    <form onSubmit={handleSubmit}>
                        <div className="mb-2">
                            <label htmlFor="username" className="block text-gray-700 font-bold mb-1 text-sm">
                                Nombre de Usuario:
                            </label>
                            <input
                                type="text"
                                id="username"
                                value={username}
                                onChange={(event) => setUsername(event.target.value)}
                                className="border border-gray-300 rounded px-2 py-1 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                                required
                            />
                        </div>

                        <div className="mb-2">
                            <label htmlFor="firstName" className="block text-gray-700 font-bold mb-1 text-sm">
                                Nombre:
                            </label>
                            <input
                                type="text"
                                id="firstName"
                                value={firstName}
                                onChange={(event) => setFirstName(event.target.value)}
                                className="border border-gray-300 rounded px-2 py-1 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                                required
                            />
                        </div>

                        <div className="mb-2">
                            <label htmlFor="lastName" className="block text-gray-700 font-bold mb-1 text-sm">
                                Apellido:
                            </label>
                            <input
                                type="text"
                                id="lastName"
                                value={lastName}
                                onChange={(event) => setLastName(event.target.value)}
                                className="border border-gray-300 rounded px-2 py-1 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                                required
                            />
                        </div>

                        <div className="mb-2">
                            <label htmlFor="email" className="block text-gray-700 font-bold mb-1 text-sm">
                                Correo electrónico:
                            </label>
                            <input
                                type="email"
                                id="email"
                                value={email}
                                onChange={(event) => setEmail(event.target.value)}
                                className="border border-gray-300 rounded px-2 py-1 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                                required
                            />
                        </div>

                        <div className="mb-2">
                            <label htmlFor="password" className="block text-gray-700 font-bold mb-1 text-sm">
                                Contraseña:
                            </label>
                            <input
                                type="password"
                                id="password"
                                value={password}
                                onChange={(event) => setPassword(event.target.value)}
                                className="border border-gray-300 rounded px-2 py-1 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                                required
                                minLength={6}
                            />
                        </div>

                        <div className="mb-4">
                            <label htmlFor="confirmPassword" className="block text-gray-700 font-bold mb-1 text-sm">
                                Confirmar Contraseña:
                            </label>
                            <input
                                type="password"
                                id="confirmPassword"
                                value={confirmPassword}
                                onChange={(event) => setConfirmPassword(event.target.value)}
                                className="border border-gray-300 rounded px-2 py-1 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                                required
                            />
                        </div>

                        {error && <p className="text-red-500 mt-2 text-sm">{error}</p>}
                        {success && <p className="text-green-500 mt-2 text-sm">Verifica tu correo para completar el registro</p>}

                        <button
                            type="submit"
                            className="bg-purple-800 hover:bg-yellow-500 text-white font-bold py-2 px-4 rounded w-full focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
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