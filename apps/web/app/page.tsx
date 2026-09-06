'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';

type ServiceItem = {
  id: string;
  name: string;
  description: string;
  provider: string;
  purpose: string;
};

type CaseSummary = {
  case_id: string;
  status: string;
  service_id: string;
  applicant_name: string;
  decision?: { decision?: string; reason?: string };
};

type NotificationItem = {
  case_id: string;
  event: string;
  message: string;
  status: string;
};

const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export default function HomePage() {
  const [services, setServices] = useState<ServiceItem[]>([]);
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [stats, setStats] = useState({ active_cases: 0, completed_cases: 0, total_services: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const response = await fetch(`${apiBase}/api/v1/citizen/dashboard`);
        if (!response.ok) {
          throw new Error('dashboard unavailable');
        }
        const data = await response.json();
        setServices(data.services ?? []);
        setCases(data.cases ?? []);
        setNotifications(data.notifications ?? []);
        setStats(data.stats ?? { active_cases: 0, completed_cases: 0, total_services: 0 });
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
  }, []);

  const caseCounts = useMemo(
    () => ({
      approved: cases.filter((entry) => entry.decision?.decision === 'approved').length,
      underReview: cases.filter((entry) => entry.status === 'UNDER_REVIEW').length,
      total: cases.length,
    }),
    [cases],
  );

  return (
    <main className="min-h-screen bg-[#f4f5f7] text-slate-900">
      <div className="border-b border-slate-200 bg-[#f8fafc]">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#0b3d91] text-sm font-bold text-white">
              G
            </div>
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-[#0b3d91]">Government services</p>
              <h1 className="text-lg font-bold">Citizen Portal</h1>
            </div>
          </div>
          <div className="flex items-center gap-3 text-sm text-slate-600">
            <button className="rounded-full border border-slate-200 bg-white px-3 py-1.5">Hindi</button>
            <button className="rounded-full bg-[#0b3d91] px-3 py-1.5 font-medium text-white">Sign in</button>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-7xl px-6 py-8">
        <section className="rounded-3xl border border-slate-200 bg-gradient-to-r from-[#0b3d91] to-[#2d5bb7] p-8 text-white shadow-sm">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-blue-100">Citizen services</p>
              <h2 className="mt-3 text-3xl font-bold md:text-4xl">Apply, track, and resolve government services</h2>
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm md:min-w-[280px]">
              <div className="rounded-2xl bg-white/10 p-3 backdrop-blur-sm">
                <div className="text-2xl font-bold">{stats.active_cases}</div>
                <div className="text-blue-100">Active cases</div>
              </div>
              <div className="rounded-2xl bg-white/10 p-3 backdrop-blur-sm">
                <div className="text-2xl font-bold">{stats.completed_cases}</div>
                <div className="text-blue-100">Completed</div>
              </div>
            </div>
          </div>
        </section>

        <section className="mt-8 grid gap-4 md:grid-cols-3">
          <StatCard label="Total services" value={stats.total_services} accent="blue" />
          <StatCard label="Approved" value={caseCounts.approved} accent="green" />
          <StatCard label="In review" value={caseCounts.underReview} accent="amber" />
        </section>

        <section className="mt-8 grid gap-6 xl:grid-cols-[1.6fr_0.9fr]">
          <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-5 flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Popular services</p>
                <h3 className="mt-2 text-xl font-bold text-slate-900">Available schemes</h3>
              </div>
              <button className="rounded-full border border-slate-200 px-3 py-1.5 text-sm font-medium text-slate-700">View all</button>
            </div>

            {loading ? (
              <div className="rounded-2xl bg-slate-50 p-4 text-sm text-slate-500">Loading services…</div>
            ) : (
              <div className="grid gap-4 md:grid-cols-2">
                {services.map((service) => (
                  <div key={service.id} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#0b3d91]">{service.provider}</p>
                        <h4 className="mt-2 text-lg font-bold text-slate-900">{service.name}</h4>
                      </div>
                      <span className="rounded-full bg-emerald-50 px-2 py-1 text-xs font-medium text-emerald-700">Active</span>
                    </div>
                    <p className="mt-3 text-sm leading-6 text-slate-600">{service.description}</p>
                    <div className="mt-4 flex items-center justify-between">
                      <span className="text-xs uppercase tracking-[0.2em] text-slate-500">{service.purpose}</span>
                      <Link href="/services" className="rounded-full bg-[#0b3d91] px-3 py-1.5 text-sm font-medium text-white">
                        Apply now
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="space-y-6">
            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Recent updates</p>
              <div className="mt-5 space-y-4">
                {notifications.length === 0 ? (
                  <div className="rounded-2xl bg-slate-50 p-4 text-sm text-slate-500">No updates yet.</div>
                ) : (
                  notifications.slice(0, 3).map((item) => (
                    <div key={`${item.case_id}-${item.event}`} className="rounded-2xl bg-slate-50 p-4">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-semibold text-slate-800">{item.event}</p>
                        <span className="rounded-full bg-blue-100 px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-blue-700">
                          {item.status}
                        </span>
                      </div>
                      <p className="mt-2 text-sm text-slate-600">{item.message}</p>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Quick actions</p>
              <div className="mt-4 grid gap-3">
                <Link href="/cases/overview" className="rounded-2xl border border-slate-200 bg-slate-50 p-3 text-left text-sm font-medium text-slate-700">
                  My applications
                </Link>
                <Link href="/services" className="rounded-2xl border border-slate-200 bg-slate-50 p-3 text-left text-sm font-medium text-slate-700">
                  Consent history
                </Link>
                <Link href="/review" className="rounded-2xl border border-slate-200 bg-slate-50 p-3 text-left text-sm font-medium text-slate-700">
                  Documents
                </Link>
              </div>
            </div>
          </div>
        </section>

        <section className="mt-8 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">My cases</p>
              <h3 className="mt-2 text-xl font-bold text-slate-900">Case tracker</h3>
            </div>
            <Link href="/services" className="rounded-full bg-[#0b3d91] px-4 py-2 text-sm font-medium text-white">
              New application
            </Link>
          </div>

          <div className="overflow-hidden rounded-2xl border border-slate-200">
            <table className="min-w-full divide-y divide-slate-200 text-left">
              <thead className="bg-slate-50 text-xs uppercase tracking-[0.2em] text-slate-500">
                <tr>
                  <th className="px-4 py-3">Case ID</th>
                  <th className="px-4 py-3">Service</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Decision</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 bg-white">
                {cases.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-4 py-6 text-center text-sm text-slate-500">
                      No cases created yet.
                    </td>
                  </tr>
                ) : (
                  cases.map((entry) => (
                    <tr key={entry.case_id} className="hover:bg-slate-50">
                      <td className="px-4 py-3 font-medium text-slate-900">{entry.case_id}</td>
                      <td className="px-4 py-3 text-slate-700">{entry.service_id}</td>
                      <td className="px-4 py-3">
                        <span className="rounded-full bg-blue-100 px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-blue-700">
                          {entry.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-slate-700">{entry.decision?.decision || 'Pending'}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </main>
  );
}

function StatCard({ label, value, accent }: { label: string; value: number; accent: 'blue' | 'green' | 'amber' }) {
  const tones = {
    blue: 'bg-blue-50 text-blue-700',
    green: 'bg-emerald-50 text-emerald-700',
    amber: 'bg-amber-50 text-amber-700',
  };

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold uppercase tracking-[0.2em] ${tones[accent]}`}>
        {label}
      </div>
      <div className="mt-4 text-3xl font-bold text-slate-900">{value}</div>
    </div>
  );
}
