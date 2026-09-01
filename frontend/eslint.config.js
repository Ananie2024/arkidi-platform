import js from '@eslint/js';
import globals from 'globals';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import tseslint from 'typescript-eslint';
import i18next from 'eslint-plugin-i18next';

export default tseslint.config(
  { ignores: ['dist'] },
  {
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
    },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
      i18next,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
      // i18n: forbid hardcoded user-facing strings landing in new code.
      // `mode: 'jsx-only'` checks JSX text children *and* JSX attribute
      // values (labels, placeholders, titles, button text…), while leaving
      // non-UI literals (API endpoints, query keys, form field names,
      // accessors, route paths) alone so the gate stays practical.
      //
      // The `t()`/`useTranslation`/`i18next.t()` calls are exempt by default
      // (see the plugin's `callees` defaults).
      'i18next/no-literal-string': [
        2,
        {
          framework: 'react',
          mode: 'jsx-only',
          // Symbols/punctuation rendered as JSX are not translatable copy.
          // (Extends the plugin defaults — `words` is shallow-merged.)
          words: {
            exclude: [
              '[0-9!-/:-@[-`{-~]+',
              '[A-Z_-]+',
              '\\u2629',
              '\\u2022',
              '\\u2026',
            ],
          },
          'jsx-attributes': {
            exclude: [
              '^className$',
              '^styleName$',
              '^style$',
              '^data-testid$',
              '^key$',
              '^href$',
              '^to$',
              '^id$',
              '^type$',
              '^variant$',
              '^size$',
              '^color$',
              '^value$',
              '^name$',
              '^accept$',
              '^maxLength$',
              '^min$',
              '^max$',
              '^step$',
              '^autoComplete$',
              '^aria-label$',
              // Route paths, layout props and example placeholders are not copy.
              '^path$',
              '^placeholder$',
              '^maxWidth$',
              '^height$',
              // Leaflet map configuration attributes.
              '^attribution$',
              '^url$',
            ],
          },
          'jsx-components': {
            exclude: ['^Trans$', '^Option$'],
          },
        },
      ],
    },
  },
  // Test files simulate UI with literal fixtures/assertions — the i18n gate
  // applies to shipped pages & components, not to test doubles.
  {
    files: ['**/*.test.{ts,tsx}', '**/*.spec.{ts,tsx}', 'src/test/**/*'],
    rules: {
      'i18next/no-literal-string': 'off',
    },
  },
);
