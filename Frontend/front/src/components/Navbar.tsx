import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from './auth_context';

const Navbar: React.FC = () => {
    const { isLoggedIn, username, logout } = useAuth();
    const location = useLocation();
    const isHomePage = location.pathname === '/';

    return (
        <nav className="bg-purple-800 text-white p-4 flex items-center justify-between">
            <div className="flex items-center">
                <Link to="/" className="text-white px-4 py-2 rounded-md mr-2">
                    Inicio
                </Link>
                {isHomePage && (
                    <>
                        <Link to="#que-hacemos" className="text-white px-4 py-2 rounded-md mr-2">
                            ¿Qué Hacemos?
                        </Link>
                        <Link to="#contactanos" className="text-white px-4 py-2 rounded-md">
                            Contáctanos
                        </Link>
                    </>
                )}
            </div>

            <div>
                <h1 className="text-2xl font-bold">NotAStartUpAnymore</h1>
            </div>

            <div className="flex items-center">
                {isLoggedIn ? (
                    <div className="flex items-center space-x-4">
                        <Link to="/profile" className="text-white hover:text-gray-300">
                            <img src="/images/perfil2.jpg" alt="Imagen de perfil" className="h-8 w-8 ml-4 rounded-full" /> {username}
                        </Link>
                        <button onClick={logout} className="bg-red-500 hover:bg-red-700 text-white px-4 py-2 rounded-md">
                            Cerrar Sesión
                        </button>
                    </div>
                ) : (
                    <div className="space-x-4">
                        <Link to="/login" className="bg-white text-black px-4 py-2 rounded-md mr-2">
                            Iniciar Sesión
                        </Link>
                        <Link to="/register" className="bg-yellow-400 text-black px-4 py-2 rounded-md">
                            Registrarse
                        </Link>
                    </div>
                )}
            </div>
        </nav>
    );
};

export default Navbar;
