'use client';

import { useEffect, useState } from 'react';

const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export default function ReviewQueuePage() {
  const [cases, setCases] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadQueue = async () => {
      try {
        const response = await fetch(`${apiBase}/api/v1/review-queue`);
        if (!response.ok) throw new Error('queue unavailable');
        const payload = await response.json();
        setCases(payload.cases || []);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    loadQueue();
  }, []);

  return (
    <main className="min-h-screen bg-[#f4f5f7] text-slate-900">
      <div className="mx-auto max-w-7xl px-6 py-8">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#0b3d91]">Officer portal</p>
            <h1 className="mt-2 text-3xl font-bold">Review queue</h1>
          </div>
          <button className="rounded-full bg-[#0b3d91] px-4 py-2 text-sm font-medium text-white">New review</button>
        </div>

        <section className="mb-6 grid gap-4 md:grid-cols-3">
          <StatCard label="Pending" value={cases.filter((item) => item.status === 'UNDER_REVIEW').length} accent="amber" />
          <StatCard label="In review" value={cases.filter((item) => item.status === 'IN_REVIEW').length} accent="blue" />
          <StatCard label="Decisioned" value={cases.filter((item) => item.status === 'DECISION_MADE').length} accent="green" />
        </section>

        <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Queue</p>
              <h2 className="mt-2 text-xl font-bold">Actionable cases</h2>
            </div>
          </div>

          {loading ? (
            <div className="rounded-2xl bg-slate-50 p-4 text-sm text-slate-500">Loading queue…</div>
          ) : cases.length === 0 ? (
            <div className="rounded-2xl bg-slate-50 p-4 text-sm text-slate-500">No cases need review.</div>
          ) : (
            <div className="overflow-hidden rounded-2xl border border-slate-200">
              <table className="min-w-full divide-y divide-slate-200 text-left">
                <thead className="bg-slate-50 text-xs uppercase tracking-[0.2em] text-slate-500">
                  <tr>
                    <th className="px-4 py-3">Case ID</th>
                    <th className="px-4 py-3">Applicant</th>
                    <th className="px-4 py-3">Service</th>
                    <th className="px-4 py-3">Priority</th>
                    <th className="px-4 py-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 bg-white">
                  {cases.map((item) => (
                    <tr key={item.case_id} className="hover:bg-slate-50">
                      <td className="px-4 py-3 font-medium text-slate-900">{item.case_id}</td>
                      <td className="px-4 py-3 text-slate-700">{item.applicant_name}</td>
                      <td className="px-4 py-3 text-slate-700">{item.service_id}</td>
                      <td className="px-4 py-3">
                        <span className="rounded-full bg-amber-100 px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-amber-700">
                          {item.review_priority}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span className="rounded-full bg-blue-100 px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-blue-700">
                          {item.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
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
