'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export default function ServicesPage() {
  const router = useRouter();
  const [service, setService] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [applicantName, setApplicantName] = useState('Citizen Portal User');
  const [studentId, setStudentId] = useState('');
  const [income, setIncome] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    const loadService = async () => {
      try {
        const response = await fetch(`${apiBase}/api/v1/services/scholarship`);
        if (!response.ok) {
          throw new Error('service unavailable');
        }
        const payload = await response.json();
        setService(payload);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    loadService();
  }, []);

  if (loading) {
    return <main className="min-h-screen bg-[#f4f5f7] p-8 text-slate-600">Loading service details…</main>;
  }

  if (!service) {
    return <main className="min-h-screen bg-[#f4f5f7] p-8 text-slate-600">Service not found.</main>;
  }

  return (
    <main className="min-h-screen bg-[#f4f5f7] text-slate-900">
      <div className="mx-auto max-w-6xl px-6 py-8">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#0b3d91]">Service portal</p>
            <h1 className="mt-2 text-3xl font-bold">{service.name}</h1>
          </div>
          <Link href="/" className="rounded-full bg-[#0b3d91] px-4 py-2 text-sm font-medium text-white">
            Apply now
          </Link>
        </div>

        <div className="grid gap-6 xl:grid-cols-[1.3fr_0.7fr]">
          <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Department</p>
                <h2 className="mt-2 text-xl font-bold">{service.provider}</h2>
              </div>
              <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-emerald-700">
                Open
              </span>
            </div>

            <p className="mt-6 text-base leading-7 text-slate-700">{service.description}</p>

            <div className="mt-8 grid gap-4 md:grid-cols-2">
              <InfoBlock label="Eligibility" value={service.eligibility_summary} />
              <InfoBlock label="Processing time" value={`${service.estimated_time_days} days`} />
              <InfoBlock label="Application fee" value={service.fee} />
              <InfoBlock label="Deadline" value={service.deadline} />
            </div>

            <div className="mt-8 rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Required documents</p>
              <ul className="mt-4 space-y-3 text-sm text-slate-700">
                {service.required_documents.map((item: string) => (
                  <li key={item} className="flex items-center gap-3">
                    <span className="h-2.5 w-2.5 rounded-full bg-[#0b3d91]" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </section>

          <aside className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Application form</p>
            <form
              className="mt-5 space-y-4"
              onSubmit={async (event) => {
                event.preventDefault();
                setSubmitting(true);
                setMessage('');

                try {
                  const response = await fetch(`${apiBase}/api/v1/cases`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                      service_id: service.id,
                      applicant_name: applicantName || 'Citizen Portal User',
                    }),
                  });

                  if (!response.ok) {
                    throw new Error('Unable to create application');
                  }

                  const payload = await response.json();
                  localStorage.setItem('lastCaseId', payload.case_id);
                  setMessage('Application submitted successfully.');
                  router.push(`/cases/${payload.case_id}`);
                } catch (error) {
                  setMessage('Unable to submit application. Please try again.');
                } finally {
                  setSubmitting(false);
                }
              }}
            >
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">Applicant name</label>
                <input
                  value={applicantName}
                  onChange={(event) => setApplicantName(event.target.value)}
                  className="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 outline-none"
                />
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">Student ID</label>
                <input
                  value={studentId}
                  onChange={(event) => setStudentId(event.target.value)}
                  className="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 outline-none"
                  placeholder="Enter ID"
                />
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">Annual family income</label>
                <input
                  value={income}
                  onChange={(event) => setIncome(event.target.value)}
                  className="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 outline-none"
                  placeholder="₹ 4,50,000"
                />
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">Consent</label>
                <div className="rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm text-slate-600">
                  I authorize verification of income and enrollment status for this application.
                </div>
              </div>
              {message ? <div className="text-sm text-slate-700">{message}</div> : null}
              <button type="submit" disabled={submitting} className="w-full rounded-xl bg-[#0b3d91] px-4 py-3 text-sm font-semibold text-white disabled:opacity-60">
                {submitting ? 'Submitting…' : 'Submit application'}
              </button>
            </form>
          </aside>
        </div>
      </div>
    </main>
  );
}

function InfoBlock({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">{label}</p>
      <p className="mt-3 text-sm font-medium text-slate-800">{value}</p>
    </div>
  );
}
