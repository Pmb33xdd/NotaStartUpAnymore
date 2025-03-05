import React, { useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';

const Home: React.FC = () => {
    const queHacemosRef = useRef<HTMLDivElement>(null);
    const contactanosRef = useRef<HTMLDivElement>(null);
    const location = useLocation();

    // Detecta si hay un hash en la URL y hace scroll a la sección correspondiente
    useEffect(() => {
        if (location.hash === '#que-hacemos' && queHacemosRef.current) {
            queHacemosRef.current.scrollIntoView({ behavior: 'smooth' });
        } else if (location.hash === '#contactanos' && contactanosRef.current) {
            contactanosRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [location]);

    return (
        <div className="relative w-screen h-screen overflow-y-auto">
            <div className="relative w-full h-screen">
                <video autoPlay muted loop className="absolute top-0 left-0 w-full h-full object-cover">
                    <source src="/videos/Startup_video.mp4" type="video/mp4" />
                    Tu navegador no soporta la reproducción de videos.
                </video>

                <div className="absolute top-0 left-0 w-full h-full z-10 flex flex-col items-center justify-center text-white text-center p-4">
                    <h1 className="text-5xl font-bold mt-20 drop-shadow-lg">
                        Bienvenido a NotAStartUpAnymore!!!
                    </h1>
                </div>
            </div>

            {/* Sección ¿Qué Hacemos? */}
            <section ref={queHacemosRef} id="que-hacemos" className="bg-gray-100 py-12 px-4">
                <h2 className="text-4xl font-bold text-center mb-6">¿Qué hacemos?</h2>
                <div className="container mx-auto">
                    <div className="bg-white p-8 rounded-lg shadow-md">
                        <p>
                            En <strong>NotAStartUpAnymore</strong>, te ofrecemos información precisa y actualizada sobre las empresas que están transformando el panorama empresarial.
                        </p>
                        <p>
                            A través de <strong>web scraping</strong> y <strong>modelos de lenguaje</strong>, identificamos empresas de nueva creación con más de 400 empleados, crecimiento superlativo o que hayan cambiado su sede.
                        </p>
                    </div>

                    <div className="container mx-auto py-12">
                        <div className="flex justify-center">
                            <div className="w-1/2 px-4">
                                <img src="/images/que_hacemos.jpg" alt="Imagen 1" className="rounded-lg shadow-md ml-60" />
                            </div>
                            <div className="w-1/2 px-4">
                                <img src="/images/ivestigar.jpg" alt="Imagen 1" className="rounded-lg shadow-md ml-40" />
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Sección Contáctanos */}
            <section ref={contactanosRef} id="contactanos" className="bg-white py-12 px-4">
                <h2 className="text-4xl font-bold text-center mb-6">Contáctanos</h2>
                <div className="container mx-auto">
                    <div className="bg-gray-100 p-8 rounded-lg shadow-md">
                        <p>
                            ¿Quieres saber más sobre cómo podemos ayudarte a identificar a las empresas que están marcando la diferencia? ¡Contáctanos y descubre el poder de la información!
                        </p>
                    </div>
                </div>
            </section>
        </div>
    );
};

export default Home;
