import React, { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';

interface ChartData {
    label: string;
    value: number;
}

interface ChartEvaluationProps {
    data: ChartData[];
}

const ChartEvaluation: React.FC<ChartEvaluationProps> = ({ data }) => {
    const chartRef = useRef<HTMLCanvasElement>(null);
    const chartInstance = useRef<Chart | null>(null);

    useEffect(() => {
        if (!chartRef.current || data.length === 0) return;

        if (chartInstance.current) {
            chartInstance.current.destroy();
        }

        const ctx = chartRef.current.getContext('2d');
        if (!ctx) return;

        chartInstance.current = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map((item) => item.label),
                datasets: [
                    {
                        label: 'Datos',
                        data: data.map((item) => item.value),
                        backgroundColor: 'rgba(54, 162, 235, 0.5)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                    },
                },
            },
        });

        return () => {
            chartInstance.current?.destroy();
        };
    }, [data]);

    return (
        <div className="bg-white p-6 rounded-xl shadow-md">
            <h3 className="font-bold mb-4 text-lg text-gray-700">Gráfico</h3>
            <div style={{ height: '400px' }} className="flex items-center justify-center">
                {data.length === 0 ? (
                    <p className="text-gray-500 text-center">No hay datos para mostrar.</p>
                ) : (
                    <canvas ref={chartRef}></canvas>
                )}
            </div>
        </div>
    );
};

export default ChartEvaluation;
