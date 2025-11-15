import MapDisplay from "@/components/MapDisplay";
import QRCode from "@/components/QRCode";

export default function HomePage() {
  return (
    <main className="grid gap-4 md:grid-cols-[3fr_1fr]">
      <MapDisplay />
      <div className="space-y-4">
        <QRCode />
        <section className="rounded-lg border border-slate-800 bg-slate-900 p-4 text-xs text-slate-400">
          <h2 className="mb-2 text-sm font-semibold text-slate-200">
            Demo Overview
          </h2>
          <p>
            Watch multiple cars move on the shared map in real time as drivers
            control them from their phones. The admin dashboard can run a
            centralized planner to assign safe paths.
          </p>
        </section>
      </div>
    </main>
  );
}
