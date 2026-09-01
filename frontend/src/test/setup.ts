import '@testing-library/jest-dom/vitest';
import i18n from '../i18n/i18n';

// Pages under test resolve copy through i18next; pin English so assertions on
// the en.json catalog strings remain deterministic across host locales.
void i18n.changeLanguage('en');
