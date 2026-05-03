"use client";
import { useState, useEffect, useCallback } from "react";
import UploadZone from "./components/UploadZone";
import DocList from "./components/DocList";

const API = "http://localhost:8000";
const DEMO_PASSWORD = process.env.NEXT_PUBLIC_DEMO_PASSWORD || "";

type Citation = {
  doc_id: string; page: number; section: string; text: string; score: number; source_uri: string;
};

interface Doc {
  doc_id: string; chunks: number; source_uri: string;
}

// ─── Password gate ────────────────────────────────────────────────────────────
function PasswordGate({ onUnlock }: { onUnlock: () => void }) {
  const [pw, setPw] = useState("");
  const [err, setErr] = useState("");
  function submit(e: React.FormEvent) {
    e.preventDefault();
    if (pw === DEMO_PASSWORD) onUnlock();
    else setErr("Wrong password");
  }
  return (
    <main className="mx-auto max-w-sm p-6 mt-32">
      <h1 className="text-2xl font-bold mb-1 text-center">InsightAgent</h1>
      <p className="text-slate-500 text-sm text-center mb-6">Enter demo password to continue</p>
      <form onSubmit={submit} className="flex flex-col gap-3">
        <input
          type="password"
          className="rounded-lg border px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Password"
          value={pw}
          onChange={e => setPw(e.target.value)}
          autoFocus
        />
        <button className="rounded-lg bg-blue-700 text-white px-5 py-2 hover:bg-blue-800">Enter</button>
        {err && <p className="text-red-500 text-sm text-center">{err}</p>}
      </form>
    </main>
  );
}

