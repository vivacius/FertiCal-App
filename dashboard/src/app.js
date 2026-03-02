import React, { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import { html } from './utils.js';
import Sidebar from './components/Sidebar.js';
import KPICards from './components/KPICards.js';
import QualityAnalysis from './components/QualityAnalysis.js';
import MotorAnalysis from './components/MotorAnalysis.js';
import GeoTable from './components/GeoTable.js';

const App = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('summary');

    const [filters, setFilters] = useState({
        year: 'All',
        month: [],
        zone: [],
        motor: []
    });

    useEffect(() => {
        fetch('./dashboard_data.json')
            .then(res => res.json())
            .then(jsonData => {
                setData(jsonData);
                setLoading(false);
            })
            .catch(err => console.error("Error loading data:", err));
    }, []);

    const filteredData = data.filter(item => {
        if (filters.year !== 'All' && item.Año !== filters.year) return false;
        if (filters.month.length > 0 && !filters.month.includes(item.Mes)) return false;
        if (filters.zone.length > 0 && !filters.zone.includes(item.Zona)) return false;
        if (filters.motor.length > 0 && !filters.motor.includes(item.Motor)) return false;
        return true;
    });

    if (loading) {
        return html`
            <div className="flex items-center justify-center h-screen bg-gray-100">
                <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-agri-500"></div>
            </div>
        `;
    }

    return html`
        <div className="flex h-screen overflow-hidden text-slate-800 font-sans">
            <${Sidebar} 
                activeTab=${activeTab} 
                setActiveTab=${setActiveTab} 
                filters=${filters} 
                setFilters=${setFilters} 
                data=${data}
            />
            
            <main className="flex-1 overflow-y-auto p-8">
                <header className="mb-8 flex justify-between items-center">
                    <div>
                        <h1 className="text-3xl font-bold text-slate-900">Fertilización de Precisión</h1>
                        <p className="text-slate-500 mt-1">
                            ${filteredData.length.toLocaleString()} registros analizados
                        </p>
                    </div>
                </header>

                <div className="space-y-6">
                    <${KPICards} data=${filteredData} />

                    <div className="glass-panel rounded-2xl p-6 min-h-[500px]">
                        ${activeTab === 'summary' && html`<${QualityAnalysis} data=${filteredData} />`}
                        ${activeTab === 'motor' && html`<${MotorAnalysis} data=${filteredData} />`}
                        ${activeTab === 'geo' && html`<${GeoTable} data=${filteredData} />`}
                    </div>
                </div>
            </main>
        </div>
    `;
};

const root = createRoot(document.getElementById('root'));
root.render(html`<${App} />`);
