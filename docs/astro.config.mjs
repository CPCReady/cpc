// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	integrations: [
		starlight({
			title: 'Documentation Site',
			tagline: 'v1.0.0',
			favicon: '/favicon.png',
			logo: {
				src: './src/assets/icon_512x512@2x.png',
			},
			social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/CPCReady/cpc' }],
			sidebar: [
				{
					label: 'Guides',
					items: [
						{ label: 'Installation', slug: 'guides/install' },
						{ label: 'Command Reference', slug: 'guides/commands' },
						{ label: 'Changelog', slug: 'guides/changelog' },
						{ label: 'Roadmap', slug: 'guides/roadmap' },
					],
				},
				{
					label: 'Reference',
					autogenerate: { directory: 'reference' },
				},
				],
		}),
	],
});
