import React, { useMemo } from 'react';
import { LayoutDashboard, Activity, Gauge, Map, Filter } from 'lucide-react';
import { html } from '../utils.js';

const Sidebar = ({ activeTab, setActiveTab, filters, setFilters, data }) => {

    const filterOptions = useMemo(() => {
        if (!data || data.length === 0) return { years: [], months: [], zones: [], motors: [] };

        const years = [...new Set(data.map(d => d.Año))].sort();
        const months = [...new Set(data.map(d => d.Mes))].sort();
        const zones = [...new Set(data.map(d => d.Zona))].sort();
        const motors = [...new Set(data.map(d => d.Motor))].sort();

        return { years, months, zones, motors };
    }, [data]);

    const handleFilterChange = (key, value) => {
        setFilters(prev => ({
            ...prev,
            [key]: value
        }));
    };

    const toggleFilter = (key, value) => {
        setFilters(prev => {
            const current = prev[key];
            const updated = current.includes(value)
                ? current.filter(item => item !== value)
                : [...current, value];
            return { ...prev, [key]: updated };
        });
    };

    return html`
        <aside className="w-80 h-full bg-white border-r border-slate-200 flex flex-col shadow-xl z-20">
            <div className="p-6 border-b border-slate-100 flex items-center gap-3">
                <div className="w-10 h-10 bg-agri-500 rounded-xl flex items-center justify-center text-white shadow-lg shadow-agri-500/30">
                    <${LayoutDashboard} size=${20} />
                </div>
                <span className="font-bold text-xl text-slate-800 tracking-tight">AgroMetric</span>
            </div>

            <nav className="p-4 space-y-2">
                <${NavItem} 
                    icon=${html`<${Activity} />`} 
                    label="Calidad de Labor" 
                    isActive=${activeTab === 'summary'} 
                    onClick=${() => setActiveTab('summary')} 
                />
                <${NavItem} 
                    icon=${html`<${Gauge} />`} 
                    label="Análisis de Motores" 
                    isActive=${activeTab === 'motor'} 
                    onClick=${() => setActiveTab('motor')} 
                />
                <${NavItem} 
                    icon=${html`<${Map} />`} 
                    label="Detalle Territorial" 
                    isActive=${activeTab === 'geo'} 
                    onClick=${() => setActiveTab('geo')} 
                />
            </nav>

            <div className="p-6 flex-1 overflow-y-auto">
                <div className="flex items-center gap-2 mb-4 text-slate-400 uppercase text-xs font-bold tracking-wider">
                    <${Filter} size=${14} />
                    <span>Filtros Globales</span>
                </div>

                <div className="mb-6">
                    <label className="text-sm font-semibold text-slate-700 mb-2 block">Año Agrícola</label>
                    <select 
                        className="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 text-sm focus:ring-2 focus:ring-agri-500 outline-none transition-all"
                        value=${filters.year}
                        onChange=${(e) => handleFilterChange('year', e.target.value === 'All' ? 'All' : Number(e.target.value))}
                    >
                        <option value="All">Todos los años</option>
                        ${filterOptions.years.map(y => html`<option key=${y} value=${y}>${y}</option>`)}
                    </select>
                </div>

                <${FilterSection} title="Meses" options=${filterOptions.months} selected=${filters.month} onToggle=${(v) => toggleFilter('month', v)} />
                
                <${FilterSection} title="Zonas" options=${filterOptions.zones} selected=${filters.zone} onToggle=${(v) => toggleFilter('zone', v)} />
                 
                <${FilterSection} title="Motores" options=${filterOptions.motors} selected=${filters.motor} onToggle=${(v) => toggleFilter('motor', v)} limit=${5} />

            </div>
            
            <div className="p-4 border-t border-slate-100 text-center">
                <button 
                    onClick=${() => setFilters({ year: 'All', month: [], zone: [], motor: [] })}
                    className="text-xs text-red-500 hover:text-red-600 font-medium transition-colors"
                >
                    Limpiar todos los filtros
                </button>
            </div>
        </aside>
    `;
};

const NavItem = ({ icon, label, isActive, onClick }) => html`
    <button 
        onClick=${onClick}
        className=${`w-full flex items-center gap-3 p-3.5 rounded-xl transition-all duration-300 group
            ${isActive
        ? 'bg-gradient-to-r from-agri-500 to-agri-600 text-white shadow-lg shadow-agri-500/30'
        : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900'
    }`}
    >
        ${React.cloneElement(icon, { size: 20, className: isActive ? 'text-white' : 'text-slate-400 group-hover:text-agri-500' })}
        <span className="font-medium text-sm">${label}</span>
    </button>
`;

const FilterSection = ({ title, options, selected, onToggle, limit = 100 }) => {
    const [expanded, setExpanded] = React.useState(false);
    const visibleOptions = expanded ? options : options.slice(0, limit);

    return html`
        <div className="mb-6">
            <label className="text-sm font-semibold text-slate-700 mb-2 block flex justify-between">
                ${title}
                ${selected.length > 0 && html`<span className="text-agri-500 text-xs">${selected.length}</span>`}
            </label>
            <div className="flex flex-wrap gap-1.5">
                ${visibleOptions.map(opt => html`
                    <button
                        key=${opt}
                        onClick=${() => onToggle(opt)}
                        className=${`text-xs px-2.5 py-1 rounded-full border transition-all duration-200
                            ${selected.includes(opt)
            ? 'bg-agri-100 border-agri-200 text-agri-800 font-medium'
            : 'bg-white border-slate-200 text-slate-500 hover:border-agri-300'
        }`}
                    >
                        ${opt}
                    </button>
                `)}
                ${options.length > limit && html`
                    <button 
                        onClick=${() => setExpanded(!expanded)}
                        className="text-xs text-indigo-500 font-medium ml-1 hover:underline"
                    >
                        ${expanded ? 'Ver menos' : `+${options.length - limit} más`}
                    </button>
                `}
            </div>
        </div>
    `;
};

export default Sidebar;
