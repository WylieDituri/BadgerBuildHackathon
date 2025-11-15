"use client";

import { useEffect, useState } from "react";
import { collection, doc, onSnapshot, query } from "firebase/firestore";
import { db } from "@/lib/firebase";

const APP_ID = process.env.NEXT_PUBLIC_APP_ID ?? "demo-app";

export type CarDoc = {
  id: string;
  start: string;
  end: string;
  x: number;
  y: number;
  last_updated?: string;
  path?: { x: number; y: number }[];
};

export function MapDisplay() {
  const [cars, setCars] = useState<CarDoc[]>([]);

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

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
      <div className="mb-2 flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-300">
          Map View
        </h2>
        <span className="text-xs text-slate-500">
          Cars: {cars.length}
        </span>
      </div>
      <div className="relative h-[480px] w-full overflow-hidden rounded-md bg-gradient-to-br from-slate-900 to-slate-800">
        {/* Simple grid background */}
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_1px_1px,#1e293b_1px,transparent_0)] bg-[length:24px_24px] opacity-60" />

        {cars.map((car) => (
          <div
            key={car.id}
            className="absolute flex h-4 w-4 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full bg-emerald-400 text-[8px] font-bold text-slate-900 shadow-lg shadow-emerald-500/40"
            style={{
              left: `${car.x}px`,
              top: `${car.y}px`,
            }}
            title={`${car.id}: ${car.start} → ${car.end}`}
          >
            C
          </div>
        ))}
      </div>
    </div>
  );
}

export default MapDisplay;
