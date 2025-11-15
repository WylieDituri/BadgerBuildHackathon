import "./globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "Centralized Car Intelligence Demo",
  description: "Multi-car planner demo with Next.js, FastAPI, and Firebase.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-950 text-slate-50">
        <div className="mx-auto max-w-6xl p-4">
          <header className="mb-6 flex items-center justify-between">
            <h1 className="text-xl font-semibold">Centralized Car Intelligence</h1>
            <nav className="space-x-4 text-sm">
              <a href="/" className="hover:underline">
                Map
              </a>
              <a href="/mobile" className="hover:underline">
                Mobile
              </a>
              <a href="/admin" className="hover:underline">
                Admin
              </a>
            </nav>
          </header>
          {children}
        </div>
      </body>
    </html>
  );
}
