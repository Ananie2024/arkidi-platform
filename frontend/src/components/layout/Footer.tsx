import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-white border-t border-gray-200 py-3 px-6 text-center text-xs text-gray-500">
      <div className="flex flex-col sm:flex-row items-center justify-between gap-2 max-w-7xl mx-auto">
        <div>Archdiocese of Kigali (Archidiocèse de Kigali) &bull; Official Digital Platform</div>
        <div className="text-gray-400">Strictly Confidential & Canonical Data Protection</div>
      </div>
    </footer>
  );
};
