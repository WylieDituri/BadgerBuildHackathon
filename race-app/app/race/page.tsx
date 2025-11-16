'use client';

import { useState, useEffect, useRef } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL;

interface StartPosition {
  x: number;
  y: number;
  heading: number;
  name: string;
}

const ROAD_WIDTH = 24;
const MAP_SIZE = 400;

const startPositions: StartPosition[] = [
  { x: -180, y: -180, heading: 45, name: 'North West Corner' },
  { x: 180, y: -180, heading: 135, name: 'North East Corner' },
  { x: -180, y: 180, heading: 315, name: 'South West Corner' },
  { x: 180, y: 180, heading: 225, name: 'South East Corner' },
  { x: 0, y: -180, heading: 90, name: 'North Edge' },
  { x: 0, y: 180, heading: 270, name: 'South Edge' },
  { x: -180, y: 0, heading: 0, name: 'West Edge' },
  { x: 180, y: 0, heading: 180, name: 'East Edge' },
];

export default function RacePage() {
  const [gameState, setGameState] = useState<'lobby' | 'waiting' | 'racing' | 'finished' | 'crashed'>('lobby');
  const [username, setUsername] = useState('');
  
  const [playerId, setPlayerId] = useState<string | null>(null);
  const [raceId, setRaceId] = useState('permanent_lobby');
  
  const [x, setX] = useState(0);
  const [y, setY] = useState(0);
  const [heading, setHeading] = useState(0);
  const [speed, setSpeed] = useState(0);
  
  const [destinationX, setDestinationX] = useState(0);
  const [destinationY, setDestinationY] = useState(0);
  
  const [offroadTime, setOffroadTime] = useState(0);
  const [otherPlayers, setOtherPlayers] = useState<any[]>([]);
  const [raceStatus, setRaceStatus] = useState('waiting');
  
  const [stats, setStats] = useState({ time: 0, distance: 0 });
  
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const keysRef = useRef<{ [key: string]: boolean }>({});
  const startTimeRef = useRef<number | null>(null);
  const gameLoopRef = useRef<NodeJS.Timeout>();
  const lastOffroadCheckRef = useRef<number>(Date.now());
  
  // Refs to track latest values for interval callbacks
  const xRef = useRef(x);
  const yRef = useRef(y);
  const speedRef = useRef(speed);
  const gameStateRef = useRef(gameState);
  const playerIdRef = useRef(playerId);
  const raceIdRef = useRef(raceId);

  // GPS conversion
  const gpsToMap = (lat: number, lon: number) => ({ x: (lon + 89.401) * 1000, y: (lat - 43.073) * 1000 });
  const mapToGps = (x: number, y: number) => ({ lat: y / 1000 + 43.073, lon: x / 1000 - 89.401 });

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

  // Road check
  const isOnRoad = (px: number, py: number): boolean => {
    // Horizontal roads every 60 units
    for (let roadY = -180; roadY <= 180; roadY += 60) {
      if (Math.abs(py - roadY) < ROAD_WIDTH / 2 && px >= -200 && px <= 200) return true;
    }
    // Vertical roads every 60 units
    for (let roadX = -180; roadX <= 180; roadX += 60) {
      if (Math.abs(px - roadX) < ROAD_WIDTH / 2 && py >= -200 && py <= 200) return true;
    }
    return false;
  };

  const joinRace = async () => {
    if (!username.trim()) {
      alert('Please enter your name');
      return;
    }

    const pid = `player_${username}_${Date.now()}`;
    const startPos = startPositions[Math.floor(Math.random() * startPositions.length)];
    
    setX(startPos.x);
    setY(startPos.y);
    setHeading(startPos.heading);
    setPlayerId(pid);

    try {
      const gps = mapToGps(startPos.x, startPos.y);
      
      const res = await fetch(`${API_BASE}/race/player/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          player_id: pid,
          username: username,
          start_point_name: startPos.name,
          start_lat: gps.lat,
          start_lon: gps.lon
        })
      });

      if (!res.ok) {
        alert('Failed to join race.');
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

      setGameState('waiting');
      
      // Send initial position immediately
      setTimeout(() => {
        updatePosition();
      }, 100);
    } catch (err) {
      console.error('Error joining race:', err);
      alert('Error joining race');
    }
  };

  const updatePosition = async () => {
    // Use refs to get latest values
    const currentPlayerId = playerIdRef.current;
    const currentX = xRef.current;
    const currentY = yRef.current;
    const currentSpeed = speedRef.current;
    
    if (!currentPlayerId) return;
    // Send position updates in both 'waiting' and 'racing' states

    const gps = mapToGps(currentX, currentY);
    console.log('Sending position:', { playerId: currentPlayerId, x: currentX, y: currentY, gps, speed: currentSpeed });
    
    try {
      const res = await fetch(`${API_BASE}/race/player/position`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          player_id: currentPlayerId,
          lat: gps.lat,
          lon: gps.lon,
          speed_mps: currentSpeed
        })
      });

      const data = await res.json();
      console.log('Position update response:', data);
      
      if (data.event === 'finished') {
        setGameState('finished');
        setStats(prev => ({ time: data.time, distance: prev.distance }));
      }
      
      if (data.event === 'crashed') {
        setGameState('crashed');
      }
    } catch (err) {
      console.error('Error updating position:', err);
    }
  };

  const fetchRaceInfo = async () => {
    if (!playerId) return;

    try {
      const res = await fetch(`${API_BASE}/race/player/${playerId}/race`);
      const data = await res.json();
      
      setRaceStatus(data.status);
      
      if (data.status === 'active' && gameState === 'waiting') {
        setGameState('racing');
        startTimeRef.current = Date.now();
      }
      
      if (data.your_status === 'finished') {
        setGameState('finished');
      }
      
      if (data.your_status === 'crashed') {
        setGameState('crashed');
      }
    } catch (err) {
      console.error('Error fetching race info:', err);
    }
  };

  const fetchOtherPlayers = async () => {
    const currentRaceId = raceIdRef.current;
    const currentPlayerId = playerIdRef.current;
    
    if (!currentRaceId || !currentPlayerId) return;

    try {
      const res = await fetch(`${API_BASE}/race/admin/race/${currentRaceId}/players`);
      const data = await res.json();
      
      const others = (data.players || [])
        .filter((p: any) => p.player_id !== currentPlayerId)
        .map((p: any) => {
          const pos = gpsToMap(p.position.lat, p.position.lon);
          return { ...p, x: pos.x, y: pos.y };
        });
      
      console.log('Other players:', others.length, others);
      setOtherPlayers(others);
    } catch (err) {
      console.error('Error fetching players:', err);
    }
  };

  const gameLoop = () => {
    if (gameState !== 'racing') return;

    let newX = x;
    let newY = y;
    let newHeading = heading;
    let newSpeed = speed;

    const keys = keysRef.current;
    const turnSpeed = 3;
    const accel = 0.5;
    const maxSpeed = 5;
    const friction = 0.95;

    // Turn
    if (keys['ArrowLeft'] || keys['a'] || keys['A']) newHeading -= turnSpeed;
    if (keys['ArrowRight'] || keys['d'] || keys['D']) newHeading += turnSpeed;

    // Accelerate
    if (keys['ArrowUp'] || keys['w'] || keys['W']) {
      newSpeed = Math.min(newSpeed + accel, maxSpeed);
    } else if (keys['ArrowDown'] || keys['s'] || keys['S']) {
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

    // Off-road check
    const now = Date.now();
    if (!isOnRoad(newX, newY)) {
      const elapsed = (now - lastOffroadCheckRef.current) / 1000;
      setOffroadTime((prev) => prev + elapsed);
    } else {
      setOffroadTime(0);
    }
    lastOffroadCheckRef.current = now;

    // Crash if off-road > 3 seconds
    if (offroadTime > 3) {
      setGameState('crashed');
      return;
    }

    // Check finish
    const distToFinish = Math.sqrt((newX - destinationX) ** 2 + (newY - destinationY) ** 2);
    if (distToFinish < 25) {
      setGameState('finished');
      const time = startTimeRef.current ? (Date.now() - startTimeRef.current) / 1000 : 0;
      setStats({ time, distance: stats.distance + distToFinish });
      return;
    }

    setX(newX);
    setY(newY);
    setHeading(newHeading);
    setSpeed(newSpeed);

    // Update stats
    if (startTimeRef.current) {
      const time = (Date.now() - startTimeRef.current) / 1000;
      setStats({ time, distance: stats.distance + Math.abs(newSpeed) });
    }
  };

  const drawMap = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.fillStyle = '#1a472a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const scale = canvas.width / MAP_SIZE;
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;

    // Draw roads
    ctx.strokeStyle = '#2d3748';
    ctx.lineWidth = ROAD_WIDTH * scale;

    for (let y = -180; y <= 180; y += 60) {
      ctx.beginPath();
      ctx.moveTo(centerX - 200 * scale, centerY + y * scale);
      ctx.lineTo(centerX + 200 * scale, centerY + y * scale);
      ctx.stroke();
    }

    for (let x = -180; x <= 180; x += 60) {
      ctx.beginPath();
      ctx.moveTo(centerX + x * scale, centerY - 200 * scale);
      ctx.lineTo(centerX + x * scale, centerY + 200 * scale);
      ctx.stroke();
    }

    // Draw destination
    const dx = centerX + destinationX * scale;
    const dy = centerY + destinationY * scale;
    ctx.fillStyle = '#10b981';
    ctx.beginPath();
    ctx.arc(dx, dy, 20 * scale, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = 'white';
    ctx.font = `${20 * scale}px sans-serif`;
    ctx.textAlign = 'center';
    ctx.fillText('🏁', dx, dy + 8 * scale);

    // Draw other players
    otherPlayers.forEach((p) => {
      const px = centerX + p.x * scale;
      const py = centerY + p.y * scale;

      let color = '#9ca3af';
      if (p.status === 'finished') color = '#10b981';
      if (p.status === 'crashed') color = '#ef4444';

      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(px, py, 6 * scale, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = 'white';
      ctx.font = `${10 * scale}px sans-serif`;
      ctx.fillText(p.username, px, py - 10 * scale);
    });

    // Draw player
    const px = centerX + x * scale;
    const py = centerY + y * scale;

    ctx.save();
    ctx.translate(px, py);
    ctx.rotate((heading * Math.PI) / 180);

    ctx.fillStyle = '#3b82f6';
    ctx.beginPath();
    ctx.moveTo(12 * scale, 0);
    ctx.lineTo(-8 * scale, -6 * scale);
    ctx.lineTo(-8 * scale, 6 * scale);
    ctx.closePath();
    ctx.fill();

    ctx.restore();

    // Off-road warning
    if (offroadTime > 0) {
      const remaining = Math.max(0, 3 - offroadTime);
      ctx.fillStyle = '#ef4444';
      ctx.font = `bold ${16 * scale}px sans-serif`;
      ctx.textAlign = 'center';
      ctx.fillText(`OFF ROAD! ${remaining.toFixed(1)}s`, centerX, centerY - 150 * scale);
    }
  };

  // Key handlers
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      keysRef.current[e.key] = true;
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      keysRef.current[e.key] = false;
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, []);

  // Game loop
  useEffect(() => {
    if (gameState === 'racing') {
      gameLoopRef.current = setInterval(gameLoop, 1000 / 60);
      return () => {
        if (gameLoopRef.current) clearInterval(gameLoopRef.current);
      };
    }
  }, [gameState, x, y, heading, speed, destinationX, destinationY, offroadTime]);

  // Update backend and fetch other players
  useEffect(() => {
    if ((gameState === 'racing' || gameState === 'waiting') && playerId) {
      // Fetch immediately
      updatePosition();
      fetchRaceInfo();
      fetchOtherPlayers();
      
      // Then set up interval
      const interval = setInterval(() => {
        updatePosition();
        fetchRaceInfo();
        fetchOtherPlayers();
      }, 100); // More frequent updates

      return () => clearInterval(interval);
    }
  }, [gameState, playerId]); // Removed x, y, speed from deps to avoid recreating interval

  // Redraw map
  useEffect(() => {
    drawMap();
  }, [x, y, heading, destinationX, destinationY, otherPlayers, offroadTime]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 text-white flex items-center justify-center p-5">
      {gameState === 'lobby' && (
        <div className="max-w-md w-full bg-white/5 border border-white/10 rounded-2xl p-8">
          <h1 className="text-4xl font-bold text-center mb-6">Join the Race!</h1>
          
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

      {gameState === 'waiting' && (
        <div className="max-w-4xl w-full">
          <div className="bg-yellow-500/10 border border-yellow-500/50 rounded-2xl p-8 mb-6 text-center">
            <h1 className="text-4xl font-bold mb-3">⏳ Waiting for Race Start</h1>
            <p className="text-gray-300 text-lg">Admin will start the race soon. Get ready!</p>
          </div>

          <canvas
            ref={canvasRef}
            width={600}
            height={600}
            className="w-full h-auto border-4 border-white/20 rounded-lg"
          />
        </div>
      )}

      {gameState === 'racing' && (
        <div className="max-w-4xl w-full">
          <div className="grid grid-cols-4 gap-3 mb-4">
            <div className="bg-white/5 border border-white/10 rounded-lg p-3 text-center">
              <div className="text-sm text-gray-400">Time</div>
              <div className="text-xl font-bold">{stats.time.toFixed(1)}s</div>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-lg p-3 text-center">
              <div className="text-sm text-gray-400">Speed</div>
              <div className="text-xl font-bold">{Math.abs(speed).toFixed(1)}</div>
            </div>
            <div className="bg-white/5 border border-white/10 rounded-lg p-3 text-center">
              <div className="text-sm text-gray-400">Distance</div>
              <div className="text-xl font-bold">{Math.floor(stats.distance)}m</div>
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
            🎮 Use Arrow Keys or WASD to drive · Stay on the road! · Reach the green flag 🏁
          </div>
        </div>
      )}

      {gameState === 'finished' && (
        <div className="max-w-md w-full bg-green-500/10 border-2 border-green-500 rounded-2xl p-8 text-center">
          <h1 className="text-5xl font-bold text-green-500 mb-4">🏁 You Finished!</h1>
          <div className="text-3xl font-bold mb-2">{stats.time.toFixed(2)}s</div>
          <div className="text-lg text-gray-300">Distance: {Math.floor(stats.distance)}m</div>
        </div>
      )}

      {gameState === 'crashed' && (
        <div className="max-w-md w-full bg-red-500/10 border-2 border-red-500 rounded-2xl p-8 text-center">
          <h1 className="text-5xl font-bold text-red-500 mb-4">💥 You Crashed!</h1>
          <p className="text-lg text-gray-300">You went off-road for too long.</p>
        </div>
      )}
    </div>
  );
}
