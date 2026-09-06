'use client';

import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const router = useRouter();

  const handleContinue = () => {
    localStorage.setItem('govbridge_session', JSON.stringify({ role: 'citizen', loggedIn: true }));
    router.push('/');
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-100 px-6">
      <div className="w-full max-w-lg rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
        <p className="mb-2 text-xs font-semibold uppercase tracking-[0.2em] text-indigo-600">GovBridge</p>
        <h1 className="text-2xl font-bold text-slate-900">Synthetic login</h1>
        <p className="mt-4 text-slate-600">
          This portal simulates a secure citizen login and redirects you into the service dashboard.
        </p>
        <button
          type="button"
          onClick={handleContinue}
          className="mt-6 rounded-xl bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-500"
        >
          Continue with Keycloak
        </button>
      </div>
    </main>
  );
}
