import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { VERIFY_EMAIL_URL } from '../urls';

const VerifyAccount: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [verified, setVerified] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [show, setShow] = useState(false);
  const navigate = useNavigate();

  const token = searchParams.get('token');

  useEffect(() => {
    const timer = setTimeout(() => setShow(true), 100);
    return () => clearTimeout(timer);
  }, []);

  const handleVerify = async () => {

    if (!token) {
    setError('Token no proporcionado');
    return;
    }
    
    try {
      const response = await fetch(VERIFY_EMAIL_URL(token));

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al verificar.');
      }

      setVerified(true);
    } catch (err: any) {
      setError(err.message || 'Error desconocido');
    }
  };

  const handleGoToLogin = () => {
    navigate('/login');
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-blue-100">
      <div
        className={`p-8 max-w-lg w-full bg-white rounded-2xl shadow-xl transform transition-all duration-700 ease-out
          ${show ? 'opacity-100 scale-100' : 'opacity-0 scale-90'}`}
      >
        <h1 className="text-2xl font-bold mb-6 text-center">Verificar cuenta</h1>
        {verified ? (
          <>
            <p className="text-green-600 text-center text-lg mb-6">✅ ¡Tu cuenta ha sido verificada con éxito!</p>
            <div className="flex justify-center">
              <button
                className="px-6 py-3 bg-green-600 text-white text-sm font-semibold rounded-lg hover:bg-green-700 transition"
                onClick={handleGoToLogin}
              >
                ¿Inicia sesión YA!
              </button>
            </div>
          </>
        ) : error ? (
          <p className="text-red-500 text-center text-lg">❌ {error}</p>
        ) : (
          <>
            <p className="mb-6 text-center">Haz clic en el siguiente botón para verificar tu cuenta:</p>
            <h2 className="text-xl font-semibold text-blue-700 text-center mb-4">
              ✅ Verifica tu cuenta para empezar a buscar noticias de interés
            </h2>
            <div className="flex justify-center">
              <button
                className="px-6 py-3 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 transition"
                onClick={handleVerify}
              >
                Verificar cuenta
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default VerifyAccount;
