"use client";

import { useEffect, useState } from "react";
import {
  signInAnonymously,
  onAuthStateChanged,
  User,
} from "firebase/auth";
import {
  collection,
  doc,
  getDoc,
  setDoc,
  updateDoc,
} from "firebase/firestore";
import { auth, db } from "@/lib/firebase";

const APP_ID = process.env.NEXT_PUBLIC_APP_ID ?? "demo-app";

const NODES = ["Alpha", "Bravo", "Charlie", "Delta"];

function getRandomNode(exclude?: string) {
  const options = NODES.filter((n) => n !== exclude);
  return options[Math.floor(Math.random() * options.length)];
}

export function MobileDriver() {
  const [user, setUser] = useState<User | null>(null);
  const [startNode, setStartNode] = useState<string>("Alpha");
  const [endNode, setEndNode] = useState<string | null>(null);
  const [x, setX] = useState<number>(120);
  const [y, setY] = useState<number>(450);
  const [path, setPath] = useState<{ x: number; y: number }[]>([]);
  const [status, setStatus] = useState<string>("Idle");

  useEffect(() => {
    const unsub = onAuthStateChanged(auth, async (u) => {
      if (u) {
        setUser(u);
        return;
      }
      const cred = await signInAnonymously(auth);
      setUser(cred.user);
    });
    return () => unsub();
  }, []);

  useEffect(() => {
    if (!user) return;

    const handler = (e: KeyboardEvent) => {
      let nextX = x;
      let nextY = y;
      const step = 10;

      if (e.key === "ArrowUp") nextY -= step;
      if (e.key === "ArrowDown") nextY += step;
      if (e.key === "ArrowLeft") nextX -= step;
      if (e.key === "ArrowRight") nextX += step;

      if (nextX === x && nextY === y) return;

      setX(nextX);
      setY(nextY);
      const newPath = [...path, { x: nextX, y: nextY }];
      setPath(newPath);

      const carRef = doc(
        db,
        "artifacts", APP_ID, "data", "public", "cars", user.uid
      );

      updateDoc(carRef, {
        x: nextX,
        y: nextY,
        path: newPath,
        last_updated: new Date().toISOString(),
      }).catch(() => {
        // Ignore for demo
      });
    };

    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [user, x, y, path]);

  const handleStart = async () => {
    if (!user) return;

    const end = getRandomNode(startNode);
    setEndNode(end);

    // Mock backend call to get a path; here we just generate a line
    const mockPath = [
      { x, y },
      { x, y: y - 10 },
      { x: x + 10, y: y - 10 },
    ];
    setPath(mockPath);

    const carRef = doc(
      db,
      "artifacts", APP_ID, "data", "public", "cars", user.uid
    );

    await setDoc(carRef, {
      start: startNode,
      end,
      x,
      y,
      last_updated: new Date().toISOString(),
      path: mockPath,
    });

    setStatus("Driving (use arrow keys)");
  };

  return (
    <div className="space-y-4 rounded-lg border border-slate-800 bg-slate-900 p-4">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-300">
        Mobile Driver
      </h2>
      <p className="text-xs text-slate-400">
        Sign in anonymously, pick a start node, then press Start. Use the
        arrow keys to move your car on the shared map.
      </p>

      <div className="space-y-2 text-xs">
        <div>
          <span className="font-medium text-slate-300">Auth Status:</span>{" "}
          <span className="text-slate-400">
            {user ? `Signed in as ${user.uid.slice(0, 6)}...` : "Signing in..."}
          </span>
        </div>
        <div>
          <span className="font-medium text-slate-300">Status:</span>{" "}
          <span className="text-slate-400">{status}</span>
        </div>
      </div>

      <div className="space-y-2 text-xs">
        <label className="block text-slate-300">Start Node</label>
        <select
          value={startNode}
          onChange={(e) => setStartNode(e.target.value)}
          className="w-full rounded-md border border-slate-700 bg-slate-800 px-2 py-1 text-xs text-slate-100"
        >
          {NODES.map((n) => (
            <option key={n} value={n}>
              {n}
            </option>
          ))}
        </select>
      </div>

      <button
        onClick={handleStart}
        className="w-full rounded-md bg-emerald-500 px-3 py-2 text-xs font-semibold text-emerald-950 hover:bg-emerald-400"
        disabled={!user}
      >
        {user ? "Start Driving" : "Connecting..."}
      </button>

      <div className="space-y-1 text-xs text-slate-400">
        <div>
          <span className="font-semibold text-slate-300">Start:</span> {startNode}
        </div>
        <div>
          <span className="font-semibold text-slate-300">End:</span> {endNode ?? "(pending)"}
        </div>
        <div>
          <span className="font-semibold text-slate-300">Position:</span> ({x},{" "}
          {y})
        </div>
        <div>
          <span className="font-semibold text-slate-300">Path length:</span> {path.length}
        </div>
      </div>
    </div>
  );
}

export default MobileDriver;
