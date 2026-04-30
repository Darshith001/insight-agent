"use client";
import { useState } from "react";

type Citation = {
  doc_id: string; page: number; section: string; text: string; score: number; source_uri: string;
};

const DEMO_PASSWORD = process.env.NEXT_PUBLIC_DEMO_PASSWORD || "";

export default function Home() {
  const [q, setQ] = useState("");
  const [answer, setAnswer] = useState("");
  const [citations, setCitations] = useState<Citation[]>([]);
  const [critique, setCritique] = useState<any>(null);
  const [meta, setMeta] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [unlocked, setUnlocked] = useState(DEMO_PASSWORD === "");
  const [pw, setPw] = useState("");

  function unlock(e: React.FormEvent) {
    e.preventDefault();
    if (pw === DEMO_PASSWORD) setUnlocked(true);
    else setError("Wrong password");
  }

  async function ask(e: React.FormEvent) {
    e.preventDefault();
    if (!q.trim()) return;
    setLoading(true);
    setAnswer(""); setCitations([]); setCritique(null); setMeta(null); setError(null);

    try {
      const API = "http://localhost:8000";
      console.log("[InsightAgent] sending request to", `${API}/chat`);
      const res = await fetch(`${API}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });

      console.log("[InsightAgent] response status:", res.status);
      if (!res.ok) {
        const text = await res.text();
        setError(`API error ${res.status}: ${text}`);
        setLoading(false);
        return;
      }

      const reader = res.body!.getReader();
      const decoder = new TextDecoder();
      let buf = "";
      while (true) {
        const { value, done } = await reader.read();
        if (done) { console.log("[InsightAgent] stream done"); break; }
        const chunk = decoder.decode(value, { stream: true });
        console.log("[InsightAgent] chunk:", chunk.slice(0, 80));
        buf += chunk.replace(/\r\n/g, "\n").replace(/\r/g, "\n");
        const events = buf.split("\n\n");
        buf = events.pop() || "";
        for (const ev of events) {
          const lines = ev.split("\n");
          const evt = lines.find(l => l.startsWith("event:"))?.slice(6).trim();
          const data = lines.find(l => l.startsWith("data:"))?.slice(5).trim();
          console.log("[InsightAgent] event:", evt, "data:", data?.slice(0, 60));
          if (!evt || !data) continue;
          try {
            const payload = JSON.parse(data);
            if (evt === "answer")         setAnswer(payload.text);
            else if (evt === "citations") setCitations(payload);
            else if (evt === "critique")  setCritique(payload);
            else if (evt === "tier")      setMeta((m: any) => ({ ...(m || {}), ...payload }));
            else if (evt === "done")      setMeta((m: any) => ({ ...(m || {}), ...payload }));
            else if (evt === "error")     setError(`${payload.message}\n\n${payload.detail}`);
          } catch (e) {
            console.error("[InsightAgent] parse error:", e);
          }
        }
      }
    } catch (err: any) {
      console.error("[InsightAgent] fetch error:", err);
      setError(`Network error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  // Password gate
  if (!unlocked) {
    return (
      <main className="mx-auto max-w-sm p-6 mt-32">
        <h1 className="text-2xl font-bold mb-1 text-center">InsightAgent</h1>
        <p className="text-slate-500 text-sm text-center mb-6">Enter demo password to continue</p>
        <form onSubmit={unlock} className="flex flex-col gap-3">
          <input
            type="password"
            className="rounded-lg border px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Password"
            value={pw}
            onChange={e => setPw(e.target.value)}
            autoFocus
          />
          <button className="rounded-lg bg-blue-700 text-white px-5 py-2 hover:bg-blue-800">
            Enter
          </button>
          {error && <p className="text-red-500 text-sm text-center">{error}</p>}
        </form>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-4xl p-6">
      <h1 className="text-3xl font-bold mb-1">InsightAgent</h1>
      <p className="text-slate-600 mb-6">Agentic multi-modal RAG with self-correcting reasoning.</p>

      <form onSubmit={ask} className="flex gap-2 mb-6">
        <input
          className="flex-1 rounded-lg border px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Ask a question about your documents..."
          value={q}
          onChange={e => setQ(e.target.value)}
        />
        <button
          className="rounded-lg bg-blue-700 text-white px-5 py-2 disabled:opacity-50 hover:bg-blue-800"
          disabled={loading}
        >
          {loading ? "Thinking..." : "Ask"}
        </button>
      </form>

      {error && (
        <div className="rounded-lg bg-red-50 border border-red-300 p-4 mb-4 text-sm text-red-800 whitespace-pre-wrap font-mono">
          <b>Error:</b> {error}
        </div>
      )}

      {meta && !error && (
        <div className="text-xs text-slate-500 mb-2">
          tier: <b>{meta.tier}</b>{meta.cache ? " (cached)" : ""}
          {meta.latency ? ` · ${meta.latency.toFixed(2)}s` : ""}
          {typeof meta.retries === "number" ? ` · retries: ${meta.retries}` : ""}
        </div>
      )}

      {answer && (
        <article className="rounded-xl bg-white border p-5 whitespace-pre-wrap leading-7 text-slate-800">
          {answer}
        </article>
      )}

      {critique && (
        <div className="mt-3 text-sm text-slate-600">
          critic score: <b>{Number(critique.score).toFixed(2)}</b>
          {" · "}faithful {Number(critique.faithful ?? 0).toFixed(2)}
          {" · "}complete {Number(critique.complete ?? 0).toFixed(2)}
          {" · "}relevant {Number(critique.relevant ?? 0).toFixed(2)}
        </div>
      )}

      {citations.length > 0 && (
        <section className="mt-6">
          <h2 className="font-semibold mb-2">Sources</h2>
          <ul className="space-y-2">
            {citations.map((c, i) => (
              <li key={i} className="rounded-lg bg-white border p-3 text-sm">
                <div className="text-slate-400 mb-1 text-xs">
                  [{i + 1}] {c.doc_id} · p.{c.page} · {c.section} · score {Number(c.score).toFixed(2)}
                </div>
                <div className="text-slate-800 line-clamp-3">{c.text}</div>
              </li>
            ))}
          </ul>
        </section>
      )}
    </main>
  );
}
