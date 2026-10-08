import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  LayoutDashboard,
  Map,
  Users,
  Cross,
  Library,
  Landmark,
  ScrollText,
  LogIn,
} from 'lucide-react';
import { useAuth } from '../core/hooks/useAuth';
import { LanguageSwitcher } from '../components/common/LanguageSwitcher';
import archdioceseLogo from '../../archidiocese-logo.png';

// ---------------------------------------------------------------------------
// Public, read-only landing page for ordinary (unauthenticated) viewers.
// Staff and admins use the "Sign in" button to access the internal system.
// ---------------------------------------------------------------------------

interface ReadOnlySection {
  icon: React.FC<{ className?: string }>;
  title: string;
  description: string;
}

export const HomePage: React.FC = () => {
  const { t } = useTranslation();
  const { isAuthenticated, isLoading } = useAuth();

  const readOnlySections: ReadOnlySection[] = [
    {
      icon: Landmark,
      title: t('home.sections.diocese_title'),
      description: t('home.sections.diocese_description'),
    },
    {
      icon: Users,
      title: t('home.sections.faithful_title'),
      description: t('home.sections.faithful_description'),
    },
    {
      icon: Cross,
      title: t('home.sections.sacraments_title'),
      description: t('home.sections.sacraments_description'),
    },
    {
      icon: Library,
      title: t('home.sections.ministries_title'),
      description: t('home.sections.ministries_description'),
    },
    {
      icon: ScrollText,
      title: t('home.sections.archives_title'),
      description: t('home.sections.archives_description'),
    },
    {
      icon: Map,
      title: t('home.sections.geography_title'),
      description: t('home.sections.geography_description'),
    },
  ];

  return (
    <div className="min-h-screen bg-[#f5f8fc]">
      {/* Top navigation bar */}
      <header className="bg-white/95 border-b border-[#dce6f0] sticky top-0 z-10 shadow-sm backdrop-blur">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img src={archdioceseLogo} alt="" className="h-12 w-12 object-contain" />
            <div>
              <h1 className="text-sm font-bold text-gray-900 leading-tight">{t('home.title')}</h1>
              <p className="text-[11px] text-gray-500 leading-tight">
                {t('home.header_subtitle')}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <LanguageSwitcher />
            {isLoading ? (
              <div className="px-4 py-2 text-sm text-gray-300">...</div>
            ) : isAuthenticated ? (
              <Link
                to="/dashboard"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-gray-800 text-white text-sm font-medium hover:bg-gray-900 transition-colors"
              >
                <LayoutDashboard className="w-4 h-4" />
                {t('home.go_to_dashboard')}
              </Link>
            ) : (
              <Link
                to="/login"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-brand-500 text-white text-sm font-medium hover:bg-brand-600 transition-colors"
              >
                <LogIn className="w-4 h-4" />
                {t('home.sign_in')}
              </Link>
            )}
          </div>
        </div>
      </header>

      {/* Hero */}
      <main>
        <section className="relative overflow-hidden border-b border-brand-100 bg-gradient-to-br from-[#eaf3fc] via-white to-[#fff9e8]">
          <div className="pointer-events-none absolute -right-20 -top-28 h-96 w-96 rounded-full border-[48px] border-gold-100/60" />
          <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-20 text-center">
            <div className="mx-auto mb-6 flex h-36 w-36 items-center justify-center rounded-full border border-gold-300/70 bg-white/80 p-4 shadow-[0_18px_50px_rgba(16,43,69,0.12)] ring-8 ring-white/60">
              <img
                src={archdioceseLogo}
                alt="Coat of arms of the Archdiocese of Kigali"
                className="h-full w-full object-contain"
              />
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 tracking-tight mb-4">
              {t('home.welcome_title')}
            </h2>
            <p className="max-w-2xl mx-auto text-base text-gray-600 mb-8">
              {t('home.welcome_body')}
            </p>
            <div className="flex flex-wrap items-center justify-center gap-3">
              {isLoading ? null : isAuthenticated ? (
                <Link
                  to="/dashboard"
                  className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-gray-800 text-white text-base font-medium hover:bg-gray-900 transition-colors"
                >
                  <LayoutDashboard className="w-5 h-5" />
                  {t('home.open_dashboard')}
                </Link>
              ) : (
                <Link
                  to="/login"
                  className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-brand-500 text-white text-base font-medium hover:bg-brand-600 transition-colors shadow-md"
                >
                  <LogIn className="w-5 h-5" />
                  {t('home.staff_sign_in')}
                </Link>
              )}
            </div>
          </div>
        </section>

        {/* Read-only information sections */}
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <h3 className="text-xl font-bold text-gray-900 mb-2">{t('home.discover_title')}</h3>
          <p className="text-sm text-gray-500 mb-8">
            {t('home.discover_subtitle')}
          </p>
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {readOnlySections.map((section) => {
              const Icon = section.icon;
              return (
                <div
                  key={section.title}
                  className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 hover:shadow-md transition-shadow"
                >
                  <div className="inline-flex items-center justify-center w-11 h-11 rounded-xl bg-brand-50 text-brand-500 mb-4">
                    <Icon className="w-6 h-6" />
                  </div>
                  <h4 className="text-base font-semibold text-gray-900 mb-1.5">{section.title}</h4>
                  <p className="text-sm text-gray-600 leading-relaxed">{section.description}</p>
                </div>
              );
            })}
          </div>
        </section>

        {/* Staff / admin call to action */}
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
          <div className="relative overflow-hidden rounded-2xl border border-brand-700 bg-gradient-to-br from-brand-900 via-brand-800 to-brand-700 text-white p-8 sm:p-10 text-center shadow-xl shadow-brand-900/15">
            <div className="pointer-events-none absolute -right-12 -top-20 h-64 w-64 rounded-full border-[32px] border-gold-500/15" />
            <h3 className="text-xl font-bold mb-2">{t('home.cta_title')}</h3>
            <p className="text-sm text-gray-300 max-w-xl mx-auto mb-6">
              {t('home.cta_body')}
            </p>
            {isAuthenticated ? (
              <Link
                to="/dashboard"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-white text-gray-900 text-base font-semibold hover:bg-gray-200 transition-colors"
              >
                <LayoutDashboard className="w-5 h-5" />
                {t('home.go_to_dashboard')}
              </Link>
            ) : (
              <Link
                to="/login"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-brand-500 text-white text-base font-semibold hover:bg-brand-600 transition-colors"
              >
                <LogIn className="w-5 h-5" />
                {t('home.sign_in_arkidi')}
              </Link>
            )}
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-100 py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-xs text-gray-400">
          {t('home.footer')}
        </div>
      </footer>
    </div>
  );
};
