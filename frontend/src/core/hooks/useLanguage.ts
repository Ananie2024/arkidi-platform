import { useTranslation } from 'react-i18next';

export const useLanguage = () => {
  const { i18n, t } = useTranslation();

  const changeLanguage = (lang: 'en' | 'fr' | 'rw') => {
    i18n.changeLanguage(lang);
    localStorage.setItem('i18nextLng', lang);
  };

  return {
    currentLanguage: (i18n.language || 'en').substring(0, 2),
    changeLanguage,
    t,
  };
};
