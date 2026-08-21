import React from 'react';
import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { NoticeBanner } from '../common/NoticeBanner';

export const AppLayout: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-950 flex flex-col font-sans">
      <Header />
      <NoticeBanner />
      <div className="flex-1 flex overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto bg-slate-900/60 p-4 lg:p-6 pb-16">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
