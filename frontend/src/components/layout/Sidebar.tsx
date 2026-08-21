import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Map,
  ScanEye,
  Layers,
  CloudRain,
  Timer,
  Network,
  ShieldAlert,
  FileSpreadsheet,
  Camera,
  BellRing,
  DatabaseZap,
  Pickaxe,
  Activity,
} from 'lucide-react';
import { cn } from '@/utils/cn';

interface NavItem {
  name: string;
  path: string;
  icon: React.ReactNode;
  badge?: string;
}

export const Sidebar: React.FC = () => {
  const monitoringNav: NavItem[] = [
    { name: 'Command Center', path: '/', icon: <LayoutDashboard className="w-3.5 h-3.5" /> },
    { name: 'GIS Risk Map', path: '/risk-map', icon: <Map className="w-3.5 h-3.5" /> },
    { name: 'Landslide Inventory', path: '/inventory', icon: <FileSpreadsheet className="w-3.5 h-3.5" />, badge: '50 Events' },
  ];

  const analysisNav: NavItem[] = [
    { name: 'Spatial Detection (U-Net)', path: '/detection', icon: <ScanEye className="w-3.5 h-3.5" /> },
    { name: 'Terrain Susceptibility', path: '/terrain', icon: <Layers className="w-3.5 h-3.5" /> },
    { name: 'Weather Hazard', path: '/weather', icon: <CloudRain className="w-3.5 h-3.5" /> },
    { name: 'Temporal Risk (LSTM)', path: '/temporal-risk', icon: <Timer className="w-3.5 h-3.5" /> },
    { name: 'Multimodal Late Fusion', path: '/multimodal-risk', icon: <Network className="w-3.5 h-3.5" /> },
  ];

  const warningNav: NavItem[] = [
    { name: 'Warning Strategy', path: '/early-warning', icon: <ShieldAlert className="w-3.5 h-3.5" /> },
    { name: 'Alerts & Authorization', path: '/alerts', icon: <BellRing className="w-3.5 h-3.5" /> },
    { name: 'Field Reports Queue', path: '/field-reports', icon: <Camera className="w-3.5 h-3.5" /> },
  ];

  const systemNav: NavItem[] = [
    { name: 'Data & Model Health', path: '/data-health', icon: <DatabaseZap className="w-3.5 h-3.5" /> },
    { name: 'Integration Boundaries', path: '/integrations', icon: <Activity className="w-3.5 h-3.5" /> },
  ];

  const secondaryNav: NavItem[] = [
    { name: 'Jharia Open-Cast Pit', path: '/jharia', icon: <Pickaxe className="w-3.5 h-3.5" />, badge: 'Mining' },
  ];

  const renderNavGroup = (title: string, items: NavItem[], badgeColor = 'bg-slate-800 text-slate-300 border-slate-700') => (
    <div className="py-2.5 border-b border-slate-800/80 last:border-b-0">
      <div className="px-3 py-1 text-[10px] font-mono font-bold tracking-widest text-slate-500 uppercase">
        {title}
      </div>
      <nav className="space-y-0.5 mt-1">
        {items.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              cn(
                'flex items-center justify-between px-2.5 py-1.5 rounded text-xs font-medium transition-colors',
                isActive
                  ? 'bg-blue-950/70 text-blue-300 border border-blue-800/80 font-semibold'
                  : 'text-slate-400 hover:bg-slate-900/80 hover:text-slate-200'
              )
            }
          >
            <div className="flex items-center gap-2.5 min-w-0">
              <span className="shrink-0 text-slate-400">{item.icon}</span>
              <span className="truncate">{item.name}</span>
            </div>
            {item.badge && (
              <span className={cn('text-[9px] font-mono px-1.5 py-0.2 rounded border shrink-0', badgeColor)}>
                {item.badge}
              </span>
            )}
          </NavLink>
        ))}
      </nav>
    </div>
  );

  return (
    <aside className="w-60 bg-slate-950 border-r border-slate-800 flex flex-col shrink-0 h-[calc(100vh-4rem)] sticky top-16 overflow-y-auto">
      <div className="p-2 space-y-0.5">
        {renderNavGroup('MONITORING', monitoringNav)}
        {renderNavGroup('ANALYSIS & MODELS', analysisNav)}
        {renderNavGroup('EARLY WARNING & OPS', warningNav)}
        {renderNavGroup('SYSTEM AUDIT', systemNav)}
        {renderNavGroup('SECONDARY SECTOR', secondaryNav, 'bg-amber-950/80 text-amber-300 border-amber-800')}
      </div>

      <div className="mt-auto p-3 border-t border-slate-800/80 bg-slate-950 text-[10px] font-mono text-slate-500 leading-tight space-y-1">
        <div className="flex items-center justify-between">
          <span>FRAMEWORK:</span>
          <span className="text-slate-400 font-semibold">LATE FUSION</span>
        </div>
        <div className="flex items-center justify-between">
          <span>REFERENCE:</span>
          <span className="text-slate-400 font-semibold">31 DEC 2024</span>
        </div>
        <div className="pt-1 text-[9px] text-slate-500 italic border-t border-slate-800">
          Research Decision Support System
        </div>
      </div>
    </aside>
  );
};

