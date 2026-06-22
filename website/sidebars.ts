import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  docs: [
    'intro',
    'installation',
    'getting-started',
    'cli-reference',
    {
      type: 'category',
      label: 'Guides',
      items: [
        'guides/monitor',
        'guides/hid-protocol',
        'guides/webhook',
      ],
    },
    'architecture',
  ],
};

export default sidebars;
