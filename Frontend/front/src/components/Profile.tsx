import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import DataSelection from './DataSelection';
import ChartEvaluation from './Chart_Evaluation';
import SettingsModal from './SettingsModal';
import ReportGenerator from './ReportGenerator';
import { API_KEY, COMPANIES_URL, DATOS_DE_USUARIO_URL, DATOS_GRAFICOS_URL, DELETE_URL, FILTROS_FETCH_URL, FILTROS_URL, NEWS_URL, REPORT_URL } from '../urls';

type NewsItem = { id: string; company: string; title: string; topic: string; details: string }
type CompaniesItem = { id: string; name: string; type: string; details: string }
type UserItem = { id: string, username: string; name: string; surname: string; email: string; subscriptions: string[]; filters: string[] }
type DataChart = { label: string; value: number }

interface ReportFormData {
    fechaInicio: string;
    fechaFin: string;
    tipoCreacion: boolean;
    tipoCambioSede: boolean;
    tipoCrecimiento: boolean;
    tipoOtras: boolean;
    incluirGraficos: boolean;
    mail: string;
    message: string;
}

const Profile: React.FC = () => {
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const [userData, setUserData] = useState<UserItem | null>(null);
    const [showSubscriptionOptions, setShowSubscriptionOptions] = useState(false);
    const [showFiltersOptions, setShowFiltersOptions] = useState(false);
    const [selectedFilters, setSelectedFilters] = useState<string[]>([]);
    const [news, setNews] = useState<NewsItem[]>([]);
    const [companies, setCompanies] = useState<CompaniesItem[]>([]);
    const [companyTypes, setCompanyTypes] = useState<string[]>([]);
    const [selectedCompanyType, setSelectedCompanyType] = useState<string | null>(null);
    const [chartData, setChartData] = useState<DataChart[]>([]);
    const [FiltersOptions, setFiltersOptions] = useState<string[]>([]);
    const [isSettingsModalOpen, setIsSettingsModalOpen] = useState(false);

    const navigate = useNavigate();

    const handleSubscriptionClick = async (subscription: string) => {

        try {
            const token = localStorage.getItem('token');
            if (!token) {
                navigate('/login');
                return;
            }
            const response = await fetch(DATOS_DE_USUARIO_URL, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                    'access_token': API_KEY,
                },
                body: JSON.stringify({ subscription, action: "add" }),
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error al actualizar la suscripción');
            }
            setUserData(prevUserData => {
                if (!prevUserData) return null;
                const currentSubscriptions = prevUserData.subscriptions || [];
                if (!currentSubscriptions.includes(subscription)) {
                    return {
                        ...prevUserData,
                        subscriptions: [...currentSubscriptions, subscription]
                    };
                }
                return prevUserData;
            });
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
            const response = await fetch(DATOS_DE_USUARIO_URL, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                    'access_token': API_KEY,
                },
                body: JSON.stringify({ subscription, action: "remove" }),
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error al eliminar la suscripción');
            }
            setUserData(prevUserData => ({
                ...(prevUserData as UserItem),
                subscriptions: (prevUserData as UserItem).subscriptions.filter((s: string) => s !== subscription)
            }));
        } catch (error) {
            console.error('Error al eliminar la suscripción:', error);
        }
    };

    const handleFilterChange = async (filter: string) => {
        setSelectedFilters(prev => {
            const updatedFilters = prev.includes(filter) ? prev.filter(s => s !== filter) : [...prev, filter];
            updateUserFilters(updatedFilters);
            return updatedFilters;
        });
    };

    const updateUserFilters = async (filters: string[]) => {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                navigate('/login');
                return;
            }
            const response = await fetch(FILTROS_URL, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                    'access_token': API_KEY,
                },
                body: JSON.stringify({ filters }),
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error al actualizar los filtros');
            }
            setUserData(prevUserData => ({
                ...(prevUserData as UserItem),
                filters: filters,
            }));
        } catch (error) {
            console.error('Error al actualizar los filtros:', error);
        }
    };

    const handleGenerateChart = async (params: Record<string, string>) => {
        try {
            const url = DATOS_GRAFICOS_URL(params);
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'access_token': API_KEY,
                },
            });
            if (!response.ok) {
                console.error('Error en la respuesta del backend:', response);
                throw new Error('Error al obtener los datos del gráfico');
            }
            const data: DataChart[] = await response.json();
            setChartData(data);
        } catch (error) {
            console.error('Error al generar el gráfico:', error);
        }
    };

    const handleDeleteAccount = async () => {
        if (window.confirm('¿Estás seguro de que quieres eliminar tu cuenta? Esta acción no se puede deshacer.')) {
            try {
                const token = localStorage.getItem('token');
                const userID = userData?.id; // Asegúrate de tener `userData.id` disponible
                if (!token || !userID) {
                    navigate('/login');
                    return;
                }
                
                const response = await fetch(DELETE_URL(userID), {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'access_token': API_KEY,
                    },
                });
    
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Error al eliminar la cuenta');
                }
    
                localStorage.removeItem('token');
                navigate('/login');
            } catch (error) {
                console.error('Error al eliminar la cuenta:', error);
                alert('Hubo un error al intentar eliminar la cuenta.');
            }
        }
    };
    

    const handleModifyUserData = () => {
        alert('Funcionalidad para modificar datos de usuario en desarrollo.');
    };

    const handleGenerateReportPDF = async (formData: ReportFormData) => {
        const token = localStorage.getItem('token');

        if (!token) {
            navigate('/login');
            return;
        }

        try {
            const response = await fetch(REPORT_URL, { 
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                    'access_token': API_KEY,
                },
                body: JSON.stringify(formData),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error al generar el informe');
            }

            // Aquí puedes manejar la descarga del PDF o la respuesta del backend
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `reporte_${new Date().toISOString()}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);

            alert('Informe generado y descargado.');

        } catch (error: any) {
            console.error('Error al generar el informe:', error);
            alert(`Error al generar el informe: ${error.message}`);
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
                const response = await fetch(DATOS_DE_USUARIO_URL, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`,
                        'access_token': API_KEY,
                    },
                });
                if (!response.ok) {
                    localStorage.removeItem('token');
                    navigate('/login');
                    return;
                }
                const userData: UserItem = await response.json();
                setUserData(userData);
                if (userData && userData.filters) {
                    setSelectedFilters(userData.filters);
                }
            } catch (error) {
                console.error('Error al obtener los datos del usuario:', error);
                localStorage.removeItem('token');
                navigate('/login');
            }
        };

        const fetchNews = async () => {
            try {
                const response = await fetch(NEWS_URL, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'access_token': API_KEY,
                    },
                });
                if (!response.ok) {
                    throw new Error('Error al obtener las noticias');
                }
                const newsData: NewsItem[] = await response.json();
                setNews(newsData);
            } catch (error) {
                console.error('Error al obtener las noticias');
            }
        };

        const fetchCompanies = async () => {
            try {
                const response = await fetch(COMPANIES_URL, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'access_token': API_KEY,
                    },
                });
                if (!response.ok) {
                    throw new Error('Error al obtener las empresas');
                }
                const companiesData: CompaniesItem[] = await response.json();
                setCompanies(companiesData);
                const uniqueTypes = Array.from(new Set(companiesData.map(company => company.type)));
                setCompanyTypes(uniqueTypes);
            } catch (error) {
                console.error('Error al obtener las empresas');
            }
        };

        const fetchFilters = async () => {
            try {
                const response = await fetch(FILTROS_FETCH_URL, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'access_token': API_KEY,
                    },
                });
                if (!response.ok) {
                    throw new Error("Error al obtener los filtros");
                }
                const filtersData: string[] = await response.json();
                setFiltersOptions(filtersData);
            } catch (error) {
                console.error("Error al obtener los filtros:", error);
            }
        };

        fetchCompanies();
        fetchNews();
        fetchUserData();
        fetchFilters();
    }, [navigate]);

    const toggleDropdown = () => {
        setIsDropdownOpen(!isDropdownOpen);
    };

    const toggleSubscriptionOptions = () => {
        setShowSubscriptionOptions(!showSubscriptionOptions);
    };

    const toggleFiltersOptions = () => {
        setShowFiltersOptions(!showFiltersOptions);
    };

    const toggleSettingsModal = () => {
        setIsSettingsModalOpen(!isSettingsModalOpen);
    };

    if (!userData) {
        return <div>Cargando...</div>;
    }

    const filteredCompanies = selectedCompanyType ? companies.filter(company => company.type === selectedCompanyType) : companies;

    return (
        <div className="flex flex-col h-screen bg-gray-100">
            <header className="bg-white shadow-lg p-4 flex justify-between items-center">
                <div className="relative">
                    <button onClick={toggleDropdown} className="flex items-center gap-2 cursor-pointer text-gray-800 font-semibold hover:text-blue-600 transition-all duration-300">
                        <span className="material-symbols-outlined">Usuario: </span>
                        <span className="font-bold">{userData?.username}</span>
                    </button>
                    {isDropdownOpen && (
                        <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg left-8 z-10">
                            <button onClick={toggleSettingsModal} className="block w-full text-left px-4 py-2 text-sm hover:bg-gray-100">Ajustes</button>
                            <a href="#" className="block px-4 py-2 text-sm hover:bg-gray-100">Mi perfil</a>
                        </div>
                    )}
                </div>
            </header>

            <div className="flex-grow p-8 bg-gray-200">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 items-stretch">
                    <div className="bg-white p-6 rounded-xl shadow-md transition-all hover:shadow-lg">
                        <h3 className="font-bold mb-4 text-lg text-gray-700">Mis suscripciones</h3>
                        <div className="bg-white p-4 rounded-md shadow-md max-h-64 h-64 overflow-y-auto relative">
                            {userData && userData.subscriptions && userData.subscriptions.length > 0 ? (
                                <ul className="list-disc pl-5">
                                    {userData.subscriptions.map((subscription) => (
                                        <li key={subscription} className="flex justify-between items-center py-1">
                                            <span className="text-gray-800">{subscription}</span>
                                            <button onClick={() => handleSubscriptionRemove(subscription)} className="ml-2 text-red-500 hover:text-red-700 transition-all cursor-pointer">
                                                x
                                            </button>
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <p className="text-gray-600">No tienes suscripciones.</p>
                            )}
                            <button
                                className="bg-blue-100 hover:bg-blue-200 text-white rounded-full h-8 w-8 flex items-center justify-center absolute bottom-2 right-2 transition-all transform hover:scale-110 cursor-pointer"
                                onClick={toggleSubscriptionOptions}
                            >
                                <span className="text-xl text-gray-600">+</span>
                            </button>
                            {showSubscriptionOptions && (
                                <div className="absolute bottom-10 right-0 bg-white rounded-md shadow-lg w-64 max-h-48 overflow-y-auto transition-all">
                                    <select
                                        className="w-full p-2 border-b text-sm"
                                        value={selectedCompanyType || ""}
                                        onChange={(e) => setSelectedCompanyType(e.target.value || null)}
                                    >
                                        <option value=""> Todos los tipos </option>
                                        {companyTypes.map((type) => (
                                            <option key={type} value={type}>{type}</option>
                                        ))}
                                    </select>
                                    {!selectedCompanyType && (
                                        <>
                                            <a className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer" onClick={() => handleSubscriptionClick('Creación de una nueva empresa')}>Creación de una nueva empresa</a>
                                            <a className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer" onClick={() => handleSubscriptionClick('Contratación abundante de empleados por parte de una empresa')}>Contratación abundante de empleados por parte de una empresa</a>
                                            <a className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer" onClick={() => handleSubscriptionClick('Cambio de sede de una empresa')}>Cambio de sede de una empresa</a>
                                        </>
                                    )}
                                    {filteredCompanies.map((company) => (
                                        <a key={company.id} className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer" onClick={() => handleSubscriptionClick(company.name)}>
                                            {company.name}
                                        </a>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="bg-white p-6 rounded-xl shadow-md transition-all hover:shadow-lg">
                        <h3 className="font-bold mb-4 text-lg text-gray-700">Noticias relacionadas con mis suscripciones</h3>
                        <div className="max-h-64 overflow-y-auto">
                            {(() => {
                                const filteredNews = news.filter(item => userData?.subscriptions.includes(item.topic) || userData?.subscriptions.includes(item.company));
                                return filteredNews.length > 0 ? (
                                    <ul className="list-disc pl-5">
                                        {filteredNews.map((newsItem) => (
                                            <li key={newsItem.id} className="pb-2">
                                                <div>
                                                    <p className="font-semibold">{newsItem.title}</p>
                                                    <p className="text-gray-600 text-sm">Empresa: {newsItem.company}</p>
                                                    <p className="text-gray-600 text-sm">Detalles: {newsItem.details}</p>
                                                </div>
                                            </li>
                                        ))}
                                    </ul>
                                ) : (
                                    <p className="text-gray-600">No hay noticias de interés.</p>
                                );
                            })()}
                        </div>
                    </div>

                    <div className="bg-white p-6 rounded-xl shadow-md transition-all hover:shadow-lg">
                        <h3 className="font-bold mb-4 text-lg text-gray-700">Filtros para mis noticias</h3>
                        <button onClick={toggleFiltersOptions} className="bg-blue-400 hover:bg-blue-500 text-white rounded-md px-4 py-2 w-full text-left transition-all cursor-pointer">
                            {showFiltersOptions ? "Cerrar Filtros" : "Seleccionar Filtros"}
                        </button>
                        <div className="bg-white p-4 rounded-md shadow-md max-h-64 h-64 overflow-y-auto relative">
                            {showFiltersOptions && (
                                <div className="relative mt-2 w-full">
                                    <div className="bg-white border rounded-md shadow-lg w-full max-h-48 overflow-y-auto z-10">
                                        {FiltersOptions.map((filter) => (
                                            <label key={filter} className="flex items-center px-2 py-1 cursor-pointer hover:bg-gray-100">
                                                <input
                                                    type="checkbox"
                                                    checked={selectedFilters.includes(filter)}
                                                    onChange={() => handleFilterChange(filter)}
                                                    className="mr-2"
                                                />
                                                {filter}
                                            </label>
                                        ))}
                                    </div>
                                </div>
                            )}
                            {selectedFilters.length > 0 && (
                                <div className="mt-4">
                                    <p className="font-semibold">Filtros seleccionados:</p>
                                    <ul className="list-disc pl-5">
                                        {selectedFilters.map((filter) => (
                                            <li key={filter} className="text-sm">{filter}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    </div>

                </div>

                <div className="bg-white p-6 rounded-xl shadow-md transition-all hover:shadow-lg mt-10">
                        <ReportGenerator onGenerateReport={handleGenerateReportPDF}/>
                    </div>

                <div className="mt-8">
                    <DataSelection onGenerate={handleGenerateChart} />
                    {chartData && <ChartEvaluation data={chartData} />}
                </div>

            </div>

            <SettingsModal
                isOpen={isSettingsModalOpen}
                onClose={toggleSettingsModal}
                onDeleteAccount={handleDeleteAccount}
                onModifyUserData={handleModifyUserData}
            />

        </div>
    );
};

export default Profile;