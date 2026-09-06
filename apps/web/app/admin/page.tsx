'use client';

import { useEffect, useState } from 'react';

const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

type AuditEntry = {
  case_id: string;
  actor: string;
  action: string;
  resource: string;
  purpose: string;
  outcome: string;
  timestamp: string;
};

type ConfigState = {
  service_catalog: Array<{ service_id: string; name: string; enabled: boolean; department: string }>;
  slas: { review_hours: number; decision_hours: number; appeal_hours: number };
  notifications: { email: boolean; sms: boolean; push: boolean };
  workflow: { auto_assign: boolean; escalation_enabled: boolean };
};

export default function AdminAuditPage() {
  const [summary, setSummary] = useState({ total_cases: 0, decision_made: 0, under_review: 0, audit_records: 0 });
  const [activity, setActivity] = useState<AuditEntry[]>([]);
  const [config, setConfig] = useState<ConfigState>({
    service_catalog: [],
    slas: { review_hours: 72, decision_hours: 24, appeal_hours: 120 },
    notifications: { email: true, sms: false, push: true },
    workflow: { auto_assign: true, escalation_enabled: true },
  });
  const [loading, setLoading] = useState(true);

  const loadAdminData = async () => {
    try {
      const [auditResponse, configResponse] = await Promise.all([
        fetch(`${apiBase}/api/v1/admin/audit`),
        fetch(`${apiBase}/api/v1/admin/config`),
      ]);

      if (!auditResponse.ok) throw new Error('audit unavailable');
      if (!configResponse.ok) throw new Error('config unavailable');

      const auditPayload = await auditResponse.json();
      const configPayload = await configResponse.json();
      setSummary(auditPayload.summary ?? summary);
      setActivity(auditPayload.recent_activity ?? []);
      setConfig(configPayload);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAdminData();
  }, []);

  const toggleNotification = async (key: keyof ConfigState['notifications']) => {
    const next = { ...config.notifications, [key]: !config.notifications[key] };
    const payload = { notifications: next };
    const response = await fetch(`${apiBase}/api/v1/admin/config`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (response.ok) {
      const updated = await response.json();
      setConfig((current) => ({ ...current, notifications: updated.notifications }));
    }
  };

  return (
    <main className="min-h-screen bg-[#f4f5f7] text-slate-900">
      <div className="mx-auto max-w-7xl px-6 py-8">
        <div className="mb-6">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[#0b3d91]">Administration</p>
          <h1 className="mt-2 text-3xl font-bold">Audit dashboard</h1>
        </div>

        <section className="mb-6 grid gap-4 md:grid-cols-4">
          <MetricCard label="Total cases" value={summary.total_cases} accent="blue" />
          <MetricCard label="Decision made" value={summary.decision_made} accent="green" />
          <MetricCard label="Under review" value={summary.under_review} accent="amber" />
          <MetricCard label="Audit records" value={summary.audit_records} accent="slate" />
        </section>

        <section className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
          <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-5 flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Operations</p>
                <h2 className="mt-2 text-xl font-bold">Recent activity</h2>
              </div>
            </div>

            {loading ? (
              <div className="rounded-2xl bg-slate-50 p-4 text-sm text-slate-500">Loading audit trail…</div>
            ) : activity.length === 0 ? (
              <div className="rounded-2xl bg-slate-50 p-4 text-sm text-slate-500">No activity yet.</div>
            ) : (
              <div className="space-y-3">
                {activity.map((item) => (
                  <div key={`${item.case_id}-${item.action}-${item.timestamp}`} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <p className="text-sm font-semibold text-slate-900">{item.action}</p>
                        <p className="mt-1 text-xs uppercase tracking-[0.2em] text-slate-500">{item.case_id}</p>
                      </div>
                      <span className="rounded-full bg-emerald-100 px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-emerald-700">
                        {item.outcome}
                      </span>
                    </div>
                    <div className="mt-3 grid gap-2 text-sm text-slate-600 md:grid-cols-2">
                      <div><span className="font-medium text-slate-700">Actor:</span> {item.actor}</div>
                      <div><span className="font-medium text-slate-700">Purpose:</span> {item.purpose}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <aside className="space-y-6">
            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Compliance</p>
              <div className="mt-5 space-y-3">
                <ComplianceRow label="Eligibility checks" value="96%" />
                <ComplianceRow label="Document completeness" value="89%" />
                <ComplianceRow label="Decision turnaround" value="4.2 days" />
              </div>
            </div>

            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Admin tasks</p>
              <div className="mt-4 space-y-3">
                <button className="w-full rounded-xl border border-slate-200 bg-slate-50 p-3 text-left text-sm font-medium text-slate-700">Review flagged cases</button>
                <button className="w-full rounded-xl border border-slate-200 bg-slate-50 p-3 text-left text-sm font-medium text-slate-700">Export audit log</button>
                <button className="w-full rounded-xl bg-[#0b3d91] p-3 text-left text-sm font-semibold text-white">Open officer queue</button>
              </div>
            </div>
          </aside>
        </section>

        <section className="mt-6 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">System settings</p>
              <h2 className="mt-2 text-xl font-bold">Admin configuration</h2>
            </div>
          </div>

          <div className="grid gap-6 lg:grid-cols-3">
            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">SLA policy</h3>
              <div className="mt-4 space-y-3 text-sm text-slate-700">
                <div className="flex items-center justify-between"><span>Review</span><span className="font-semibold">{config.slas.review_hours} hrs</span></div>
                <div className="flex items-center justify-between"><span>Decision</span><span className="font-semibold">{config.slas.decision_hours} hrs</span></div>
                <div className="flex items-center justify-between"><span>Appeal</span><span className="font-semibold">{config.slas.appeal_hours} hrs</span></div>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">Notification modes</h3>
              <div className="mt-4 space-y-3 text-sm text-slate-700">
                {Object.entries(config.notifications).map(([key, value]) => (
                  <button
                    key={key}
                    type="button"
                    onClick={() => toggleNotification(key as keyof ConfigState['notifications'])}
                    className="flex w-full items-center justify-between rounded-xl border border-slate-200 bg-white px-3 py-2 text-left"
                  >
                    <span className="capitalize">{key}</span>
                    <span className={`rounded-full px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] ${value ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-200 text-slate-600'}`}>
                      {value ? 'On' : 'Off'}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-500">Service catalog</h3>
              <div className="mt-4 space-y-3 text-sm text-slate-700">
                {config.service_catalog.slice(0, 3).map((entry) => (
                  <div key={entry.service_id} className="flex items-center justify-between gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2">
                    <div>
                      <div className="font-medium text-slate-800">{entry.name}</div>
                      <div className="text-[10px] uppercase tracking-[0.2em] text-slate-500">{entry.department}</div>
                    </div>
                    <span className={`rounded-full px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] ${entry.enabled ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-200 text-slate-600'}`}>
                      {entry.enabled ? 'Live' : 'Paused'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}

function MetricCard({ label, value, accent }: { label: string; value: number; accent: 'blue' | 'green' | 'amber' | 'slate' }) {
  const tones = {
    blue: 'bg-blue-50 text-blue-700',
    green: 'bg-emerald-50 text-emerald-700',
    amber: 'bg-amber-50 text-amber-700',
    slate: 'bg-slate-100 text-slate-700',
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

function ComplianceRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between rounded-xl bg-slate-50 p-3 text-sm text-slate-700">
      <span>{label}</span>
      <span className="font-semibold text-slate-900">{value}</span>
    </div>
  );
}
