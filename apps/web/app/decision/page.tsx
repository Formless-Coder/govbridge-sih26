'use client';

import { useEffect, useState } from 'react';

const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export default function DecisionPage() {
  const [caseId, setCaseId] = useState('');
  const [decision, setDecision] = useState('approved');
  const [reason, setReason] = useState('Eligibility verified and all checks passed.');
  const [response, setResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem('lastCaseId');
    if (stored) setCaseId(stored);
  }, []);

  const submitDecision = async () => {
    if (!caseId.trim()) {
      setResponse({ error: 'Please enter a case ID.' });
      return;
    }

    setLoading(true);
    try {
      const result = await fetch(`${apiBase}/api/v1/cases/${caseId}/decisions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ decision, reason }),
      });
      const payload = await result.json();
      setResponse(payload);
      localStorage.setItem('lastCaseId', caseId);
    } catch (error) {
      setResponse({ error: 'Unable to submit decision.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-[#f4f5f7] text-slate-900">
      <div className="mx-auto max-w-4xl px-6 py-8">
        <div className="mb-6">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#0b3d91]">Decision center</p>
          <h1 className="mt-2 text-3xl font-bold">Case decision</h1>
        </div>

        <div className="grid gap-6 xl:grid-cols-[1fr_0.8fr]">
          <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="space-y-5">
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">Case ID</label>
                <input
                  value={caseId}
                  onChange={(event) => setCaseId(event.target.value)}
                  className="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 outline-none"
                  placeholder="Enter case id"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">Decision</label>
                <select
                  value={decision}
                  onChange={(event) => setDecision(event.target.value)}
                  className="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 outline-none"
                >
                  <option value="approved">Approved</option>
                  <option value="rejected">Rejected</option>
                  <option value="referred">Referred</option>
                </select>
              </div>

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">Reason</label>
                <textarea
                  value={reason}
                  onChange={(event) => setReason(event.target.value)}
                  rows={6}
                  className="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 outline-none"
                />
              </div>

              <button
                type="button"
                onClick={submitDecision}
                disabled={loading}
                className="w-full rounded-xl bg-[#0b3d91] px-4 py-3 text-sm font-semibold text-white disabled:opacity-60"
              >
                {loading ? 'Submitting…' : 'Submit decision'}
              </button>
            </div>
          </section>

          <aside className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Result</p>
            {response ? (
              <div className="mt-5 rounded-2xl bg-slate-50 p-4 text-sm text-slate-700">
                {response.error ? (
                  <div className="text-red-600">{response.error}</div>
                ) : (
                  <div className="space-y-2">
                    <div><span className="font-semibold">Case:</span> {response.case_id}</div>
                    <div><span className="font-semibold">Decision:</span> {response.decision}</div>
                    <div><span className="font-semibold">Reason:</span> {response.reason}</div>
                  </div>
                )}
              </div>
            ) : (
              <div className="mt-5 rounded-2xl bg-slate-50 p-4 text-sm text-slate-500">No decision submitted yet.</div>
            )}
          </aside>
        </div>
      </div>
    </main>
  );
}
