import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from './auth_context';
import { Menu, X } from 'lucide-react';

const Navbar: React.FC = () => {
  const { isLoggedIn, username, logout } = useAuth();
  const location = useLocation();
  const isHomePage = location.pathname === '/';

  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <nav className="bg-purple-800 text-white p-4">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center md:justify-between">
        <div className="flex items-center justify-between md:justify-start md:w-1/3">
          <button
            className="md:hidden"
            onClick={() => setMenuOpen(!menuOpen)}
          >
            {menuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>

          <div className="hidden md:flex md:space-x-4 ml-4">
            <Link to="/" className="hover:text-gray-300">Inicio</Link>
            {isHomePage && (
              <>
                <Link to="#que-hacemos" className="hover:text-gray-300">¿Qué Hacemos?</Link>
                <Link to="#contactanos" className="hover:text-gray-300">Contáctanos</Link>
              </>
            )}
          </div>
        </div>

        <div className="text-xl font-bold text-center md:w-1/3">
          NotAStartUpAnymore
        </div>

        <div className="mt-4 md:mt-0 flex flex-col md:flex-row md:items-center md:justify-end md:w-1/3 space-y-2 md:space-y-0 md:space-x-4">
          {isLoggedIn ? (
            <>
              <Link to="/profile" className="flex items-center hover:text-gray-300">
                <img src="/images/perfil2.jpg" alt="Perfil" className="h-8 w-8 rounded-full mr-2" />
                {username}
              </Link>
              <button
                onClick={logout}
                className="bg-red-500 hover:bg-red-700 px-4 py-2 rounded-md"
              >
                Cerrar Sesión
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="bg-white text-black px-4 py-2 rounded-md text-center">
                Iniciar Sesión
              </Link>
              <Link to="/register" className="bg-yellow-400 text-black px-4 py-2 rounded-md text-center">
                Registrarse
              </Link>
            </>
          )}
        </div>

        {menuOpen && (
          <div className="md:hidden mt-4 space-y-2">
            <Link to="/" className="block hover:text-gray-300">Inicio</Link>
            {isHomePage && (
              <>
                <Link to="#que-hacemos" className="block hover:text-gray-300">¿Qué Hacemos?</Link>
                <Link to="#contactanos" className="block hover:text-gray-300">Contáctanos</Link>
              </>
            )}
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
