import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  site: 'https://javiermunrom.github.io',
  base: '/de-sputnik-a-starlink',
  integrations: [
    tailwind({
      applyBaseStyles: false,
    }),
  ],
});
