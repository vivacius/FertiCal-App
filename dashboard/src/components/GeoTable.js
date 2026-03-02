import React, { useMemo, useState } from 'react';
import { html } from '../utils.js';

const GeoTable = ({ data }) => {
    const [sortConfig, setSortConfig] = useState({ key: 'pctOptima', direction: 'asc' });

    const rows = useMemo(() => {
        if (!data.length) return [];
        const grouped = {};

        data.forEach(item => {
            const validClassifs = ['Óptima', 'Sobre', 'Sub'];
            if (!validClassifs.includes(item.Clasificación) || item.Métrica !== 'Area') return;
            const key = `${item.Zona}-${item.Hacienda}-${item.Suerte}`;
            if (!grouped[key]) {
                grouped[key] = {
                    id: key,
                    zona: item.Zona,
                    hacienda: item.Hacienda,
                    suerte: item.Suerte,
                    optima: 0,
                    sobre: 0,
                    sub: 0,
                    total: 0
                };
            }
            grouped[key][item.Clasificación === 'Óptima' ? 'optima' : item.Clasificación.toLowerCase()] += (item.Valor || 0);
            grouped[key].total += (item.Valor || 0);
        });

        let result = Object.values(grouped).map(row => ({
            ...row,
            pctOptima: row.total ? (row.optima / row.total) * 100 : 0,
            pctSobre: row.total ? (row.sobre / row.total) * 100 : 0,
            pctSub: row.total ? (row.sub / row.total) * 100 : 0,
        }));

        if (sortConfig.key) {
            result.sort((a, b) => {
                if (a[sortConfig.key] < b[sortConfig.key]) {
                    return sortConfig.direction === 'asc' ? -1 : 1;
                }
                if (a[sortConfig.key] > b[sortConfig.key]) {
                    return sortConfig.direction === 'asc' ? 1 : -1;
                }
                return 0;
            });
        }
        return result;
    }, [data, sortConfig]);

    const requestSort = (key) => {
        let direction = 'asc';
        if (sortConfig.key === key && sortConfig.direction === 'asc') {
            direction = 'desc';
        }
        setSortConfig({ key, direction });
    };

    const getSortIcon = (key) => {
        if (sortConfig.key !== key) return html`<span className="text-slate-300 ml-1">↕</span>`;
        return sortConfig.direction === 'asc' ? html`<span className="ml-1">↑</span>` : html`<span className="ml-1">↓</span>`;
    };

    return html`
        <div className="space-y-4">
            <div className="border-b border-slate-100 pb-4">
                 <h2 className="text-xl font-bold text-slate-800">Detalle Territorial</h2>
            </div>
            
            <div className="overflow-x-auto rounded-xl border border-slate-200">
                <table className="w-full text-sm text-left">
                    <thead className="bg-slate-50 text-slate-500 uppercase text-xs font-semibold">
                        <tr>
                            <th className="px-6 py-4 cursor-pointer hover:bg-slate-100" onClick=${() => requestSort('zona')}>Zona ${getSortIcon('zona')}</th>
                            <th className="px-6 py-4 cursor-pointer hover:bg-slate-100" onClick=${() => requestSort('hacienda')}>Hacienda ${getSortIcon('hacienda')}</th>
                            <th className="px-6 py-4 cursor-pointer hover:bg-slate-100" onClick=${() => requestSort('suerte')}>Suerte ${getSortIcon('suerte')}</th>
                            <th className="px-6 py-4 text-right cursor-pointer hover:bg-slate-100" onClick=${() => requestSort('total')}>Total (ha) ${getSortIcon('total')}</th>
                            <th className="px-6 py-4 text-right cursor-pointer hover:bg-slate-100" onClick=${() => requestSort('pctOptima')}>% Óptima ${getSortIcon('pctOptima')}</th>
                            <th className="px-6 py-4 text-right cursor-pointer hover:bg-slate-100" onClick=${() => requestSort('pctSobre')}>% Sobre ${getSortIcon('pctSobre')}</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                        ${rows.slice(0, 100).map((row) => html`
                            <tr key=${row.id} className="hover:bg-slate-50 transition-colors">
                                <td className="px-6 py-4 font-medium text-slate-700">${row.zona}</td>
                                <td className="px-6 py-4 text-slate-600">${row.hacienda}</td>
                                <td className="px-6 py-4 text-slate-600">${row.suerte}</td>
                                <td className="px-6 py-4 text-right font-mono text-slate-700">${row.total.toFixed(1)}</td>
                                <td className="px-6 py-4 text-right">
                                    <${Badge} value=${row.pctOptima} type="optima" />
                                </td>
                                <td className="px-6 py-4 text-right">
                                    <${Badge} value=${row.pctSobre} type="semaphor" inverse />
                                </td>
                            </tr>
                        `)}
                    </tbody>
                </table>
            </div>
            <p className="text-xs text-slate-400 text-center mt-2">Mostrando primeros 100 registros</p>
        </div>
    `;
};

const Badge = ({ value, type, inverse }) => {
    let color = 'bg-slate-100 text-slate-600';
    if (type === 'optima') {
        if (value >= 85) color = 'bg-green-100 text-green-700';
        else if (value >= 70) color = 'bg-yellow-100 text-yellow-700';
        else color = 'bg-red-100 text-red-700';
    } else if (type === 'semaphor') {
        if (inverse) {
            if (value > 10) color = 'bg-red-100 text-red-700';
            else if (value > 5) color = 'bg-yellow-100 text-yellow-700';
            else color = 'bg-green-100 text-green-700';
        }
    }

    return html`
        <span className=${`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${color}`}>
            ${value.toFixed(1)}%
        </span>
    `;
};

export default GeoTable;
