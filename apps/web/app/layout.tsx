import Link from 'next/link';
import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'GovBridge',
  description: 'GovBridge identity and service workflow demo',
};

const navItems = [
  { href: '/', label: 'Dashboard' },
  { href: '/services', label: 'Services' },
  { href: '/review', label: 'Review queue' },
  { href: '/decision', label: 'Decision center' },
  { href: '/admin', label: 'Admin audit' },
  { href: '/login', label: 'Login' },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#f4f5f7] text-slate-900 antialiased">
        <div className="min-h-screen">
          <header className="sticky top-0 z-30 border-b border-slate-200 bg-[#f8fafc]/90 backdrop-blur-xl">
            <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
              <Link href="/" className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#0b3d91] text-sm font-bold text-white shadow-sm">
                  G
                </div>
                <div>
                  <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-[#0b3d91]">GovBridge</p>
                  <p className="text-sm font-semibold text-slate-800">Citizen Services</p>
                </div>
              </Link>

              <nav className="hidden items-center gap-2 md:flex">
                {navItems.map((item) => (
                  <Link
                    key={item.href}
                    href={item.href}
                    className="rounded-full px-3 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"
                  >
                    {item.label}
                  </Link>
                ))}
              </nav>

              <div className="flex items-center gap-3">
                <button className="hidden rounded-full border border-slate-200 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 md:inline-flex">
                  Hindi
                </button>
                <Link
                  href="/login"
                  className="rounded-full bg-[#0b3d91] px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-[#0a2f72]"
                >
                  Sign in
                </Link>
              </div>
            </div>
          </header>

          <main>{children}</main>
        </div>
      </body>
    </html>
  );
}
