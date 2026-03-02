import React, { useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { html } from '../utils.js';

const COLORS = {
    'Óptima': '#22c55e',
    'Sobre': '#ef4444',
    'Sub': '#3b82f6',
    'Baja': '#f59e0b',
    'Alta': '#d97706'
};

const QualityAnalysis = ({ data }) => {

    const evolutionData = useMemo(() => {
        if (!data.length) return [];
        const grouped = {};
        data.forEach(item => {
            const validClassifs = ['Óptima', 'Sobre', 'Sub'];
            if (!validClassifs.includes(item.Clasificación) || item.Métrica !== 'Area') return;
            const key = `${item.Mes} ${item.Año}`;
            if (!grouped[key]) {
                grouped[key] = { name: key, 'Óptima': 0, 'Sobre': 0, 'Sub': 0, orderYear: item.Año, orderMonth: item.Mes };
            }
            grouped[key][item.Clasificación] += (item.Valor || 0);
        });
        return Object.values(grouped).sort((a, b) => a.orderYear - b.orderYear);
    }, [data]);

    const distributionData = useMemo(() => {
        if (!data.length) return [];
        const stats = { 'Óptima': 0, 'Sobre': 0, 'Sub': 0 };
        data.forEach(item => {
            if (stats[item.Clasificación] !== undefined && item.Métrica === 'Area') {
                stats[item.Clasificación] += (item.Valor || 0);
            }
        });
        return Object.keys(stats).map(key => ({
            name: key,
            value: stats[key]
        })).filter(d => d.value > 0);
    }, [data]);

    const pctOptima = useMemo(() => {
        const opt = distributionData.find(d => d.name === 'Óptima')?.value || 0;
        const total = distributionData.reduce((a, b) => a + b.value, 0);
        return total ? Math.round((opt / total) * 100) : 0;
    }, [distributionData]);

    return html`
        <div className="space-y-8">
            <div className="flex justify-between items-center border-b border-slate-100 pb-4">
                <div>
                    <h2 className="text-xl font-bold text-slate-800">Calidad de Aplicación</h2>
                    <p className="text-sm text-slate-500">Distribución y evolución temporal</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2 h-[400px]">
                    <h3 className="text-sm font-semibold text-slate-600 mb-4">Evolución Mensual (Área)</h3>
                    <${ResponsiveContainer} width="100%" height="100%">
                        <${BarChart} data=${evolutionData} margin=${{ top: 20, right: 30, left: 20, bottom: 5 }}>
                            <${CartesianGrid} strokeDasharray="3 3" vertical=${false} stroke="#E2E8F0" />
                            <${XAxis} dataKey="name" fontSize=${12} tickLine=${false} axisLine=${false} />
                            <${YAxis} fontSize=${12} tickLine=${false} axisLine=${false} />
                            <${Tooltip} 
                                contentStyle=${{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}
                                cursor=${{ fill: '#F1F5F9' }}
                            />
                            <${Legend} />
                            <${Bar} dataKey="Sub" stackId="a" fill=${COLORS['Sub']} radius=${[0, 0, 4, 4]} />
                            <${Bar} dataKey="Óptima" stackId="a" fill=${COLORS['Óptima']} />
                            <${Bar} dataKey="Sobre" stackId="a" fill=${COLORS['Sobre']} radius=${[4, 4, 0, 0]} />
                        <//>
                    <//>
                </div>

                <div className="h-[400px] flex flex-col items-center justify-center bg-slate-50 rounded-2xl p-6">
                    <h3 className="text-sm font-semibold text-slate-600 mb-4 self-start w-full">Distribución Total</h3>
                    <div className="w-full h-full relative">
                         <${ResponsiveContainer} width="100%" height="100%">
                            <${PieChart}>
                                <${Pie}
                                    data=${distributionData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius=${80}
                                    outerRadius=${110}
                                    paddingAngle=${5}
                                    dataKey="value"
                                >
                                    ${distributionData.map((entry, index) => html`
                                        <${Cell} key=${`cell-${index}`} fill=${COLORS[entry.name]} />
                                    `)}
                                <//>
                                <${Tooltip} />
                                <${Legend} verticalAlign="bottom" height=${36}/>
                            <//>
                        <//>
                        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                            <div className="text-center">
                                <span className="block text-3xl font-bold text-slate-800">
                                    ${pctOptima}%
                                </span>
                                <span className="text-xs text-slate-400 font-medium">ÓPTIMA</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
};

export default QualityAnalysis;