// ─── Sidebar: document library ────────────────────────────────────────────────
function Sidebar() {
  const [docs, setDocs] = useState<Doc[]>([]);
  const [loadingDocs, setLoadingDocs] = useState(true);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const fetchDocs = useCallback(async () => {
    setLoadingDocs(true);
    try {
      const res = await fetch(`${API}/documents`);
      if (res.ok) {
        const data = await res.json();
        setDocs(data.documents ?? []);
      }
    } catch {}
    setLoadingDocs(false);
  }, []);

  useEffect(() => { fetchDocs(); }, [fetchDocs]);

  async function handleDelete(doc_id: string) {
    if (!confirm(`Delete "${doc_id}" and all its vectors?`)) return;
    setDeleteError(null);
    try {
      const res = await fetch(`${API}/documents/${encodeURIComponent(doc_id)}`, { method: "DELETE" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setDocs(prev => prev.filter(d => d.doc_id !== doc_id));
    } catch (e: any) {
      setDeleteError(e.message);
    }
  }

  return (
    <aside className="w-72 shrink-0 flex flex-col border-r border-slate-200 bg-white h-screen overflow-hidden">
      <div className="p-4 border-b border-slate-200">
        <h2 className="font-semibold text-slate-800 mb-3 flex items-center gap-2">
          <LibraryIcon className="w-4 h-4 text-blue-600" />
          Document Library
        </h2>
        <UploadZone onUploaded={fetchDocs} />
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {deleteError && (
          <p className="text-xs text-red-600 mb-2">{deleteError}</p>
        )}
        <DocList docs={docs} loading={loadingDocs} onDelete={handleDelete} />
      </div>

      <div className="p-3 border-t border-slate-100 text-xs text-slate-400 text-center">
        {docs.length} document{docs.length !== 1 ? "s" : ""} indexed
      </div>
    </aside>
  );
}

// ─── Chat panel ───────────────────────────────────────────────────────────────
function ChatPanel() {
  const [q, setQ] = useState("");
  const [answer, setAnswer] = useState("");
  const [citations, setCitations] = useState<Citation[]>([]);
  const [critique, setCritique] = useState<any>(null);
  const [meta, setMeta] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function ask(e: React.FormEvent) {
    e.preventDefault();
    if (!q.trim()) return;
    setLoading(true);
    setAnswer(""); setCitations([]); setCritique(null); setMeta(null); setError(null);

    try {
      const res = await fetch(`${API}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });

      if (!res.ok) {
        setError(`API error ${res.status}: ${await res.text()}`);
        setLoading(false);
        return;
      }

      const reader = res.body!.getReader();
      const decoder = new TextDecoder();
      let buf = "";
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buf += decoder.decode(value, { stream: true }).replace(/\r\n/g, "\n").replace(/\r/g, "\n");
        const events = buf.split("\n\n");
        buf = events.pop() || "";
        for (const ev of events) {
          const lines = ev.split("\n");
          const evt = lines.find(l => l.startsWith("event:"))?.slice(6).trim();
          const data = lines.find(l => l.startsWith("data:"))?.slice(5).trim();
          if (!evt || !data) continue;
          try {
            const payload = JSON.parse(data);
            if (evt === "answer")         setAnswer(payload.text);
            else if (evt === "citations") setCitations(payload);
            else if (evt === "critique")  setCritique(payload);
            else if (evt === "tier")      setMeta((m: any) => ({ ...(m || {}), ...payload }));
            else if (evt === "done")      setMeta((m: any) => ({ ...(m || {}), ...payload }));
            else if (evt === "error")     setError(`${payload.message}\n\n${payload.detail}`);
          } catch {}
        }
      }
    } catch (err: any) {
      setError(`Network error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden">
      {/* Header */}
      <header className="px-6 py-4 border-b border-slate-200 bg-white">
        <h1 className="text-xl font-bold text-slate-900">InsightAgent</h1>
        <p className="text-xs text-slate-500">Agentic RAG · ask questions about your documents</p>
      </header>

      {/* Scrollable output */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {!answer && !error && !loading && (
          <div className="flex flex-col items-center justify-center h-full text-slate-400 text-sm gap-2">
            <ChatIcon className="w-12 h-12 opacity-20" />
            <p>Upload a PDF in the sidebar, then ask a question below.</p>
          </div>
        )}

        {error && (
          <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-800 whitespace-pre-wrap font-mono">
            <b>Error:</b> {error}
          </div>
        )}

        {meta && !error && (
          <div className="text-xs text-slate-400">
            tier: <b className="text-slate-600">{meta.tier}</b>
            {meta.cache ? " · cached" : ""}
            {meta.latency ? ` · ${meta.latency.toFixed(2)}s` : ""}
            {typeof meta.retries === "number" ? ` · retries: ${meta.retries}` : ""}
          </div>
        )}

        {answer && (
          <article className="rounded-xl bg-white border border-slate-200 p-5 whitespace-pre-wrap leading-7 text-slate-800 text-sm">
            {answer}
          </article>
        )}

        {critique && (
          <div className="text-xs text-slate-500">
            critic <b>{Number(critique.score).toFixed(2)}</b>
            {" · "}faithful {Number(critique.faithful ?? 0).toFixed(2)}
            {" · "}complete {Number(critique.complete ?? 0).toFixed(2)}
            {" · "}relevant {Number(critique.relevant ?? 0).toFixed(2)}
          </div>
        )}

        {citations.length > 0 && (
          <section>
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Sources</h3>
            <ul className="space-y-2">
              {citations.map((c, i) => (
                <li key={i} className="rounded-lg bg-white border border-slate-200 p-3 text-xs">
                  <div className="text-slate-400 mb-1">
                    [{i + 1}] <b>{c.doc_id}</b> · p.{c.page} · {c.section} · score {Number(c.score).toFixed(2)}
                  </div>
                  <div className="text-slate-700 line-clamp-3">{c.text}</div>
                </li>
              ))}
            </ul>
          </section>
        )}
      </div>

      {/* Input bar */}
      <div className="px-6 py-4 border-t border-slate-200 bg-white">
        <form onSubmit={ask} className="flex gap-2">
          <input
            className="flex-1 rounded-lg border border-slate-300 px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Ask a question about your documents…"
            value={q}
            onChange={e => setQ(e.target.value)}
            disabled={loading}
          />
          <button
            className="rounded-lg bg-blue-700 text-white px-5 py-2 text-sm disabled:opacity-50 hover:bg-blue-800 transition-colors"
            disabled={loading || !q.trim()}
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <Spinner /> Thinking…
              </span>
            ) : "Ask"}
          </button>
        </form>
      </div>
    </div>
  );
}

// ─── Root ─────────────────────────────────────────────────────────────────────
export default function Home() {
  const [unlocked, setUnlocked] = useState(DEMO_PASSWORD === "");

  if (!unlocked) return <PasswordGate onUnlock={() => setUnlocked(true)} />;

  return (
    <main className="flex h-screen overflow-hidden bg-slate-50">
      <Sidebar />
      <ChatPanel />
    </main>
  );
}

// ─── Icons ────────────────────────────────────────────────────────────────────
function LibraryIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round"
        d="M12 6.042A8.967 8.967 0 0 0 6 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 0 1 6 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 0 1 6-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0 0 18 18a8.967 8.967 0 0 0-6 2.292m0-14.25v14.25" />
    </svg>
  );
}

function ChatIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round"
        d="M8.625 12a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H8.25m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H12m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 0 1-2.555-.337A5.972 5.972 0 0 1 5.41 20.97a5.969 5.969 0 0 1-.474-.065 4.48 4.48 0 0 0 .978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25Z" />
    </svg>
  );
}

function Spinner() {
  return (
    <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8V0C5.373 0 0 5.373 0 12h4Z" />
    </svg>
  );
}
