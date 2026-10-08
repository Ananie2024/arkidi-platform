import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useQuery } from '@tanstack/react-query';
import {
  BookOpen,
  Building2,
  Church,
  UsersRound,
  UserRound,
  LayoutDashboard,
  Map,
  Users,
  Cross,
  Library,
  Landmark,
  ScrollText,
  LogIn,
  ArrowDown,
} from 'lucide-react';
import { useAuth } from '../core/hooks/useAuth';
import { LanguageSwitcher } from '../components/common/LanguageSwitcher';
import { domainApi } from '../core/api/domain';
import archdioceseLogo from '../../archidiocese-logo.png';

// ---------------------------------------------------------------------------
// Public landing page. The staff portal remains available as a secondary link.
// ---------------------------------------------------------------------------

interface ReadOnlySection {
  icon: React.FC<{ className?: string }>;
  title: string;
  description: string;
}

export const HomePage: React.FC = () => {
  const { t } = useTranslation();
  const { isAuthenticated, isLoading } = useAuth();
  const overviewQuery = useQuery({
    queryKey: ['public-overview'],
    queryFn: domainApi.getPublicOverview,
    staleTime: 5 * 60 * 1000,
  });

  const statistics = overviewQuery.data?.statistics;
  const statisticCards = statistics
    ? [
        { label: t('home.stats_deaneries'), value: statistics.deaneries, icon: Building2 },
        { label: t('home.stats_parishes'), value: statistics.parishes, icon: Church },
        { label: t('home.stats_priests'), value: statistics.active_priests, icon: UserRound },
        {
          label: t('home.stats_faithful'),
          value: statistics.registered_faithful,
          icon: UsersRound,
        },
      ]
    : [];

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
          <nav aria-label="Main navigation" className="flex items-center gap-4 sm:gap-6">
            <LanguageSwitcher />
            {isLoading ? (
              <span className="text-sm text-gray-400">...</span>
            ) : isAuthenticated ? (
              <Link
                to="/dashboard"
                className="inline-flex items-center gap-2 rounded-full border border-brand-200 px-4 py-2 text-sm font-semibold text-brand-800 transition-colors hover:border-brand-400 hover:bg-brand-50"
              >
                <LayoutDashboard className="w-4 h-4" />
                {t('home.go_to_dashboard')}
              </Link>
            ) : (
              <Link
                to="/login"
                className="hidden items-center gap-1.5 py-2 text-xs font-medium text-gray-500 transition-colors hover:text-brand-700 sm:inline-flex sm:text-sm"
              >
                <LogIn className="h-3.5 w-3.5" />
                {t('home.staff_portal')}
              </Link>
            )}
          </nav>
        </div>
      </header>

      {/* Hero */}
      <main>
        <section className="relative overflow-hidden border-b border-brand-100 bg-gradient-to-br from-[#eaf3fc] via-white to-[#fff9e8]">
          <div className="pointer-events-none absolute -right-20 -top-28 h-96 w-96 rounded-full border-[48px] border-gold-100/60" />
          <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-20 text-center">
            <p className="mb-5 text-[11px] font-bold uppercase tracking-[0.22em] text-brand-700">
              {t('home.hero_kicker')}
            </p>
            <div className="mx-auto mb-6 flex h-36 w-36 items-center justify-center rounded-full border border-gold-300/70 bg-white/80 p-4 shadow-[0_18px_50px_rgba(16,43,69,0.12)] ring-8 ring-white/60">
              <img
                src={archdioceseLogo}
                alt="Coat of arms of the Archdiocese of Kigali"
                className="h-full w-full object-contain"
              />
            </div>
            <h2 className="text-3xl sm:text-5xl font-bold text-brand-900 tracking-tight mb-4">
              {t('home.welcome_title')}
            </h2>
            <p className="max-w-2xl mx-auto text-base sm:text-lg text-gray-600 leading-relaxed mb-8">
              {t('home.welcome_body')}
            </p>
            <div className="flex flex-wrap items-center justify-center gap-3">
              {isLoading ? null : isAuthenticated ? (
                <Link
                  to="/dashboard"
                  className="inline-flex items-center gap-2 rounded-full bg-brand-700 px-6 py-3 text-sm font-semibold text-white shadow-md transition hover:bg-brand-800"
                >
                  <LayoutDashboard className="w-5 h-5" />
                  {t('home.open_dashboard')}
                </Link>
              ) : (
                <a
                  href="#discover"
                  className="inline-flex items-center gap-2 rounded-full bg-brand-700 px-6 py-3 text-sm font-semibold text-white shadow-md shadow-brand-900/15 transition hover:bg-brand-800"
                >
                  {t('home.explore_button')}
                  <ArrowDown className="h-4 w-4" />
                </a>
              )}
            </div>
          </div>
        </section>

        <section className="border-y border-gray-200 bg-white" aria-labelledby="public-stats-title">
          <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8 sm:py-12">
            <div className="mb-6 flex flex-col justify-between gap-2 sm:flex-row sm:items-end">
              <div>
                <h3 id="public-stats-title" className="text-xl font-bold text-brand-900">
                  {t('home.stats_title')}
                </h3>
                <p className="mt-1 text-sm text-gray-500">{t('home.stats_subtitle')}</p>
              </div>
            </div>
            {overviewQuery.isPending ? (
              <div
                className="grid grid-cols-2 gap-3 lg:grid-cols-4"
                aria-label={t('common.loading')}
              >
                {[0, 1, 2, 3].map((item) => (
                  <div
                    key={item}
                    className="h-28 animate-pulse rounded-2xl border border-gray-100 bg-gray-50"
                  />
                ))}
              </div>
            ) : overviewQuery.isError ? (
              <p
                role="status"
                className="rounded-xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm text-gray-600"
              >
                {t('home.stats_unavailable')}
              </p>
            ) : (
              <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
                {statisticCards.map(({ label, value, icon: Icon }) => (
                  <article
                    key={label}
                    className="rounded-2xl border border-gray-200 bg-gradient-to-br from-white to-brand-50/80 p-5 shadow-sm"
                  >
                    <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl border border-gold-200 bg-white text-brand-700">
                      <Icon className="h-5 w-5" aria-hidden="true" />
                    </div>
                    <p className="text-2xl font-bold tracking-tight text-brand-900 sm:text-3xl">
                      {value.toLocaleString()}
                    </p>
                    <h4 className="mt-1 text-xs font-semibold uppercase tracking-wide text-gray-500 sm:text-sm">
                      {label}
                    </h4>
                  </article>
                ))}
              </div>
            )}
          </div>
        </section>

        <section
          className="mx-auto max-w-7xl px-4 py-12 sm:px-6 sm:py-16 lg:px-8"
          aria-labelledby="organigram-title"
        >
          <div className="mb-8 max-w-2xl">
            <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.18em] text-brand-600">
              {t('home.organigram_kicker')}
            </p>
            <h3 id="organigram-title" className="text-2xl font-bold text-brand-900 sm:text-3xl">
              {t('home.organigram_title')}
            </h3>
            <p className="mt-2 text-sm leading-relaxed text-gray-600">
              {t('home.organigram_subtitle')}
            </p>
          </div>
          {overviewQuery.isPending ? (
            <div className="h-48 animate-pulse rounded-3xl border border-gray-200 bg-white" />
          ) : overviewQuery.isError ? (
            <p
              role="status"
              className="rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm text-gray-600"
            >
              {t('home.organigram_unavailable')}
            </p>
          ) : (
            <div>
              <div className="mx-auto flex max-w-xl items-center gap-4 rounded-2xl border border-gold-300 bg-gradient-to-r from-white via-brand-50 to-[#fffbed] p-5 shadow-sm sm:p-6">
                <img src={archidioceseLogo} alt="" className="h-14 w-14 shrink-0 object-contain" />
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-brand-600">
                    {t('home.organigram_root')}
                  </p>
                  <h4 className="mt-1 text-lg font-bold text-brand-900">
                    {overviewQuery.data.organigram.name}
                  </h4>
                </div>
              </div>
              <div className="mx-auto h-8 w-px bg-gold-400" aria-hidden="true" />
              {overviewQuery.data.organigram.deaneries.length ? (
                <div className="grid gap-4 border-t border-gold-300 pt-6 sm:grid-cols-2 xl:grid-cols-3">
                  {overviewQuery.data.organigram.deaneries.map((deanery, index) => (
                    <article
                      key={`${deanery.name}-${index}`}
                      className="relative rounded-2xl border border-gray-200 bg-white p-5 shadow-sm before:absolute before:-top-[25px] before:left-1/2 before:h-6 before:w-px before:bg-gold-300"
                    >
                      <div className="flex items-start justify-between gap-3 border-b border-gray-100 pb-3">
                        <div>
                          <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-brand-500">
                            {t('home.organigram_deanery')}
                          </p>
                          <h4 className="mt-1 font-semibold text-brand-900">{deanery.name}</h4>
                        </div>
                        <span className="rounded-full border border-gold-200 bg-gold-50 px-2.5 py-1 text-xs font-semibold text-brand-800">
                          {t('home.organigram_parish', { count: deanery.parishes.length })}
                        </span>
                      </div>
                      {deanery.parishes.length ? (
                        <ul className="mt-3 space-y-2">
                          {deanery.parishes.map((parish) => (
                            <li key={parish} className="flex items-center gap-2 text-sm text-gray-600">
                              <span
                                className="h-1.5 w-1.5 shrink-0 rounded-full bg-gold-500"
                                aria-hidden="true"
                              />
                              {parish}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="mt-3 text-xs text-gray-400">{t('home.organigram_no_parishes')}</p>
                      )}
                    </article>
                  ))}
                </div>
              ) : (
                <p className="rounded-xl border border-gray-200 bg-white px-4 py-6 text-center text-sm text-gray-500">
                  {t('home.organigram_empty')}
                </p>
              )}
            </div>
          )}
        </section>

        {/* Read-only information sections */}
        <section
          id="discover"
          className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14 sm:py-16 scroll-mt-24"
        >
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
                  className="group bg-white rounded-2xl border border-gray-200 shadow-sm p-6 transition-all duration-200 hover:-translate-y-1 hover:border-gold-300 hover:shadow-lg hover:shadow-brand-900/5"
                >
                  <div className="inline-flex items-center justify-center w-11 h-11 rounded-xl border border-gold-200 bg-brand-50 text-brand-600 transition-colors group-hover:bg-gold-50 group-hover:text-brand-800">
                    <Icon className="w-6 h-6" />
                  </div>
                  <h4 className="text-base font-semibold text-gray-900 mb-1.5">{section.title}</h4>
                  <p className="text-sm text-gray-600 leading-relaxed">{section.description}</p>
                </div>
              );
            })}
          </div>
        </section>

        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-14 sm:pb-16">
          <div className="relative overflow-hidden rounded-3xl border border-brand-100 bg-gradient-to-r from-white via-brand-50 to-[#fffbed] p-7 sm:p-10">
            <div className="pointer-events-none absolute -right-12 -top-20 h-64 w-64 rounded-full border-[32px] border-gold-200/50" />
            <div className="relative flex flex-col items-start gap-5 sm:flex-row sm:items-center">
              <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl border border-gold-200 bg-white text-brand-700 shadow-sm">
                <BookOpen className="h-7 w-7" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-brand-900">{t('home.public_note_title')}</h3>
                <p className="mt-2 max-w-3xl text-sm leading-relaxed text-gray-600">
                  {t('home.public_note_body')}
                </p>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-100 py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col items-center justify-between gap-3 text-xs text-gray-400 sm:flex-row">
          <span>{t('home.footer')}</span>
          {!isAuthenticated && !isLoading && (
            <Link to="/login" className="text-gray-400 transition-colors hover:text-brand-700">
              {t('home.staff_portal')}
            </Link>
          )}
        </div>
      </footer>
    </div>
  );
};
