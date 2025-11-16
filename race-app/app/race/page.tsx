"use client";

import {
  drawRoadLayout,
  isPointOnRoad,
  snapPointToRoad,
} from "../../lib/roadLayout";
import { useCallback, useEffect, useRef, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL;

interface StartPosition {
  x: number;
  y: number;
  heading: number;
  name: string;
}

interface LobbyPlayer {
  player_id: string;
  position: { lat: number; lon: number };
}

interface ApiPlayer {
  player_id: string;
  username: string;
  status: string;
  position: { lat: number; lon: number };
  destination?: { lat: number; lon: number };
}

interface RenderPlayer {
  player_id: string;
  username: string;
  status: string;
  x: number;
  y: number;
}

const MAP_SIZE = 400;
const CAR_HALF_LENGTH = 12;
const CAR_HALF_WIDTH = 6;

const startPositions: StartPosition[] = [
  // Corners (4)
  { x: -180, y: -180, heading: 45, name: "North West Corner" },
  { x: 180, y: -180, heading: 135, name: "North East Corner" },
  { x: -180, y: 180, heading: 315, name: "South West Corner" },
  { x: 180, y: 180, heading: 225, name: "South East Corner" },
  // Edges - North (4)
  { x: -120, y: -180, heading: 90, name: "North West" },
  { x: -60, y: -180, heading: 90, name: "North Center-West" },
  { x: 60, y: -180, heading: 90, name: "North Center-East" },
  { x: 120, y: -180, heading: 90, name: "North East" },
  // Edges - South (4)
  { x: -120, y: 180, heading: 270, name: "South West" },
  { x: -60, y: 180, heading: 270, name: "South Center-West" },
  { x: 60, y: 180, heading: 270, name: "South Center-East" },
  { x: 120, y: 180, heading: 270, name: "South East" },
  // Edges - West (4)
  { x: -180, y: -120, heading: 0, name: "West North" },
  { x: -180, y: -60, heading: 0, name: "West Center-North" },
  { x: -180, y: 60, heading: 0, name: "West Center-South" },
  { x: -180, y: 120, heading: 0, name: "West South" },
  // Edges - East (4)
  { x: 180, y: -120, heading: 180, name: "East North" },
  { x: 180, y: -60, heading: 180, name: "East Center-North" },
  { x: 180, y: 60, heading: 180, name: "East Center-South" },
  { x: 180, y: 120, heading: 180, name: "East South" },
  // Center edges (4)
  { x: 0, y: -180, heading: 90, name: "North Center" },
  { x: 0, y: 180, heading: 270, name: "South Center" },
  { x: -180, y: 0, heading: 0, name: "West Center" },
  { x: 180, y: 0, heading: 180, name: "East Center" },
];

export default function RacePage() {
  const [gameState, setGameState] = useState<
    "lobby" | "waiting" | "racing" | "finished" | "crashed"
  >("lobby");
  const [username, setUsername] = useState("");

  const [playerId, setPlayerId] = useState<string | null>(null);
  const [raceId, setRaceId] = useState("permanent_lobby");

  const [x, setX] = useState(0);
  const [y, setY] = useState(0);
  const [heading, setHeading] = useState(0);
  const [speed, setSpeed] = useState(0);

  const [destinationX, setDestinationX] = useState(0);
  const [destinationY, setDestinationY] = useState(0);

  const [otherPlayers, setOtherPlayers] = useState<RenderPlayer[]>([]);

  const [stats, setStats] = useState({ time: 0, distance: 0 });

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const keysRef = useRef<{ [key: string]: boolean }>({});
  const startTimeRef = useRef<number | null>(null);
  const gameLoopRef = useRef<NodeJS.Timeout | null>(null);
  const joinCounterRef = useRef(0);
  const destinationRef = useRef({ x: 0, y: 0 });
  const otherPlayersRef = useRef<RenderPlayer[]>([]);
  const headingRef = useRef(heading);

  // Refs to track latest values for interval callbacks
  const xRef = useRef(x);
  const yRef = useRef(y);
  const speedRef = useRef(speed);
  const gameStateRef = useRef(gameState);
  const playerIdRef = useRef(playerId);
  const raceIdRef = useRef(raceId);

  // GPS conversion
  const gpsToMap = (lat: number, lon: number) => ({
    x: (lon + 89.401) * 1000,
    y: (lat - 43.073) * 1000,
  });
  const mapToGps = (x: number, y: number) => ({
    lat: y / 1000 + 43.073,
    lon: x / 1000 - 89.401,
  });

  // Keep refs in sync with state
  useEffect(() => {
    xRef.current = x;
  }, [x]);

  useEffect(() => {
    yRef.current = y;
  }, [y]);

  useEffect(() => {
    speedRef.current = speed;
  }, [speed]);

  useEffect(() => {
    gameStateRef.current = gameState;
  }, [gameState]);

  useEffect(() => {
    playerIdRef.current = playerId;
  }, [playerId]);

  useEffect(() => {
    raceIdRef.current = raceId;
  }, [raceId]);

  useEffect(() => {
    headingRef.current = heading;
  }, [heading]);

  useEffect(() => {
    destinationRef.current = { x: destinationX, y: destinationY };
  }, [destinationX, destinationY]);

  useEffect(() => {
    otherPlayersRef.current = otherPlayers;
  }, [otherPlayers]);

  // Road check
  const isCarWithinRoad = (px: number, py: number, headingDeg: number) => {
    const theta = (headingDeg * Math.PI) / 180;
    const cos = Math.cos(theta);
    const sin = Math.sin(theta);
    const sampleOffsets = [
      { dx: 0, dy: 0 },
      { dx: CAR_HALF_LENGTH, dy: 0 },
      { dx: -CAR_HALF_LENGTH, dy: 0 },
      { dx: 0, dy: CAR_HALF_WIDTH },
      { dx: 0, dy: -CAR_HALF_WIDTH },
    ];

    return sampleOffsets.every(({ dx, dy }) => {
      const rotatedX = px + dx * cos - dy * sin;
      const rotatedY = py + dx * sin + dy * cos;
      return isPointOnRoad(rotatedX, rotatedY);
    });
  };

  const joinRace = async () => {
    if (!username.trim()) {
      alert("Please enter your name");
      return;
    }

    joinCounterRef.current += 1;
    const pid = `player_${username}_${joinCounterRef.current}`;

    try {
      // Fetch existing players to find used spawn points
      const playersRes = await fetch(
        `${API_BASE}/race/admin/race/permanent_lobby/players`
      );
      const playersData: { players?: LobbyPlayer[] } = await playersRes.json();
      const existingPlayers = playersData.players || [];

      // Get used spawn points
      const usedSpawns = new Set<string>();
      existingPlayers.forEach((p) => {
        const spawn = gpsToMap(p.position.lat, p.position.lon);
        // Find closest spawn point
        let closestDist = Infinity;
        let closestSpawn = "";
        startPositions.forEach((sp) => {
          const dist = Math.sqrt((spawn.x - sp.x) ** 2 + (spawn.y - sp.y) ** 2);
          if (dist < closestDist && dist < 10) {
            // Within 10 units = same spawn
            closestDist = dist;
            closestSpawn = `${sp.x},${sp.y}`;
          }
        });
        if (closestSpawn) usedSpawns.add(closestSpawn);
      });

      // Select unused spawn point
      const availableSpawns = startPositions.filter(
        (sp) => !usedSpawns.has(`${sp.x},${sp.y}`)
      );
      if (availableSpawns.length === 0) {
        alert("All spawn points are taken! Please wait for a spot.");
        return;
      }

      const spawnIndex = (joinCounterRef.current - 1) % availableSpawns.length;
      const startPos = availableSpawns[spawnIndex];

      setX(startPos.x);
      setY(startPos.y);
      setHeading(startPos.heading);
      setPlayerId(pid);

      const gps = mapToGps(startPos.x, startPos.y);

      const res = await fetch(`${API_BASE}/race/player/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          player_id: pid,
          username: username,
          start_point_name: startPos.name,
          start_lat: gps.lat,
          start_lon: gps.lon,
        }),
      });

      if (!res.ok) {
        alert("Failed to join race.");
        return;
      }

      const data = await res.json();
      const dest = gpsToMap(data.destination.lat, data.destination.lon);
      setDestinationX(dest.x);
      setDestinationY(dest.y);

      // Update raceId from response
      if (data.race_id) {
        setRaceId(data.race_id);
      }

      setGameState("waiting");

      // Send initial position immediately
      setTimeout(() => {
        updatePosition();
      }, 100);
    } catch (err) {
      console.error("Error joining race:", err);
      alert("Error joining race");
    }
  };

  const fetchRaceInfo = useCallback(async () => {
    const currentPlayerId = playerIdRef.current;
    if (!currentPlayerId) return;

    try {
      const res = await fetch(
        `${API_BASE}/race/player/${currentPlayerId}/race`
      );
      const data = await res.json();

      if (data.status === "active" && gameStateRef.current === "waiting") {
        setGameState("racing");
        startTimeRef.current = Date.now();
      }

      if (data.your_status === "finished") {
        setGameState("finished");
      }

      if (data.your_status === "crashed") {
        setGameState("crashed");
      }
    } catch (err) {
      console.error("Error fetching race info:", err);
    }
  }, []);

  const fetchOtherPlayers = useCallback(async () => {
    const currentRaceId = raceIdRef.current;
    const currentPlayerId = playerIdRef.current;

    if (!currentRaceId || !currentPlayerId) return;

    try {
      const res = await fetch(
        `${API_BASE}/race/admin/race/${currentRaceId}/players`
      );
      const data: { players?: ApiPlayer[] } = await res.json();

      const others: RenderPlayer[] = (data.players || [])
        .filter((p) => p.player_id !== currentPlayerId)
        .map((p) => {
          const pos = gpsToMap(p.position.lat, p.position.lon);
          return {
            player_id: p.player_id,
            username: p.username,
            status: p.status,
            x: pos.x,
            y: pos.y,
          };
        });

      console.log("Other players:", others.length, others);
      setOtherPlayers(others);
    } catch (err) {
      console.error("Error fetching players:", err);
    }
  }, []);

  const updatePosition = useCallback(async () => {
    const currentPlayerId = playerIdRef.current;
    const currentX = xRef.current;
    const currentY = yRef.current;
    const currentSpeed = speedRef.current;

    if (!currentPlayerId) return;

    const gps = mapToGps(currentX, currentY);
    console.log("Sending position:", {
      playerId: currentPlayerId,
      x: currentX,
      y: currentY,
      gps,
      speed: currentSpeed,
    });

    try {
      const res = await fetch(`${API_BASE}/race/player/position`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          player_id: currentPlayerId,
          lat: gps.lat,
          lon: gps.lon,
          speed_mps: currentSpeed,
        }),
      });

      const data = await res.json();
      console.log("Position update response:", data);

      if (data.event === "finished") {
        setGameState("finished");
        setStats((prev) => ({ time: data.time, distance: prev.distance }));
      }

      if (data.event === "crashed") {
        setGameState("crashed");
        setSpeed(0);
        await fetchRaceInfo();
        fetchOtherPlayers();
      }

      if (gameStateRef.current === "racing") {
        await fetchRaceInfo();
      }
    } catch (err) {
      console.error("Error updating position:", err);
    }
  }, [fetchRaceInfo, fetchOtherPlayers]);

  const gameLoop = useCallback(() => {
    if (gameStateRef.current !== "racing") return;

    let newX = xRef.current;
    let newY = yRef.current;
    let newHeading = headingRef.current;
    let newSpeed = speedRef.current;

    const keys = keysRef.current;
    const turnSpeed = 3;
    const accel = 0.5;
    const maxSpeed = 5;
    const friction = 0.95;

    // Turn
    if (keys["ArrowLeft"] || keys["a"] || keys["A"]) newHeading -= turnSpeed;
    if (keys["ArrowRight"] || keys["d"] || keys["D"]) newHeading += turnSpeed;

    // Accelerate
    if (keys["ArrowUp"] || keys["w"] || keys["W"]) {
      newSpeed = Math.min(newSpeed + accel, maxSpeed);
    } else if (keys["ArrowDown"] || keys["s"] || keys["S"]) {
      newSpeed = Math.max(newSpeed - accel, -maxSpeed / 2);
    } else {
      newSpeed *= friction;
    }

    // Move
    const rad = (newHeading * Math.PI) / 180;
    newX += Math.cos(rad) * newSpeed;
    newY += Math.sin(rad) * newSpeed;

    // Bounds
    newX = Math.max(-200, Math.min(200, newX));
    newY = Math.max(-200, Math.min(200, newY));

    // Keep full car hitbox on the road
    if (!isCarWithinRoad(newX, newY, newHeading)) {
      const snapped = snapPointToRoad(newX, newY);
      newX = snapped.x;
      newY = snapped.y;
      newSpeed *= 0.5; // dampen speed if we hit a barrier
    }

    // Collision check with other players (check BEFORE movement to catch early)
    const COLLISION_RADIUS = 10; // match visual car size
    const WARNING_RADIUS = 14; // Check status if very close (might be collision)

    for (const other of otherPlayersRef.current) {
      if (other.status === "crashed" || other.status === "finished") continue;

      const distToOther = Math.sqrt(
        (newX - other.x) ** 2 + (newY - other.y) ** 2
      );

      // If very close, force immediate status check (backend might have detected collision)
      if (distToOther < WARNING_RADIUS) {
        // Check status immediately (non-blocking)
        fetchRaceInfo().catch(() => {});
      }

      if (distToOther < COLLISION_RADIUS) {
        // Collision! Both players crash immediately
        setGameState("crashed");
        // Stop movement
        setSpeed(0);
        setX(newX);
        setY(newY);
        updatePosition().then(() => {
          fetchRaceInfo();
          fetchOtherPlayers();
        });
        return;
      }
    }

    // Check finish - original finish detection (25 unit radius)
    const { x: destX, y: destY } = destinationRef.current;
    const distToFinish = Math.sqrt((newX - destX) ** 2 + (newY - destY) ** 2);
    if (distToFinish < 25) {
      setGameState("finished");
      const time = startTimeRef.current
        ? (Date.now() - startTimeRef.current) / 1000
        : 0;
      setStats((prev) => ({ time, distance: prev.distance + distToFinish }));
      return;
    }

    setX(newX);
    setY(newY);
    setHeading(newHeading);
    setSpeed(newSpeed);

    if (startTimeRef.current) {
      const time = (Date.now() - startTimeRef.current) / 1000;
      setStats((prev) => ({
        time,
        distance: prev.distance + Math.abs(newSpeed),
      }));
    }
  }, [fetchOtherPlayers, fetchRaceInfo, updatePosition]);

  const drawMap = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.fillStyle = "#1a472a";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const scale = canvas.width / MAP_SIZE;
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;

    // Draw complex winding roads
    drawRoadLayout(ctx, centerX, centerY, scale);

    // Draw destination (finish line)
    const dx = centerX + destinationX * scale;
    const dy = centerY + destinationY * scale;
    ctx.fillStyle = "#10b981";
    ctx.beginPath();
    ctx.arc(dx, dy, 20 * scale, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "white";
    ctx.font = `${20 * scale}px sans-serif`;
    ctx.textAlign = "center";
    ctx.fillText("🏁", dx, dy + 8 * scale);

    // Draw other players
    otherPlayers.forEach((p) => {
      const px = centerX + p.x * scale;
      const py = centerY + p.y * scale;

      let color = "#9ca3af";
      if (p.status === "finished") color = "#10b981";
      if (p.status === "crashed") color = "#ef4444";

      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(px, py, 6 * scale, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = "white";
      ctx.font = `${10 * scale}px sans-serif`;
      ctx.fillText(p.username, px, py - 10 * scale);
    });

    // Draw player
    const px = centerX + x * scale;
    const py = centerY + y * scale;

    ctx.save();
    ctx.translate(px, py);
    ctx.rotate((heading * Math.PI) / 180);

    ctx.fillStyle = "#3b82f6";
    ctx.beginPath();
    ctx.moveTo(12 * scale, 0);
    ctx.lineTo(-8 * scale, -6 * scale);
    ctx.lineTo(-8 * scale, 6 * scale);
    ctx.closePath();
    ctx.fill();

    ctx.restore();
  }, [destinationX, destinationY, heading, otherPlayers, x, y]);

  // Key handlers
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      keysRef.current[e.key] = true;
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      keysRef.current[e.key] = false;
    };

    window.addEventListener("keydown", handleKeyDown);
    window.addEventListener("keyup", handleKeyUp);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      window.removeEventListener("keyup", handleKeyUp);
    };
  }, []);

  // Game loop
  useEffect(() => {
    if (gameState === "racing") {
      gameLoopRef.current = setInterval(gameLoop, 1000 / 60);
      return () => {
        if (gameLoopRef.current) {
          clearInterval(gameLoopRef.current);
          gameLoopRef.current = null;
        }
      };
    }

    return () => {
      if (gameLoopRef.current) {
        clearInterval(gameLoopRef.current);
        gameLoopRef.current = null;
      }
    };
  }, [gameState, gameLoop]);

  // Update backend and fetch other players
  useEffect(() => {
    if ((gameState === "racing" || gameState === "waiting") && playerId) {
      let cancelled = false;

      const tick = async () => {
        if (cancelled) return;
        await updatePosition();
        await fetchRaceInfo();
        await fetchOtherPlayers();
      };

      tick();
      const interval = setInterval(tick, 50);

      return () => {
        cancelled = true;
        clearInterval(interval);
      };
    }
  }, [gameState, playerId, updatePosition, fetchRaceInfo, fetchOtherPlayers]);

  // Redraw map
  useEffect(() => {
    drawMap();
  }, [drawMap]);

  return (
    <div className="min-h-screen bg-linear-to-br from-gray-900 to-gray-800 text-white flex items-center justify-center p-5">
      {gameState === "lobby" && (
        <div className="max-w-md w-full bg-white/5 border border-white/10 rounded-2xl p-8">
          <h1 className="text-4xl font-bold text-center mb-6">
            Join the Race!
          </h1>

          <input
            type="text"
            placeholder="Your Name"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 mb-4"
          />

          <button
            onClick={joinRace}
            className="w-full px-6 py-3 bg-green-500 hover:bg-green-600 rounded-lg font-bold text-lg"
          >
            🏁 Join Race
          </button>
        </div>
      )}

      {gameState === "waiting" && (
        <div className="max-w-4xl w-full">
          <div className="bg-yellow-500/10 border border-yellow-500/50 rounded-2xl p-8 mb-6 text-center">
            <h1 className="text-4xl font-bold mb-3">
              ⏳ Waiting for Race Start
            </h1>
            <p className="text-gray-300 text-lg">
              Admin will start the race soon. Get ready!
            </p>
          </div>

          <canvas
            ref={canvasRef}
            width={600}
            height={600}
            className="w-full h-auto border-4 border-white/20 rounded-lg"
          />
        </div>
      )}

      {gameState === "racing" && (
        <div className="max-w-4xl w-full">
          <div className="grid grid-cols-4 gap-3 mb-4">
            <div className="bg-white/5 border border-white/10 rounded-lg p-3 text-center">
              <div className="text-sm text-gray-400">Time</div>
              <div className="text-xl font-bold">{stats.time.toFixed(1)}s</div>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-lg p-3 text-center">
              <div className="text-sm text-gray-400">Speed</div>
              <div className="text-xl font-bold">
                {Math.abs(speed).toFixed(1)}
              </div>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-lg p-3 text-center">
              <div className="text-sm text-gray-400">Distance</div>
              <div className="text-xl font-bold">
                {Math.floor(stats.distance)}m
              </div>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-lg p-3 text-center">
              <div className="text-sm text-gray-400">Status</div>
              <div className="text-xl font-bold text-green-500">Racing!</div>
            </div>
          </div>

          <canvas
            ref={canvasRef}
            width={600}
            height={600}
            className="w-full h-auto border-4 border-green-500/50 rounded-lg"
          />

          <div className="mt-4 text-center text-sm text-gray-400">
            🎮 Use Arrow Keys or WASD to drive · Stay on the road! · Reach the
            green flag 🏁
          </div>
        </div>
      )}

      {gameState === "finished" && (
        <div className="max-w-md w-full bg-green-500/10 border-2 border-green-500 rounded-2xl p-8 text-center">
          <h1 className="text-5xl font-bold text-green-500 mb-4">
            🏁 You Finished!
          </h1>
          <div className="text-3xl font-bold mb-2">
            {stats.time.toFixed(2)}s
          </div>
          <div className="text-lg text-gray-300">
            Distance: {Math.floor(stats.distance)}m
          </div>
        </div>
      )}

      {gameState === "crashed" && (
        <div className="max-w-md w-full bg-red-500/10 border-2 border-red-500 rounded-2xl p-8 text-center">
          <h1 className="text-5xl font-bold text-red-500 mb-4">
            💥 You Crashed!
          </h1>
          <p className="text-lg text-gray-300">
            You went crashed into another player.
          </p>
        </div>
      )}
    </div>
  );
}
