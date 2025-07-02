import React, { useState, ChangeEvent, FormEvent } from 'react';

interface ReportFormData {
    fechaInicio: string;
    fechaFin: string;
    tipoCreacion: boolean;
    tipoCambioSede: boolean;
    tipoCrecimiento: boolean;
    incluirGraficos: boolean;
    mail: string;
    message: string;
}

interface ReportGeneratorProps {
    onGenerateReport: (formData: ReportFormData) => void;
}

const ReportGenerator: React.FC<ReportGeneratorProps> = ({ onGenerateReport }) => {
    const [showReportOptions, setShowReportOptions] = useState(false);
    const [reportFormData, setReportFormData] = useState<ReportFormData>({
        fechaInicio: "",
        fechaFin: "",
        tipoCreacion: false,
        tipoCambioSede: false,
        tipoCrecimiento: false,
        incluirGraficos: false,
        mail: "",
        message: "",
    });
    const [loading, setLoading] = useState(false);
    const [response, setResponse] = useState("");

    const handleDateChange = (e: ChangeEvent<HTMLInputElement>) => {
        setReportFormData({ ...reportFormData, [e.target.name]: e.target.value });
    };

    const handleCheckboxChange = (e: ChangeEvent<HTMLInputElement>) => {
        setReportFormData({ ...reportFormData, [e.target.name]: e.target.checked });
    };

    const handleInputChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        setReportFormData({ ...reportFormData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        setResponse("");

        if (!reportFormData.fechaInicio.trim() || !reportFormData.fechaFin.trim()) {
            setResponse("Las fechas de inicio y fin son obligatorias.");
            return;
        }

        const isTipoSelected = reportFormData.tipoCreacion || reportFormData.tipoCambioSede || reportFormData.tipoCrecimiento;
        if (!isTipoSelected) {
            setResponse("Debes seleccionar al menos un tipo de noticia.");
            return;
        }

        if (new Date(reportFormData.fechaInicio) > new Date(reportFormData.fechaFin)) {
            setResponse("La fecha de fin debe ser posterior a la de inicio.");
            return;
        }

        setLoading(true);

        try {
            onGenerateReport(reportFormData);
            setResponse("Solicitud de informe enviada.");
            setReportFormData({
                fechaInicio: "",
                fechaFin: "",
                tipoCreacion: false,
                tipoCambioSede: false,
                tipoCrecimiento: false,
                incluirGraficos: false,
                mail: "",
                message: "",
            });
        } catch {
            setResponse("Error al generar el documento PDF. Inténtalo de nuevo.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            <button
                onClick={() => setShowReportOptions(!showReportOptions)}
                className="w-full text-left px-4 py-2 bg-yellow-100 hover:bg-yellow-200 text-gray-700 rounded-md transition-all cursor-pointer"
            >
                Generar informe PDF
            </button>

            {showReportOptions && (
                <div className="mt-4 bg-gray-50 border border-gray-200 rounded-lg p-4 shadow-inner">
                    <form className="space-y-4" onSubmit={handleSubmit}>
                        <div>
                            <label className="block text-sm text-gray-600">Desde</label>
                            <input type="date" name="fechaInicio" value={reportFormData.fechaInicio} onChange={handleDateChange} className="w-full p-2 border border-gray-300 rounded-lg" />
                        </div>
                        <div>
                            <label className="block text-sm text-gray-600">Hasta</label>
                            <input type="date" name="fechaFin" value={reportFormData.fechaFin} onChange={handleDateChange} className="w-full p-2 border border-gray-300 rounded-lg" />
                        </div>

                        <div>
                            <label className="block text-sm text-gray-600 mb-1">Tipo de noticias</label>
                            <div className="flex flex-col">
                                <label className="inline-flex items-center mb-1">
                                    <input type="checkbox" name="tipoCreacion" checked={reportFormData.tipoCreacion} onChange={handleCheckboxChange} className="mr-2" />
                                    Creación de empresas
                                </label>
                                <label className="inline-flex items-center mb-1">
                                    <input type="checkbox" name="tipoCambioSede" checked={reportFormData.tipoCambioSede} onChange={handleCheckboxChange} className="mr-2" />
                                    Cambio de sede
                                </label>
                                <label className="inline-flex items-center mb-1">
                                    <input type="checkbox" name="tipoCrecimiento" checked={reportFormData.tipoCrecimiento} onChange={handleCheckboxChange} className="mr-2" />
                                    Crecimiento superlativo
                                </label>
                            </div>
                        </div>

                        <div>
                            <label className="inline-flex items-center">
                                <input type="checkbox" name="incluirGraficos" checked={reportFormData.incluirGraficos} onChange={handleCheckboxChange} className="mr-2" />
                                Incluir gráficos y visualizaciones
                            </label>
                        </div>

                        <div>
                            <label className="block text-sm text-gray-600">Correo electrónico (opcional)</label>
                            <input type="email" name="mail" value={reportFormData.mail} onChange={handleInputChange} placeholder="Tu correo" className="w-full p-2 border border-gray-300 rounded-lg" />
                        </div>

                        <div>
                            <label className="block text-sm text-gray-600">Notas adicionales</label>
                            <textarea name="message" value={reportFormData.message} onChange={handleInputChange} className="w-full p-2 border border-gray-300 rounded-lg h-24" placeholder="Comentarios u observaciones"></textarea>
                        </div>

                        <button type="submit" className="w-full bg-blue-500 hover:bg-blue-600 text-white py-2 rounded-lg shadow-md transition-transform transform hover:scale-105" disabled={loading}>
                            {loading ? "Generando..." : "Generar informe"}
                        </button>

                        {response && <p className="mt-2 text-center text-gray-700">{response}</p>}
                    </form>
                </div>
            )}
        </>
    );
};

export default ReportGenerator;
