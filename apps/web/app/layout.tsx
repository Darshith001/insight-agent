import "./globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "InsightAgent",
  description: "Agentic multi-modal RAG",
  icons: { icon: "/favicon.svg" },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className="h-full">
      <body className="h-full overflow-hidden">{children}</body>
    </html>
  );
}
