'use client';

import { useEffect, useState } from 'react';

const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export default function CaseDetailPage({ params }: { params: { caseId: string } }) {
  const [caseData, setCaseData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadCase = async () => {
      try {
        const response = await fetch(`${apiBase}/api/v1/cases/${params.caseId}`);
        if (!response.ok) {
          throw new Error('case unavailable');
        }
        const payload = await response.json();
        setCaseData(payload);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    if (params.caseId) {
      loadCase();
    }
  }, [params.caseId]);

  if (loading) {
    return <main className="min-h-screen bg-[#f4f5f7] p-10 text-slate-600">Loading case details…</main>;
  }

  if (!caseData) {
    return <main className="min-h-screen bg-[#f4f5f7] p-10 text-slate-600">Case not found.</main>;
  }

  return (
    <main className="min-h-screen bg-[#f4f5f7] text-slate-900">
      <div className="mx-auto max-w-6xl px-6 py-8">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#0b3d91]">Case tracker</p>
            <h1 className="mt-2 text-3xl font-bold">{caseData.case_id}</h1>
          </div>
          <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-blue-700">
            {caseData.status}
          </span>
        </div>

        <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
          <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="grid gap-4 md:grid-cols-3">
              <InfoCard label="Applicant" value={caseData.applicant_name} />
              <InfoCard label="Service" value={caseData.service_id} />
              <InfoCard label="Decision" value={caseData.decision?.decision || 'Pending'} />
            </div>

            <div className="mt-8 rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Timeline</p>
              <div className="mt-5 space-y-5">
                {(caseData.timeline || []).map((event: any, index: number) => (
                  <div key={`${event.event}-${index}`} className="flex gap-4">
                    <div className="flex flex-col items-center">
                      <div className="h-3 w-3 rounded-full bg-[#0b3d91]" />
                      {index < (caseData.timeline || []).length - 1 && <div className="mt-2 h-full w-px bg-slate-200" />}
                    </div>
                    <div className="flex-1 rounded-2xl bg-white p-4 shadow-sm ring-1 ring-slate-200">
                      <div className="flex items-center justify-between gap-3">
                        <p className="font-semibold text-slate-800">{event.event}</p>
                        <span className="text-xs uppercase tracking-[0.2em] text-slate-500">{caseData.status}</span>
                      </div>
                      {event.result && <p className="mt-2 text-sm text-slate-600">Result: {event.result}</p>}
                      {event.reason && <p className="mt-2 text-sm text-slate-600">Reason: {event.reason}</p>}
                      {event.department_id && <p className="mt-2 text-sm text-slate-600">Department: {event.department_id}</p>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </section>

          <aside className="space-y-6">
            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Status summary</p>
              <div className="mt-5 space-y-3 text-sm text-slate-700">
                <div className="flex items-center justify-between rounded-xl bg-slate-50 p-3">
                  <span>Submitted</span>
                  <span className="font-medium">{caseData.timeline?.length ? 'Yes' : 'No'}</span>
                </div>
                <div className="flex items-center justify-between rounded-xl bg-slate-50 p-3">
                  <span>Department check</span>
                  <span className="font-medium">{caseData.department_checks?.length ? 'Verified' : 'Pending'}</span>
                </div>
                <div className="flex items-center justify-between rounded-xl bg-slate-50 p-3">
                  <span>Decision</span>
                  <span className="font-medium">{caseData.decision?.decision || 'Pending'}</span>
                </div>
              </div>
            </div>

            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Action center</p>
              <div className="mt-4 space-y-3">
                <button className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-left text-sm font-medium text-slate-700">Download acknowledgement</button>
                <button className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-left text-sm font-medium text-slate-700">Contact helpdesk</button>
                <button className="w-full rounded-xl bg-[#0b3d91] px-4 py-3 text-sm font-semibold text-white">Track application</button>
              </div>
            </div>
          </aside>
        </div>
      </div>
    </main>
  );
}

function InfoCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">{label}</p>
      <p className="mt-3 text-base font-semibold text-slate-800">{value}</p>
    </div>
  );
}
