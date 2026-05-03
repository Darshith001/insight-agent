"use client";

interface Doc {
  doc_id: string;
  chunks: number;
  source_uri: string;
}

interface Props {
  docs: Doc[];
  loading: boolean;
  onDelete: (doc_id: string) => void;
}

export default function DocList({ docs, loading, onDelete }: Props) {
  if (loading) {
    return (
      <div className="space-y-2">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-12 rounded-lg bg-slate-200 animate-pulse" />
        ))}
      </div>
    );
  }

  if (docs.length === 0) {
    return (
      <div className="text-center py-8 text-slate-400 text-sm">
        <FileIcon className="w-10 h-10 mx-auto mb-2 opacity-30" />
        No documents yet.
        <br />Upload a PDF to get started.
      </div>
    );
  }

  return (
    <ul className="space-y-2">
      {docs.map((doc) => (
        <li
          key={doc.doc_id}
          className="flex items-start gap-2 rounded-lg border border-slate-200 bg-white p-3 text-sm"
        >
          <FileIcon className="w-4 h-4 mt-0.5 shrink-0 text-blue-500" />
          <div className="flex-1 min-w-0">
            <p className="font-medium text-slate-800 truncate" title={doc.doc_id}>
              {doc.doc_id}
            </p>
            <p className="text-xs text-slate-400">{doc.chunks} chunks</p>
          </div>
          <button
            onClick={() => onDelete(doc.doc_id)}
            className="shrink-0 text-slate-300 hover:text-red-500 transition-colors"
            title="Delete document"
          >
            <TrashIcon className="w-4 h-4" />
          </button>
        </li>
      ))}
    </ul>
  );
}

function FileIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round"
        d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
    </svg>
  );
}

function TrashIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round"
        d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
    </svg>
  );
}
