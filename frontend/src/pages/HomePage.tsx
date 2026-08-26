import React from 'react';
import { Link } from 'react-router-dom';
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

// ---------------------------------------------------------------------------
// Public, read-only landing page for ordinary (unauthenticated) viewers.
// Staff and admins use the "Sign in" button to access the internal system.
// ---------------------------------------------------------------------------

interface ReadOnlySection {
  icon: React.FC<{ className?: string }>;
  title: string;
  description: string;
}

const readOnlySections: ReadOnlySection[] = [
  {
    icon: Landmark,
    title: 'Diocese & Parishes',
    description:
      'Discover the parishes and ecclesiastical territory of the Archdiocese of Kigali through our public directory.',
  },
  {
    icon: Users,
    title: 'Faithful',
    description:
      'Public information about the community and pastoral care offered across the archdiocese.',
  },
  {
    icon: Cross,
    title: 'Sacraments',
    description:
      'General information about the administration of Baptism, Confirmation and Matrimony.',
  },
  {
    icon: Library,
    title: 'Clergy & Ministries',
    description:
      'Overview of the clergy, religious and pastoral ministries serving the local Church.',
  },
  {
    icon: ScrollText,
    title: 'Archives & History',
    description:
      'Historical records and documentation preserved by the Diocesan Archives.',
  },
  {
    icon: Map,
    title: 'Geography',
    description:
      'Explore the geographical footprint and territorial organization of the archdiocese.',
  },
];

export const HomePage: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top navigation bar */}
      <header className="bg-white border-b border-gray-100 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="inline-flex items-center justify-center w-9 h-9 rounded-lg bg-brand-500 text-white text-lg font-bold shadow-sm">
              ☩
            </div>
            <div>
              <h1 className="text-sm font-bold text-gray-900 leading-tight">Arkidi Platform</h1>
              <p className="text-[11px] text-gray-500 leading-tight">
                Archdiocese of Kigali &bull; Archidiocèse de Kigali
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
                Go to Dashboard
              </Link>
            ) : (
              <Link
                to="/login"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-brand-500 text-white text-sm font-medium hover:bg-brand-600 transition-colors"
              >
                <LogIn className="w-4 h-4" />
                Sign in
              </Link>
            )}
          </div>
        </div>
      </header>

      {/* Hero */}
      <main>
        <section className="bg-gradient-to-b from-brand-50 to-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-20 text-center">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-brand-500 text-white text-4xl font-bold mb-6 shadow-lg">
              ☩
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 tracking-tight mb-4">
              Welcome to the Arkidi Platform
            </h2>
            <p className="max-w-2xl mx-auto text-base text-gray-600 mb-8">
              The public portal of the Archdiocese of Kigali Ecclesiastical Management System.
              Browse general information about the archdiocese here; staff and administrators
              can sign in to manage records.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-3">
              {isLoading ? null : isAuthenticated ? (
                <Link
                  to="/dashboard"
                  className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-gray-800 text-white text-base font-medium hover:bg-gray-900 transition-colors"
                >
                  <LayoutDashboard className="w-5 h-5" />
                  Open my Dashboard
                </Link>
              ) : (
                <Link
                  to="/login"
                  className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-brand-500 text-white text-base font-medium hover:bg-brand-600 transition-colors shadow-md"
                >
                  <LogIn className="w-5 h-5" />
                  Staff &amp; Admin Sign in
                </Link>
              )}
            </div>
          </div>
        </section>

        {/* Read-only information sections */}
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <h3 className="text-xl font-bold text-gray-900 mb-2">Discover the Archdiocese</h3>
          <p className="text-sm text-gray-500 mb-8">
            Read-only information available to all visitors.
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
          <div className="rounded-2xl bg-gray-900 text-white p-8 sm:p-10 text-center">
            <h3 className="text-xl font-bold mb-2">Are you staff or an administrator?</h3>
            <p className="text-sm text-gray-300 max-w-xl mx-auto mb-6">
              Sign in to access the platform&apos;s internal tools for managing parishes,
              records, finances and more.
            </p>
            {isAuthenticated ? (
              <Link
                to="/dashboard"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-white text-gray-900 text-base font-semibold hover:bg-gray-200 transition-colors"
              >
                <LayoutDashboard className="w-5 h-5" />
                Go to Dashboard
              </Link>
            ) : (
              <Link
                to="/login"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-brand-500 text-white text-base font-semibold hover:bg-brand-600 transition-colors"
              >
                <LogIn className="w-5 h-5" />
                Sign in to Arkidi
              </Link>
            )}
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-100 py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-xs text-gray-400">
          Archdiocese of Kigali Ecclesiastical Management System &bull; Arkidi Platform
        </div>
      </footer>
    </div>
  );
};