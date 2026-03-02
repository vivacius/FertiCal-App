import React, { useMemo } from 'react';
import { ArrowUpRight, ArrowDownRight, Layers, Target, AlertTriangle, Activity } from 'lucide-react';
import { html } from '../utils.js';

const KPICards = ({ data }) => {

    const kpis = useMemo(() => {
        if (!data.length) return { area: 0, optimal: 0, over: 0, under: 0, coverage: 0 };

        const areaMetrics = data.filter(d => d.Métrica === 'Area');
        const validClassifs = ['Sobre', 'Sub', 'Óptima'];
        const qualityData = areaMetrics.filter(d => validClassifs.includes(d.Clasificación));

        const totalArea = qualityData.reduce((acc, curr) => acc + (curr.Valor || 0), 0);

        const optimalArea = qualityData
            .filter(d => d.Clasificación === 'Óptima')
            .reduce((acc, curr) => acc + (curr.Valor || 0), 0);

        const overArea = qualityData
            .filter(d => d.Clasificación === 'Sobre')
            .reduce((acc, curr) => acc + (curr.Valor || 0), 0);

        const underArea = qualityData
            .filter(d => d.Clasificación === 'Sub')
            .reduce((acc, curr) => acc + (curr.Valor || 0), 0);

        const uniqueSuertes = [...new Map(data.map(item => [item.Suerte + item.Fecha_Labor, item])).values()];
        const totalSte = uniqueSuertes.reduce((acc, curr) => acc + (curr.Area_ste || 0), 0);
        const totalApplied = uniqueSuertes.reduce((acc, curr) => acc + (curr.Area_aplicada || 0), 0);

        return {
            area: totalArea,
            optimal: totalArea ? (optimalArea / totalArea * 100) : 0,
            over: totalArea ? (overArea / totalArea * 100) : 0,
            under: totalArea ? (underArea / totalArea * 100) : 0,
            coverage: totalSte ? (totalApplied / totalSte * 100) : 0
        };
    }, [data]);

    return html`
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <${Card} 
                label="Área Fertilizada" 
                value=${`${kpis.area.toLocaleString(undefined, { maximumFractionDigits: 0 })} ha`} 
                subValue="Total procesado"
                icon=${html`<${Layers} className="text-blue-500" />`}
                trend="neutral"
            />
            <${Card} 
                label="Calidad Óptima" 
                value=${`${kpis.optimal.toFixed(1)}%`} 
                subValue="Meta: >85%"
                icon=${html`<${Target} className="text-agri-500" />`}
                trend=${kpis.optimal >= 85 ? "up" : "down"}
                isGood=${true}
            />
            <${Card} 
                label="Sobre-Aplicación" 
                value=${`${kpis.over.toFixed(1)}%`} 
                subValue="Desperdicio potencial"
                icon=${html`<${AlertTriangle} className="text-red-500" />`}
                trend=${kpis.over > 5 ? "up" : "down"}
                isGood=${false}
            />
            <${Card} 
                label="Cobertura Labor" 
                value=${`${kpis.coverage.toFixed(1)}%`} 
                subValue="Sobre área programada"
                icon=${html`<${Activity} className="text-indigo-500" />`}
                trend="neutral"
            />
        </div>
    `;
};

const Card = ({ label, value, subValue, icon, trend, isGood }) => {
    let trendColor = 'text-slate-400';
    let TrendIcon = null;

    if (trend === 'up') {
        TrendIcon = ArrowUpRight;
        trendColor = isGood ? 'text-agri-500' : 'text-red-500';
    } else if (trend === 'down') {
        TrendIcon = ArrowDownRight;
        trendColor = isGood ? 'text-red-500' : 'text-agri-500';
    }

    return html`
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:scale-110 transition-transform duration-500">
                ${React.cloneElement(icon, { size: 60 })}
            </div>

            <div className="flex justify-between items-start mb-4 relative z-10">
                <div className="p-2 bg-slate-50 rounded-lg">
                    ${React.cloneElement(icon, { size: 24 })}
                </div>
                ${TrendIcon && html`<${TrendIcon} className=${trendColor} />`}
            </div>
            
            <div className="relative z-10">
                <h3 className="text-slate-500 text-sm font-medium mb-1">${label}</h3>
                <div className="text-3xl font-bold text-slate-800 tracking-tight">${value}</div>
                <p className="text-xs text-slate-400 mt-2 font-medium">${subValue}</p>
            </div>
        </div>
    `;
};

export default KPICards;
