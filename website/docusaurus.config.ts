import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'luxafor',
  tagline: 'Python driver and internet health monitor for the Luxafor Flag USB LED device',
  favicon: 'img/favicon.ico',

  url: 'https://joeblackwaslike.github.io',
  baseUrl: '/luxafor/',

  organizationName: 'joeblackwaslike',
  projectName: 'luxafor',

  onBrokenLinks: 'warn',
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  markdown: {
    mermaid: true,
  },

  themes: ['@docusaurus/theme-mermaid'],

  presets: [
    [
      'classic',
      {
        docs: {
          routeBasePath: '/',
          sidebarPath: './sidebars.ts',
          editUrl: 'https://github.com/joeblackwaslike/luxafor/tree/main/website/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    navbar: {
      title: 'luxafor',
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docs',
          position: 'left',
          label: 'Docs',
        },
        {
          href: '/luxafor/how-it-works.html',
          label: 'How It Works',
          position: 'left',
          target: '_self',
        },
        {
          href: 'https://github.com/joeblackwaslike/luxafor',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {label: 'Getting Started', to: '/'},
            {label: 'CLI Reference', to: '/cli-reference'},
            {label: 'Monitor Guide', to: '/guides/monitor'},
          ],
        },
        {
          title: 'More',
          items: [
            {label: 'GitHub', href: 'https://github.com/joeblackwaslike/luxafor'},
            {label: 'How It Works', href: '/luxafor/how-it-works.html'},
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Joe Black. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['bash', 'python', 'toml'],
    },
    mermaid: {
      theme: {light: 'neutral', dark: 'dark'},
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
