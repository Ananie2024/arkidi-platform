import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Button } from '../../components/common/Button';
import { Scroll, Heart, Award, Shield, FileCheck } from 'lucide-react';
import { CertificateGeneratorModal } from './CertificateGeneratorModal';

export const SacramentsOverviewPage: React.FC = () => {
  const { t } = useTranslation();
  const [isCertModalOpen, setIsCertModalOpen] = useState(false);

  const sacramentCards = [
    { title: t('sacraments.card_baptism'), desc: t('sacraments.card_baptism_desc'), link: '/sacraments/baptism', icon: Scroll, color: 'text-blue-600 bg-blue-50' },
    { title: t('sacraments.card_confirmation'), desc: t('sacraments.card_confirmation_desc'), link: '/sacraments/confirmation', icon: Award, color: 'text-amber-600 bg-amber-50' },
    { title: t('sacraments.card_matrimony'), desc: t('sacraments.card_matrimony_desc'), link: '/sacraments/matrimony', icon: Heart, color: 'text-rose-600 bg-rose-50' },
    { title: t('sacraments.card_holy_orders'), desc: t('sacraments.card_holy_orders_desc'), link: '/sacraments', icon: Shield, color: 'text-purple-600 bg-purple-50' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-gray-900">{t('sacraments.overview_title')}</h1>
          <p className="text-xs text-gray-500 mt-0.5">{t('sacraments.overview_subtitle')}</p>
        </div>
        <Button size="sm" onClick={() => setIsCertModalOpen(true)}>
          <FileCheck className="w-4 h-4 mr-1.5" /> {t('sacraments.issue_qr')}
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
