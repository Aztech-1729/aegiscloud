import type { Metadata } from 'next';
import { Inter, JetBrains_Mono } from 'next/font/google';
import './globals.css';
import Providers from '@/components/providers';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

const jetbrains = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  display: 'swap',
});

export const metadata: Metadata = {
  title: {
    default: 'Aegis Cloud — AI Remote Windows Manager',
    template: '%s | Aegis Cloud',
  },
  description:
    'Securely control and manage your Windows PCs from anywhere through a modern web dashboard powered by AI.',
  keywords: [
    'remote PC management',
    'Windows',
    'cloud',
    'AI',
    'device management',
    'SaaS',
    'remote desktop',
  ],
  authors: [{ name: 'Aegis Cloud' }],
  creator: 'Aegis Cloud',
  publisher: 'Aegis Cloud',
  openGraph: {
    title: 'Aegis Cloud — AI Remote Windows Manager',
    description:
      'Securely control and manage your Windows PCs from anywhere through a modern web dashboard powered by AI.',
    type: 'website',
    locale: 'en_US',
    siteName: 'Aegis Cloud',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Aegis Cloud — AI Remote Windows Manager',
    description: 'Manage your Windows PCs from anywhere with AI.',
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning className={`${inter.variable} ${jetbrains.variable}`}>
      <head>
        <meta name="theme-color" content="#0f0d2e" />
      </head>
      <body className="font-sans min-h-screen bg-background antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
