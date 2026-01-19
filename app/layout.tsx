import './globals.css';
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'deepkrak3n - Check Availability Instantly',
  description: 'Check username availability across 100+ platforms instantly with deepkrak3n. Search Twitter, Instagram, GitHub, Discord, Twitch, and more all at once.',
  keywords: 'username checker, social media username, available usernames, username search, platform checker, deepkrak3n',
  icons: {
    icon: [
      { url: '/favicon-16.png?v=2', sizes: '16x16', type: 'image/png' },
      { url: '/favicon-32.png?v=2', sizes: '32x32', type: 'image/png' },
      { url: '/favicon-64.png?v=2', sizes: '64x64', type: 'image/png' },
      { url: '/favicon-128.png?v=2', sizes: '128x128', type: 'image/png' },
      { url: '/favicon-256.png?v=2', sizes: '256x256', type: 'image/png' },
      { url: '/favicon-512.png?v=2', sizes: '512x512', type: 'image/png' },
      { url: '/favicon.png?v=2', type: 'image/png' },
    ],
    shortcut: '/favicon-32.png?v=2',
    apple: '/favicon-180.png?v=2',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className={`${inter.className} bg-slate-950 text-white`}>{children}</body>
    </html>
  );
}