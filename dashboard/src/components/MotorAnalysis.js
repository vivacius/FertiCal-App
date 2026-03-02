import React, { useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { html } from '../utils.js';

const COLORS = {
    'Óptima': '#22c55e',
    'Sobre': '#ef4444',
    'Sub': '#3b82f6'
};

const MotorAnalysis = ({ data }) => {

    const motorData = useMemo(() => {
        if (!data.length) return [];
        const grouped = {};

        data.forEach(item => {
            const validClassifs = ['Óptima', 'Sobre', 'Sub'];
            if (!validClassifs.includes(item.Clasificación) || item.Métrica !== 'Area') return;
            if (item.Motor === 'Total' || item.Motor === 'No aplica') return;

            if (!grouped[item.Motor]) {
                grouped[item.Motor] = { name: item.Motor, 'Óptima': 0, 'Sobre': 0, 'Sub': 0, total: 0 };
            }
            grouped[item.Motor][item.Clasificación] += (item.Valor || 0);
            grouped[item.Motor].total += (item.Valor || 0);
        });

        const result = Object.values(grouped).map(m => ({
            ...m,
            pctOptima: (m['Óptima'] / m.total) * 100,
            pctSobre: (m['Sobre'] / m.total) * 100,
            pctSub: (m['Sub'] / m.total) * 100
        }));

        return result.sort((a, b) => b.pctSobre - a.pctSobre);
    }, [data]);

    return html`
        <div className="space-y-8">
            <div className="border-b border-slate-100 pb-4">
                 <h2 className="text-xl font-bold text-slate-800">Análisis de Motores</h2>
                 <p className="text-sm text-slate-500">Comparativa técnica y ranking de desviaciones</p>
            </div>

            <div className="h-[500px]">
                <h3 className="text-sm font-semibold text-slate-600 mb-4">Desempeño Relativo (%) - Ordenado por Sobre-aplicación</h3>
                <${ResponsiveContainer} width="100%" height="100%">
                    <${BarChart} layout="vertical" data=${motorData} margin=${{ top: 20, right: 30, left: 60, bottom: 5 }}>
                        <${CartesianGrid} strokeDasharray="3 3" horizontal=${false} stroke="#E2E8F0" />
                        <${XAxis} type="number" unit="%" fontSize=${12} tickLine=${false} axisLine=${false} />
                        <${YAxis} dataKey="name" type="category" fontSize=${12} tickLine=${false} axisLine=${false} width=${80} />
                        <${Tooltip} 
                            formatter=${(value) => `${value.toFixed(1)}%`}
                            contentStyle=${{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}
                            cursor=${{ fill: 'transparent' }}
                        />
                        <${Legend} />
                        <${Bar} dataKey="pctSub" name="% Sub" stackId="a" fill=${COLORS['Sub']} radius=${[0, 0, 0, 0]} barSize=${20} />
                        <${Bar} dataKey="pctOptima" name="% Óptima" stackId="a" fill=${COLORS['Óptima']} barSize=${20} />
                        <${Bar} dataKey="pctSobre" name="% Sobre" stackId="a" fill=${COLORS['Sobre']} radius=${[0, 4, 4, 0]} barSize=${20} />
                    <//>
                <//>
            </div>
        </div>
    `;
};

export default MotorAnalysis;
