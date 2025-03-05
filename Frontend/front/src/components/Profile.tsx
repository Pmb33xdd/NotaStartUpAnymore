import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const Profile: React.FC = () => {
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const [userData, setUserData] = useState<{ username: string; name: string; surname: string; email: string; subscriptions: string[]; sources: string[]; } | null>(null);
    const [showSubscriptionOptions, setShowSubscriptionOptions] = useState(false);
    const [showSourcesOptions, setShowSourcesOptions] = useState(false);
    const [selectedSources, setSelectedSources] = useState<string[]>([]);
    const [news, setNews] = useState<Array<{id: string; company: string; title: string; topic: string; details: string}>>([]);
    const [companies, setCompanies] = useState<Array<{id: string; name: string; type: string; details: string}>>([]);

    const sourcesOptions = [
        "El Economista",
        "Expansión",
        "Cinco Días",
        "Forbes",
        "Bloomberg",
        "Financial Times",
        "The Wall Street Journal",
        "Business Insider",
        "TechCrunch",
        "Reuters",
        "CNN Business"
    ];

    const navigate = useNavigate();

    const handleSubscriptionClick = async (subscription: string) => {
        try {
            const token = localStorage.getItem('token');
            console.log('Token:', token); 
            console.log('Subscription:', subscription); 
            if (!token) {
                navigate('/login');
                return;
            }

            const response = await fetch('http://localhost:8000/users/me', { 
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({ subscription, action: "add" }), 
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error al actualizar la suscripción');
            }

            setUserData(prevUserData => ({
                ...(prevUserData as any), 
                subscriptions: [...(prevUserData as any).subscriptions, subscription]
            }));

            setShowSubscriptionOptions(false); 

        } catch (error) {
            console.error('Error al actualizar la suscripción:', error);
        }
    };

    const handleSubscriptionRemove = async (subscription: string) => {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                navigate('/login');
                return;
            }

            const response = await fetch('http://localhost:8000/users/me', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({ subscription, action: "remove" }),  
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error al eliminar la suscripción');
            }

            setUserData(prevUserData => ({
                ...(prevUserData as any),
                subscriptions: (prevUserData as any).subscriptions.filter((s: string) => s !== subscription)
            }));

        } catch (error) {
            console.error('Error al eliminar la suscripción:', error);
        }
    };

    const handleSourceChange = async (source: string) => {
        setSelectedSources(prev => {
            const updatedSources = prev.includes(source) ? prev.filter(s => s !== source) : [...prev, source];
            updateUserSources(updatedSources); // Llamar a la función para actualizar en el backend
            return updatedSources;
        });
    };

    const updateUserSources = async (sources: string[]) => {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                navigate('/login');
                return;
            }

            const response = await fetch('http://localhost:8000/users/me/sources', { // Nueva ruta en el backend
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({ sources }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error al actualizar las fuentes');
            }

            setUserData(prevUserData => ({
                ...(prevUserData as any),
                sources: sources, // Actualizar el estado local con las fuentes actualizadas
            }));
        } catch (error) {
            console.error('Error al actualizar las fuentes:', error);
        }
    };



    useEffect(() => {
        const fetchUserData = async () => {
            try {
                const token = localStorage.getItem('token');
                if (!token) {
                    navigate('/login');
                    return;
                }

                const response = await fetch('http://localhost:8000/users/me', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`,
                    },
                });

                if (!response.ok) {
                    localStorage.removeItem('token');
                    navigate('/login');
                    return;
                }

                const userData = await response.json();
                setUserData(userData);
                if(userData && userData.sources){
                    setSelectedSources(userData.sources);
                }

            } catch (error) {
                console.error('Error al obtener los datos del usuario:', error);
                localStorage.removeItem('token');
                navigate('/login');
            }
        };

        const fetchNews = async () => {
            try{
                const response = await fetch ('http://localhost:8000/users/news');
                if(!response.ok){
                    throw new Error('Error al obtener las noticias')
                }

                const newsData = await response.json()
                setNews(newsData)
            } catch(error){
                console.error('Error al obtener las noticias')
            }

        };

        const fetchCompanies = async () =>{
            try{
                const response = await fetch('http://localhost:8000/users/companies');
                if(!response.ok){
                    throw new Error('Error al obtener las empresas')
                }

                const companiesData = await response.json()
                setCompanies(companiesData)
            } catch(error){
                console.error('Error al obtener las empresas')
            }
        }

        fetchCompanies();
        fetchNews();
        fetchUserData();
    }, [navigate]);

    const toggleDropdown = () => {
        setIsDropdownOpen(!isDropdownOpen);
    };

    const toggleSubscriptionOptions = () => {
        setShowSubscriptionOptions(!showSubscriptionOptions);
    };

    const toggleSourcesOptions = () => {
        setShowSourcesOptions(!showSourcesOptions);
    };

    if (!userData) {
        return <div>Cargando...</div>;
    }

    return (
        <div className="flex flex-col h-screen">
            <div className="bg-gray-100 p-4 flex justify-between items-center">
                <div className="relative">
                    <button onClick={toggleDropdown} className="flex items-center cursor-pointer">
                        <span className="material-symbols-outlined">Usuario: </span>
                        <span className="ml-2 font-bold">{userData?.username}</span> 
                    </button>
                    {isDropdownOpen && (
                        <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg left-8 z-10">
                            <a href="#" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Ajustes</a>
                            <a href="#" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Mi perfil</a>
                        </div>
                    )}
                </div>
            </div>

            <div className="flex-grow p-8 bg-gray-200">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 items-start">




                <div>
                <h3 className="font-bold mb-2 bg-white top-0 p-2 z-10">Mis suscripciones</h3>
                    <div className="bg-white p-4 rounded-md shadow-md max-h-64 h-64 overflow-y-auto relative">                       
                        {userData && userData.subscriptions && userData.subscriptions.length > 0 ? (
                            <ul className="list-disc pl-5">
                                {userData.subscriptions.map((subscription, index) => (
                                    <li key={index}>
                                        {subscription}
                                        <button onClick={() => handleSubscriptionRemove(subscription)} className="ml-2">
                                            <span className="text-red-500 hover:bg-gray-100 cursor-pointer">x</span> 
                                        </button>
                                    </li>
                                ))}
                            </ul>
                        ) : (
                            <p>No tienes suscripciones.</p>
                        )}
                        <button
                            className="bg-gray-200 hover:bg-gray-300 rounded-full h-8 w-8 flex items-center justify-center absolute bottom-2 right-2 cursor-pointer"
                            onClick={toggleSubscriptionOptions}
                        >
                            <span className="text-gray-600">+</span>
                        </button>

                        {showSubscriptionOptions && (
                            <div className="absolute bottom-10 right-0 bg-white rounded-md shadow-lg w-48 max-h-48 overflow-y-auto z-10">
                                <a className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer" onClick={() => handleSubscriptionClick('Creación de una nueva empresa')}>Creación de una nueva empresa</a>
                                <a className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer" onClick={() => handleSubscriptionClick('Contratación abundante de empleados por parte de una empresa')}>Contratación abundante de empleados por parte de una empresa</a>
                                <a className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer" onClick={() => handleSubscriptionClick('Cambio de sede de una empresa')}>Cambio de sede de una empresa</a>

                                {companies.map((company) => (
                                    <a key={company.id} className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer" onClick={() => handleSubscriptionClick(company.name)}>
                                        {company.name}
                                    </a>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
                
                <div>
                    <h3 className="font-bold mb-2 bg-white top-0 p-2 z-10">Notificaciones</h3>
                    <div className="bg-white p-4 rounded-md shadow-md max-h-64 h-64 overflow-y-auto relative">
                        

                    </div>             
                </div>

                <div>
                    <h3 className="font-bold mb-2 bg-white top-0 p-2 z-10">Noticias de interés</h3>
                        <div className="bg-white p-4 rounded-md shadow-md max-h-64 overflow-y-auto relative">
                            {(() => {
                                const filteredNews = news.filter(item => userData?.subscriptions.includes(item.topic) || userData?.subscriptions.includes(item.company)); // Filtrar noticias relevantes

                                return filteredNews.length > 0 ? (
                                    <ul className="list-disc pl-5">
                                        {filteredNews.map((newsItem) => (
                                            <li key={newsItem.id}>
                                                <div>
                                                    <p className="font-bold">{newsItem.title}</p>
                                                    <p className="text-gray-600 text-sm">Empresa: {newsItem.company}</p>
                                                    <p className="text-gray-600 text-sm">Detalles: {newsItem.details}</p>
                                                </div>
                                            </li>
                                        ))}
                                    </ul>
                                ) : (
                                    <p>No hay noticias de interés.</p> // Mostrar mensaje si no hay coincidencias con las suscripciones
                                );
                            })()}
                        </div>
                </div>

                    
                <div>
                    <h3 className="font-bold mb-2 bg-white top-0 p-2 z-10">Fuentes de Información</h3>
                    <div className="bg-white p-4 rounded-md shadow-md max-h-64 h-64 overflow-y-auto relative">

                        <button onClick={toggleSourcesOptions} className="bg-gray-200 hover:bg-gray-300 rounded-md px-4 py-2 w-full text-left">

                            {showSourcesOptions ? "Cerrar Fuentes" : "Seleccionar Fuentes"}
                        </button>

                        {showSourcesOptions && (
                            <div className="absolute top-12 left-0 bg-white border rounded-md shadow-lg w-64 p-2 max-h-48 overflow-y-auto z-10">
                                {sourcesOptions.map((source, index) => (
                                    <label key={index} className="flex items-center px-2 py-1 cursor-pointer hover:bg-gray-100">
                                        <input type ="checkbox" 
                                               checked={selectedSources.includes(source)} 
                                               onChange={() => handleSourceChange(source)}
                                               className="mr-2"
                                        />
                                        {source}
                                    </label>
                                ))}
                            </div>
                        )}

                        {selectedSources.length > 0 && (
                            <div className="mt-4">
                                <p className="font-semibold">Fuentes seleccionadas:</p>
                                <ul className="list-disc pl-5">
                                    {selectedSources.map((source, index) => (
                                        <li key={index}>{source}</li>
                                    ))}
                                </ul>
                            </div>
                        )}
                        
                    </div>
                </div>

                </div>
            </div>
        </div>
    );
};

export default Profile;