"use client";

import { useEffect, useState, useRef } from "react";
import { storage } from "@/lib/firebase";

const BACKEND_URL = storage.getBackendUrl();
const WS_URL = BACKEND_URL.replace("http://", "ws://").replace("https://", "wss://");

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
  const [connectionStatus, setConnectionStatus] = useState<"connecting" | "connected" | "disconnected">("connecting");
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const connectWebSocket = () => {
      try {
        const ws = new WebSocket(`${WS_URL}/api/v1/ws`);
        wsRef.current = ws;

        ws.onopen = () => {
          console.log("WebSocket connected");
          setConnectionStatus("connected");
          // Send ping every 30 seconds to keep connection alive
          const pingInterval = setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
              ws.send("ping");
            }
          }, 30000);
          
          // Store interval ID for cleanup
          (ws as any).pingInterval = pingInterval;
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            
            if (data.type === "initial_state" || data.type === "cars_update") {
              // Convert backend format to frontend format
              const nextCars: CarDoc[] = Object.entries(data.cars || {}).map(([id, car]: [string, any]) => ({
                id,
                start: car.start || "",
                end: car.end || "",
                x: car.path?.[0]?.x || car.x || 0,
                y: car.path?.[0]?.y || car.y || 0,
                path: car.path || [],
                last_updated: car.updated_at,
              }));
              setCars(nextCars);
            }
          } catch (error) {
            console.error("Failed to parse WebSocket message:", error);
          }
        };

        ws.onerror = (error) => {
          console.error("WebSocket error:", error);
          setConnectionStatus("disconnected");
        };

        ws.onclose = () => {
          console.log("WebSocket disconnected");
          setConnectionStatus("disconnected");
          
          // Clear ping interval
          if ((ws as any).pingInterval) {
            clearInterval((ws as any).pingInterval);
          }
          
          // Reconnect after 2 seconds
          reconnectTimeoutRef.current = setTimeout(() => {
            connectWebSocket();
          }, 2000);
        };
      } catch (error) {
        console.error("Failed to connect WebSocket:", error);
        setConnectionStatus("disconnected");
        // Retry connection
        reconnectTimeoutRef.current = setTimeout(() => {
          connectWebSocket();
        }, 2000);
      }
    };

    connectWebSocket();

    return () => {
      // Cleanup
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        if ((wsRef.current as any).pingInterval) {
          clearInterval((wsRef.current as any).pingInterval);
        }
        wsRef.current.close();
      }
    };
  }, []);

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
      <div className="mb-2 flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-300">
          Map View
        </h2>
        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-500">
            Cars: {cars.length}
          </span>
          <span className={`text-xs ${
            connectionStatus === "connected" ? "text-emerald-400" :
            connectionStatus === "connecting" ? "text-yellow-400" :
            "text-red-400"
          }`}>
            {connectionStatus === "connected" ? "● Live" :
             connectionStatus === "connecting" ? "○ Connecting..." :
             "○ Disconnected"}
          </span>
        </div>
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
