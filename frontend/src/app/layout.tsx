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
  metadataBase: new URL('https://aegiscloud.in'),
  title: {
    default: 'Aegis Cloud - AI-Powered Windows Endpoint Management',
    template: '%s | Aegis Cloud',
  },
  description:
    'Manage Windows PCs remotely with AI. Monitor devices, automate tasks, and control endpoints from anywhere. Free trial available. Trusted by IT professionals and MSPs worldwide.',
  keywords: [
    'remote windows management',
    'windows endpoint management',
    'ai pc management',
    'remote desktop control',
    'windows automation',
    'remote monitoring',
    'endpoint management platform',
    'windows agent',
    'remote pc control',
    'it management tool',
    'msp software',
    'windows service management',
    'manage windows remotely',
    'ai powered endpoint management',
    'remote device management',
    'windows remote admin',
    'cloud pc management',
    'remote system administration',
    'enterprise endpoint management',
    'windows automation tool'
  ],
  authors: [{ name: 'Aegis Cloud', url: 'https://aegiscloud.in' }],
  creator: 'Aegis Cloud',
  publisher: 'Aegis Cloud',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  alternates: {
    canonical: '/',
  },
  openGraph: {
    title: 'Aegis Cloud - AI-Powered Windows Endpoint Management',
    description:
      'Manage Windows PCs remotely with AI. Monitor, control, and automate endpoints from anywhere. Free trial available.',
    url: 'https://aegiscloud.in',
    type: 'website',
    locale: 'en_US',
    siteName: 'Aegis Cloud',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Aegis Cloud - AI Windows Management Dashboard',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Aegis Cloud - AI-Powered Windows Endpoint Management',
    description: 'Manage Windows PCs remotely with AI. Monitor, control, and automate endpoints from anywhere.',
    images: ['/og-image.png'],
    creator: '@aegiscloud',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: 'your-google-verification-code',
  },
  category: 'technology',
};

const jsonLd = {
  '@context': 'https://schema.org',
  '@type': 'SoftwareApplication',
  name: 'Aegis Cloud',
  operatingSystem: 'Windows',
  applicationCategory: 'BusinessApplication',
  offers: {
    '@type': 'Offer',
    price: '0',
    priceCurrency: 'USD',
    description: 'Free plan available with up to 2 devices',
  },
  aggregateRating: {
    '@type': 'AggregateRating',
    ratingValue: '4.8',
    ratingCount: '156',
  },
  description:
    'AI-powered remote Windows endpoint management platform. Monitor, control, and automate Windows PCs from anywhere.',
  featureList: [
    'AI-powered device management',
    'Real-time monitoring',
    'Remote task automation',
    'Enterprise-grade security',
    'File management',
    'Service control',
    'Process management',
    'Automated maintenance',
  ],
  screenshot: 'https://aegiscloud.in/og-image.png',
  softwareVersion: '1.0.0',
  author: {
    '@type': 'Organization',
    name: 'Aegis Cloud',
    url: 'https://aegiscloud.in',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning className={`${inter.variable} ${jetbrains.variable}`}>
      <head>
        <meta name="theme-color" content="#0f0d2e" />
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <link rel="manifest" href="/manifest.json" />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      </head>
      <body className="font-sans min-h-screen bg-background antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
