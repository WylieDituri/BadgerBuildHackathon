'use client';

import { useState, useEffect, useRef } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL;

interface Player {
  player_id: string;
  username: string;
  status: string;
  position: { lat: number; lon: number };
  destination: { lat: number; lon: number };
  speed: number;
}

export default function AdminPage() {
  const [lobbyId, setLobbyId] = useState('permanent_lobby');
  const [raceStatus, setRaceStatus] = useState('waiting');
  const [stats, setStats] = useState({ total: 0, racing: 0, finished: 0, crashed: 0 });
  const [leaderboard, setLeaderboard] = useState<any[]>([]);
  const [players, setPlayers] = useState<Player[]>([]);

  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Convert GPS to map coords
  const gpsToMap = (lat: number, lon: number) => {
    return {
      x: (lon + 89.401) * 1000,
      y: (lat - 43.073) * 1000
    };
  };

  const drawMap = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear
    ctx.fillStyle = '#1a472a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const MAP_SIZE = 400;
    const scale = canvas.width / MAP_SIZE;
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;

    // Draw grid roads
    ctx.strokeStyle = '#2d3748';
    ctx.lineWidth = 24 * scale;

    // Horizontal roads
    for (let y = -180; y <= 180; y += 60) {
      ctx.beginPath();
      ctx.moveTo(centerX - 200 * scale, centerY + y * scale);
      ctx.lineTo(centerX + 200 * scale, centerY + y * scale);
      ctx.stroke();
    }

    // Vertical roads
    for (let x = -180; x <= 180; x += 60) {
      ctx.beginPath();
      ctx.moveTo(centerX + x * scale, centerY - 200 * scale);
      ctx.lineTo(centerX + x * scale, centerY + 200 * scale);
      ctx.stroke();
    }

    // Draw all players
    players.forEach((player) => {
      const pos = gpsToMap(player.position.lat, player.position.lon);
      const dest = gpsToMap(player.destination.lat, player.destination.lon);

      const px = centerX + pos.x * scale;
      const py = centerY + pos.y * scale;
      const dx = centerX + dest.x * scale;
      const dy = centerY + dest.y * scale;

      // Draw destination for this player
      ctx.fillStyle = '#10b98150';
      ctx.beginPath();
      ctx.arc(dx, dy, 20 * scale, 0, Math.PI * 2);
      ctx.fill();

      // Draw player car
      let color = '#3b82f6'; // Blue
      if (player.status === 'finished') color = '#10b981'; // Green
      if (player.status === 'crashed') color = '#ef4444'; // Red

      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(px, py, 8 * scale, 0, Math.PI * 2);
      ctx.fill();

      // Draw username
      ctx.fillStyle = 'white';
      ctx.font = `${12 * scale}px sans-serif`;
      ctx.textAlign = 'center';
      ctx.fillText(player.username, px, py - 15 * scale);
    });
  };

  const fetchRaceStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/race/admin/race/${lobbyId}/status`);
      const data = await res.json();

      setRaceStatus(data.status || 'waiting');
      setStats(data.players || { total: 0, racing: 0, finished: 0, crashed: 0 });
      setLeaderboard(data.leaderboard || []);
    } catch (err) {
      console.error('Failed to fetch race status:', err);
      setStats({ total: 0, racing: 0, finished: 0, crashed: 0 });
    }
  };

  const fetchPlayers = async () => {
    try {
      const res = await fetch(`${API_BASE}/race/admin/race/${lobbyId}/players`);
      const data = await res.json();
      console.log('Fetched players:', data.players?.length || 0, data.players);
      setPlayers(data.players || []);
    } catch (err) {
      console.error('Failed to fetch players:', err);
    }
  };

  const startRace = async () => {
    try {
      await fetch(`${API_BASE}/race/admin/race/${lobbyId}/start`, { method: 'POST' });
      alert('Race started!');
    } catch (err) {
      console.error('Failed to start race:', err);
    }
  };

  const endRace = async () => {
    try {
      await fetch(`${API_BASE}/race/admin/race/${lobbyId}/end`, { method: 'POST' });
      alert('Race ended!');
    } catch (err) {
      console.error('Failed to end race:', err);
    }
  };

  // Poll for updates
  useEffect(() => {
    fetchRaceStatus();
    fetchPlayers();

    const interval = setInterval(() => {
      fetchRaceStatus();
      fetchPlayers();
    }, 100); // More frequent updates

    return () => clearInterval(interval);
  }, [lobbyId]);

  // Redraw map whenever players update
  useEffect(() => {
    drawMap();
  }, [players, raceStatus]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 text-white p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-5xl font-bold mb-6 text-center">🏁 Admin Control Panel</h1>

        {/* Controls */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white/5 border border-white/10 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">Race Status</div>
            <div className="text-2xl font-bold capitalize">{raceStatus}</div>
          </div>

          <div className="bg-white/5 border border-white/10 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">Players</div>
            <div className="text-2xl font-bold">{stats?.total || 0} Total</div>
            <div className="text-sm text-gray-400 mt-1">
              {stats?.racing || 0} Racing · {stats?.finished || 0} Finished · {stats?.crashed || 0} Crashed
            </div>
          </div>

          <div className="bg-white/5 border border-white/10 rounded-lg p-4 space-y-2">
            <button
              onClick={startRace}
              className="w-full px-4 py-2 bg-green-500 hover:bg-green-600 rounded-lg font-semibold"
            >
              🏁 Start Race
            </button>
            <button
              onClick={endRace}
              className="w-full px-4 py-2 bg-red-500 hover:bg-red-600 rounded-lg font-semibold"
            >
              🛑 End Race
            </button>
          </div>
        </div>

        {/* Map */}
        <div className="bg-white/5 border border-white/10 rounded-lg p-4 mb-6">
          <h2 className="text-xl font-bold mb-4">Live Map</h2>
          <canvas
            ref={canvasRef}
            width={800}
            height={800}
            className="w-full h-auto border border-white/20 rounded"
          />
        </div>

        {/* Leaderboard */}
        <div className="bg-white/5 border border-white/10 rounded-lg p-4">
          <h2 className="text-xl font-bold mb-4">Leaderboard</h2>
          {leaderboard.length > 0 ? (
            <div className="space-y-2">
              {leaderboard.map((entry, idx) => (
                <div
                  key={entry.player_id}
                  className="flex items-center justify-between bg-white/5 p-3 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <div className="text-2xl font-bold text-yellow-500">#{idx + 1}</div>
                    <div>
                      <div className="font-semibold">{entry.username}</div>
                      <div className="text-sm text-gray-400 capitalize">{entry.status}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold">
                      {entry.total_time ? `${entry.total_time.toFixed(2)}s` : '—'}
                    </div>
                    <div className="text-sm text-gray-400">
                      {entry.distance_traveled ? `${entry.distance_traveled.toFixed(0)}m` : '—'}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-gray-400 text-center py-8">No finishers yet</div>
          )}
        </div>
      </div>
    </div>
  );
}
