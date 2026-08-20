import React, { useState } from 'react';
import { Button } from '../../components/common/Button';
import { Scroll, Heart, Award, Shield, FileCheck } from 'lucide-react';
import { CertificateGeneratorModal } from './CertificateGeneratorModal';

export const SacramentsOverviewPage: React.FC = () => {
  const [isCertModalOpen, setIsCertModalOpen] = useState(false);

  const sacramentCards = [
    { title: 'Baptism Register', desc: 'Registre des Baptêmes / Igitabo cya Batisimu', link: '/sacraments/baptism', icon: Scroll, color: 'text-blue-600 bg-blue-50' },
    { title: 'Confirmation Register', desc: 'Registre des Confirmations / Gukomezwa', link: '/sacraments/confirmation', icon: Award, color: 'text-amber-600 bg-amber-50' },
    { title: 'Matrimony Register', desc: 'Registre des Mariages / Ugushyingirwa', link: '/sacraments/matrimony', icon: Heart, color: 'text-rose-600 bg-rose-50' },
    { title: 'Holy Orders & Vows', desc: 'Registre des Ordinations et Vœux Religieux', link: '/sacraments', icon: Shield, color: 'text-purple-600 bg-purple-50' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Canonical Sacramental Registers</h1>
          <p className="text-xs text-gray-500 mt-0.5">Catholic registers, Act numbers, Volume tracking and QR Certificate issuance</p>
        </div>
        <Button size="sm" onClick={() => setIsCertModalOpen(true)}>
          <FileCheck className="w-4 h-4 mr-1.5" /> Issue QR Certificate
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {sacramentCards.map((card, i) => {
          const Icon = card.icon;
          return (
            <a key={i} href={card.link} className="block p-5 bg-white rounded-xl border border-gray-200 shadow-sm hover:border-brand-300 hover:shadow-md transition-all">
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-3 ${card.color}`}>
                <Icon className="w-5 h-5" />
              </div>
              <h3 className="font-semibold text-gray-900 text-sm">{card.title}</h3>
              <p className="text-xs text-gray-500 mt-1">{card.desc}</p>
            </a>
          );
        })}
      </div>

      <CertificateGeneratorModal isOpen={isCertModalOpen} onClose={() => setIsCertModalOpen(false)} />
    </div>
  );
};
