"use client";
import { useRef, useState, DragEvent, ChangeEvent } from "react";

interface Props {
  onUploaded: () => void;
}

export default function UploadZone({ onUploaded }: Props) {
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  async function uploadFile(file: File) {
    setUploading(true);
    setError(null);
    setProgress(`Uploading ${file.name}…`);

    const form = new FormData();
    form.append("file", file);
    form.append("doc_id", file.name.replace(/\.[^.]+$/, ""));

    try {
      const res = await fetch("http://localhost:8000/ingest", {
        method: "POST",
        body: form,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
      setProgress(`✓ ${data.doc_id} — ${data.chunks} chunks indexed`);
      onUploaded();
    } catch (e: any) {
      setError(e.message);
      setProgress(null);
    } finally {
      setUploading(false);
    }
  }

  function onDrop(e: DragEvent) {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) uploadFile(file);
  }

  function onChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) uploadFile(file);
    e.target.value = "";
  }

  return (
    <div className="mb-4">
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => !uploading && inputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-xl p-5 text-center cursor-pointer transition-colors select-none
          ${dragging ? "border-blue-500 bg-blue-50" : "border-slate-300 hover:border-blue-400 hover:bg-slate-100"}
          ${uploading ? "pointer-events-none opacity-60" : ""}`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx,.txt,.md,.html"
          className="hidden"
          onChange={onChange}
        />
        <div className="flex flex-col items-center gap-1">
          <UploadIcon className="w-8 h-8 text-slate-400" />
          <p className="text-sm font-medium text-slate-600">
            {uploading ? "Processing…" : "Drop PDF here or click to browse"}
          </p>
          <p className="text-xs text-slate-400">PDF, DOCX, TXT, MD · max 50 MB</p>
        </div>
      </div>

      {uploading && (
        <div className="mt-2 h-1.5 rounded-full bg-slate-200 overflow-hidden">
          <div className="h-full bg-blue-500 animate-pulse w-full" />
        </div>
      )}

      {progress && !uploading && (
        <p className="mt-2 text-xs text-green-700 font-medium">{progress}</p>
      )}
      {error && (
        <p className="mt-2 text-xs text-red-600">{error}</p>
      )}
    </div>
  );
}

function UploadIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round"
        d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5" />
    </svg>
  );
}
