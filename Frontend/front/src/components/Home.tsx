import React, { useEffect, useRef, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { API_KEY, ENVIAR_CORREO_CONTACTANOS_URL } from "../urls";

const Home: React.FC = () => {
    const queHacemosRef = useRef<HTMLDivElement>(null);
    const contactanosRef = useRef<HTMLDivElement>(null);
    const location = useLocation();

    const [formData, setFormData] = useState({ name: "", mail: "", message: "" });
    const [loading, setLoading] = useState(false);
    const [response, setResponse] = useState("");

    useEffect(() => {
        if (location.hash === "#que-hacemos" && queHacemosRef.current) {
            queHacemosRef.current.scrollIntoView({ behavior: "smooth" });
        } else if (location.hash === "#contactanos" && contactanosRef.current) {
            contactanosRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [location]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setResponse("");

        if (!formData.name.trim() || !formData.mail.trim() || !formData.message.trim()) {
            setResponse("Todos los campos son obligatorios.");
            return;
        }

        setLoading(true);

        try {
            const res = await fetch(ENVIAR_CORREO_CONTACTANOS_URL, {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    "access_token": API_KEY,
                },
                body: JSON.stringify(formData),
            });

            const data = await res.json();
            if (res.ok) {
                setResponse("Mensaje enviado correctamente");
                setFormData({ name: "", mail: "", message: "" });
            } else {
                setResponse(`Error: ${data.detail}`);
            }
        } catch (error) {
            setResponse("Error al enviar el mensaje. Inténtalo de nuevo.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="relative w-full overflow-y-auto font-sans bg-purple-100 min-h-screen">
            <div className="relative w-full h-screen">
                <video autoPlay muted loop className="absolute top-0 left-0 w-full h-full object-cover brightness-75">
                    <source src="/videos/Startup_video.mp4" type="video/mp4" />
                    Tu navegador no soporta la reproducción de videos.
                </video>

                <div className="absolute top-0 left-0 w-full h-full z-10 flex flex-col mt-20 items-center justify-center text-white text-center p-4">
                    <h1 className="text-5xl font-extrabold drop-shadow-lg animate-fade-in">
                        Bienvenido a NotAStartUpAnymore!!!
                    </h1>

                    <p className="mt-4 text-lg max-w-xl">
                        Encuentra información clave sobre empresas en crecimiento y cambios estratégicos.
                    </p>

                    <Link to="#que-hacemos" className="mt-6 bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg shadow-md transition-transform transform hover:scale-105">
                        Descubre más
                    </Link>
                </div>
            </div>

            <section ref={queHacemosRef} id="que-hacemos" className="py-16 px-6 max-w-7xl mx-auto">
                <h2 className="text-4xl font-bold text-center mb-8 text-gray-800">¿Qué hacemos?</h2>
                <div className="grid md:grid-cols-2 gap-8 items-center">
                    <div className="p-8 rounded-lg shadow-lg bg-purple-100">
                        <p className="text-lg text-gray-700">
                            En <strong>NotAStartUpAnymore</strong>, te ofrecemos información precisa y actualizada sobre las empresas que están transformando el panorama empresarial.
                        </p>
                        <p className="mt-4 text-lg text-gray-700">
                            A través de <strong>web scraping</strong> y <strong>modelos de lenguaje</strong>, identificamos empresas de nueva creación con más de 400 empleados, crecimiento superlativo o que hayan cambiado su sede.
                        </p>
                    </div>

                    <div className="flex space-x-4">
                        <img src="/images/que_hacemos.jpg" alt="Investigación" className="w-1/2 rounded-lg shadow-lg" />
                        <img src="/images/ivestigar.jpg" alt="Análisis" className="w-1/2 rounded-lg shadow-lg" />
                    </div>
                </div>
            </section>

            <section ref={contactanosRef} id="contactanos" className="py-16 px-6 max-w-md mx-auto">
                <h2 className="text-4xl font-bold text-center mb-8 text-gray-800">Contáctanos</h2>
                <div className="p-8 rounded-lg shadow-lg bg-purple-100">
                    <div className="text-lg text-gray-700 text-center mb-6">
                        <p>
                            ¿Quieres saber más sobre cómo podemos ayudarte a identificar a las empresas que están marcando la diferencia? ¡Contáctanos y descubre el poder de la información!
                        </p>
                        <form className="space-y-4" onSubmit={handleSubmit}>
                            <input type="text" name="name" placeholder="Tu nombre" value={formData.name} onChange={handleChange} className="w-full p-3 border border-gray-300 rounded-lg" />
                            <input type="email" name="mail" placeholder="Tu correo" value={formData.mail} onChange={handleChange} className="w-full p-3 border border-gray-300 rounded-lg" />
                            <textarea name="message" placeholder="Tu mensaje" value={formData.message} onChange={handleChange} className="w-full p-3 border border-gray-300 rounded-lg h-32"></textarea>
                            <button type="submit" className="w-full bg-blue-500 hover:bg-blue-600 text-white py-3 rounded-lg shadow-md transition-transform transform hover:scale-105" disabled={loading}>
                                {loading ? "Enviando..." : "Enviar mensaje"}
                            </button>
                        </form>
                        {response && <p className="mt-4 text-center text-gray-700">{response}</p>}
                    </div>
                </div>
            </section>

            <footer className="w-full">
                <img src="/images/Logo_Nombre_Proyecto.png" alt="Footer completo" className="w-full h-screen bg-purple-100 object-cover" />
            </footer>
        </div>
    );
};

export default Home;
