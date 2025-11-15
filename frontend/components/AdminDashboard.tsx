"use client";

import { useEffect, useState } from "react";
import { collection, onSnapshot, query } from "firebase/firestore";
import { db } from "@/lib/firebase";

const APP_ID = process.env.NEXT_PUBLIC_APP_ID ?? "demo-app";
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

type CarDoc = {
  id: string;
  start: string;
  end: string;
  x: number;
  y: number;
  last_updated?: string;
  path?: { x: number; y: number }[];
};

type PlanResponse = {
  plan_id: string;
  paths: {
    car_id: string;
    path: { x: number; y: number }[];
    status: string;
  }[];
};

export function AdminDashboard() {
  const [cars, setCars] = useState<CarDoc[]>([]);
  const [planResponse, setPlanResponse] = useState<PlanResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Create collection path with 5 segments: collection/doc/collection/doc/collection
    const carsCol = collection(db, "artifacts", APP_ID, "data", "public", "cars");
    const q = query(carsCol);

    const unsub = onSnapshot(q, (snap) => {
      const nextCars: CarDoc[] = [];
      snap.forEach((docSnap) => {
        const data = docSnap.data() as Omit<CarDoc, "id">;
        nextCars.push({ id: docSnap.id, ...data });
      });
      setCars(nextCars);
    });

    return () => unsub();
  }, []);

  const handleRunPlanner = async () => {
    setLoading(true);
    setError(null);
    setPlanResponse(null);

    try {
      const payload = {
        cars: cars.map((c) => ({
          id: c.id,
          start_node: c.start,
          end_node: c.end,
          current_pos: [c.x, c.y],
        })),
      };

      const res = await fetch(`${BACKEND_URL}/api/v1/run-plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        throw new Error(`Failed to run planner: ${res.statusText}`);
      }

      const data: PlanResponse = await res.json();
      setPlanResponse(data);
    } catch (err: any) {
      setError(err.message ?? "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-300">
          Admin Dashboard
        </h2>

        <div className="mb-4 space-y-2">
          <h3 className="text-xs font-medium text-slate-400">
            Active Cars ({cars.length})
          </h3>
          {cars.length === 0 ? (
            <p className="text-xs text-slate-500">No cars active yet.</p>
          ) : (
            <div className="space-y-1">
              {cars.map((car) => (
                <div
                  key={car.id}
                  className="flex items-center justify-between rounded-md border border-slate-700 bg-slate-800 px-2 py-1 text-xs"
                >
                  <span className="font-mono text-slate-300">
                    {car.id.slice(0, 8)}...
                  </span>
                  <span className="text-slate-400">
                    {car.start} → {car.end}
                  </span>
                  <span className="text-slate-500">
                    ({car.x}, {car.y})
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        <button
          onClick={handleRunPlanner}
          disabled={loading || cars.length === 0}
          className="w-full rounded-md bg-blue-600 px-3 py-2 text-xs font-semibold text-white hover:bg-blue-500 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-500"
        >
          {loading ? "Running Planner..." : "Run Planner"}
        </button>

        {error && (
          <div className="mt-3 rounded-md border border-red-800 bg-red-950/50 p-2 text-xs text-red-300">
            Error: {error}
          </div>
        )}
      </div>

      {planResponse && (
        <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
          <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-300">
            Plan Result
          </h3>
          <div className="space-y-2 text-xs">
            <div>
              <span className="font-medium text-slate-400">Plan ID:</span>{" "}
              <span className="text-slate-300">{planResponse.plan_id}</span>
            </div>
            <div>
              <span className="font-medium text-slate-400">Paths:</span>
            </div>
            <div className="space-y-1">
              {planResponse.paths.map((p) => (
                <div
                  key={p.car_id}
                  className="rounded-md border border-slate-700 bg-slate-800 p-2"
                >
                  <div className="font-mono text-slate-300">
                    {p.car_id.slice(0, 8)}...
                  </div>
                  <div className="text-slate-400">
                    Status: {p.status} | Path length: {p.path.length}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AdminDashboard;
