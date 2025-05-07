import React, { useState } from 'react';

interface DataSelectionProps {
    onGenerate: (params: any) => void;
}

const DataSelection: React.FC<DataSelectionProps> = ({ onGenerate }) => {
    const [dataType, setDataType] = useState('empresasCreadas');
    const [companyType, setCompanyType] = useState('todos');
    const [timePeriod, setTimePeriod] = useState('ultimoAno');

    const handleGenerate = () => {
        onGenerate({ dataType, companyType, timePeriod });
    };

    return (
        <div className="bg-white p-6 rounded-xl shadow-md">
            <h3 className="font-bold mb-4 text-lg text-gray-700">Selecciona los datos del gráfico</h3>
            <select value={dataType} onChange={(e) => setDataType(e.target.value)} className="w-full p-2 border rounded-md mb-2">
                <option value="empresasCreadas">Cantidad de empresas creadas</option>
                <option value="crecimientoEmpleados">Crecimiento de empleados</option>
                <option value="cambioSede">Cambios de sede de empresas</option>
            </select>
            <select value={companyType} onChange={(e) => setCompanyType(e.target.value)} className="w-full p-2 border rounded-md mb-2">
                <option value="todos">Todos los tipos</option>
                <option value="tecnologia">Tecnología</option>
                {/* ... otras opciones */}
            </select>
            <select value={timePeriod} onChange={(e) => setTimePeriod(e.target.value)} className="w-full p-2 border rounded-md mb-2">
                <option value="ultimoAno">Último año</option>
                <option value="ultimoMes">Último mes</option>
                {/* ... otras opciones */}
            </select>
            <button onClick={handleGenerate} className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded cursor-pointer">
                Generar gráfico
            </button>
        </div>
    );
};

export default DataSelection;