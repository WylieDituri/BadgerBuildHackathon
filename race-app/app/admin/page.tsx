'use client';

import { useState, useEffect, useRef } from 'react';
import { drawRoadLayout } from '../../lib/roadLayout';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL;

interface Player {
  player_id: string;
  username: string;
  status: string;
  position: { lat: number; lon: number };
  destination: { lat: number; lon: number };
  speed: number;
}

interface AiReplayCar {
  id: string;
  start: { x: number; y: number };
  dest: { x: number; y: number };
}

export default function AdminPage() {
  const [lobbyId, setLobbyId] = useState('permanent_lobby');
  const [raceStatus, setRaceStatus] = useState('waiting');
  const [stats, setStats] = useState({ total: 0, racing: 0, finished: 0, crashed: 0 });
  const [leaderboard, setLeaderboard] = useState<any[]>([]);
  const [players, setPlayers] = useState<Player[]>([]);
  const [raceStartTime, setRaceStartTime] = useState<number | null>(null);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [collisions, setCollisions] = useState(0);
  const [raceEnded, setRaceEnded] = useState(false);
  const [finalStats, setFinalStats] = useState<{ totalTime: number; collisions: number } | null>(null);
  const [aiSimulation, setAiSimulation] = useState<{ running: boolean; time: number; collisions: number } | null>(null);
  const [showComparison, setShowComparison] = useState(false);
  const [aiReplay, setAiReplay] = useState<{ active: boolean; progress: number; cars: AiReplayCar[] }>({ active: false, progress: 0, cars: [] });

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const timerIntervalRef = useRef<NodeJS.Timeout>();
  const previousRaceStatusRef = useRef<string>('waiting');
  const raceStartTimeRef = useRef<number | null>(null);
  const hasAutoEndedRef = useRef(false);
  const humanSpawnPointsRef = useRef<Array<{ x: number; y: number; destX: number; destY: number }>>([]);
  const aiAnimationRef = useRef<NodeJS.Timeout>();
  const aiPlannedTimeRef = useRef(0);

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

    // Draw complex winding roads
    drawRoadLayout(ctx, centerX, centerY, scale);

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

    if (aiReplay.active || aiReplay.progress > 0) {
      const progress = aiReplay.progress;
      aiReplay.cars.forEach((car, idx) => {
        const ax = centerX + (car.start.x + (car.dest.x - car.start.x) * progress) * scale;
        const ay = centerY + (car.start.y + (car.dest.y - car.start.y) * progress) * scale;

        ctx.fillStyle = '#22d3ee';
        ctx.beginPath();
        ctx.arc(ax, ay, 6 * scale, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = '#a5f3fc';
        ctx.font = `${10 * scale}px sans-serif`;
        ctx.textAlign = 'center';
        ctx.fillText(`AI ${idx + 1}`, ax, ay - 10 * scale);
      });
    }
  };

  const fetchRaceStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/race/admin/race/${lobbyId}/status`);
      const data = await res.json();

      const newStatus = data.status || 'waiting';
      const newStats = data.players || { total: 0, racing: 0, finished: 0, crashed: 0 };
      const previousStatus = previousRaceStatusRef.current;
      
      setRaceStatus(newStatus);
      setStats(newStats);
      setLeaderboard(data.leaderboard || []);
      previousRaceStatusRef.current = newStatus;
      
      // Track race start time
      if (newStatus === 'active' && previousStatus !== 'active') {
        const startTime = Date.now();
        setRaceStartTime(startTime);
        raceStartTimeRef.current = startTime;
        setRaceEnded(false);
        setElapsedTime(0);
        setCollisions(0);
        setFinalStats(null);
        hasAutoEndedRef.current = false;
      }
      
      // Count collisions (pairs of crashed players)
      const crashedPlayers = newStats.crashed || 0;
      const collisionCount = Math.ceil(crashedPlayers / 2);
      setCollisions(collisionCount);
      
      // Auto-end if everyone is done (finished or crashed)
      if (newStatus === 'active' && newStats.total > 0 && !hasAutoEndedRef.current) {
        const totalDone = (newStats.finished || 0) + (newStats.crashed || 0);
        if (totalDone >= newStats.total) {
          // Everyone is done - auto-end race
          hasAutoEndedRef.current = true; // Prevent multiple calls
          
          // Find the longest finish time from leaderboard (last person to finish)
          let longestTime = 0;
          console.log('Checking leaderboard for times:', data.leaderboard);
          data.leaderboard?.forEach((entry: any) => {
            console.log('Leaderboard entry:', entry);
            if (entry.status === 'finished' && entry.time != null) {
              longestTime = Math.max(longestTime, entry.time);
            }
          });
          
          // If no finishers with time, use current elapsed time
          const totalTime = longestTime > 0 ? longestTime : elapsedTime;
          
          console.log('Auto-ending race:', { 
            longestTime, 
            totalTime, 
            elapsed: elapsedTime, 
            leaderboard: data.leaderboard,
            finished: newStats.finished 
          });
          
          setFinalStats({
            totalTime,
            collisions: collisionCount
          });
          
          // End the race
          fetch(`${API_BASE}/race/admin/race/${lobbyId}/end`, { method: 'POST' })
            .then(() => {
              setRaceEnded(true);
              setRaceStartTime(null);
              raceStartTimeRef.current = null;
              setShowComparison(false); // Make sure comparison doesn't show yet
              
              if (timerIntervalRef.current) {
                clearInterval(timerIntervalRef.current);
              }
            })
            .catch(err => console.error('Failed to auto-end race:', err));
        }
      }
      
      // Reset if race ends manually
      if (newStatus === 'finished' && previousStatus === 'active' && !hasAutoEndedRef.current) {
        // Find the longest finish time from leaderboard
        let longestTime = 0;
        console.log('Manual end - checking leaderboard:', data.leaderboard);
        data.leaderboard?.forEach((entry: any) => {
          if (entry.status === 'finished' && entry.time != null) {
            longestTime = Math.max(longestTime, entry.time);
          }
        });
        
        const totalTime = longestTime > 0 ? longestTime : elapsedTime;
        
        console.log('Manual end - final time:', { longestTime, totalTime, elapsed: elapsedTime });
        
        setFinalStats({
          totalTime,
          collisions: Math.ceil((newStats.crashed || 0) / 2)
        });
        
        setRaceEnded(true);
        setRaceStartTime(null);
        raceStartTimeRef.current = null;
        setShowComparison(false); // Don't show comparison yet
        
        if (timerIntervalRef.current) {
          clearInterval(timerIntervalRef.current);
        }
      }
      
      // Reset flag when waiting for new race
      if (newStatus === 'waiting') {
        hasAutoEndedRef.current = false;
      }
    } catch (err) {
      console.error('Failed to fetch race status:', err);
      setStats({ total: 0, racing: 0, finished: 0, crashed: 0 });
    }
  };

  const fetchPlayers = async () => {
    try {
      const res = await fetch(`${API_BASE}/race/admin/race/${lobbyId}/players`);
      const data = await res.json();
      const playersList = data.players || [];
      setPlayers(playersList);
      
      // Store spawn points when race starts (for AI simulation later)
      // Store on first fetch where we have players, regardless of current state
      if (humanSpawnPointsRef.current.length === 0 && playersList.length > 0) {
        // Check if any player is racing or finished (means race has started)
        const raceHasStarted = playersList.some((p: Player) => 
          p.status === 'racing' || p.status === 'finished' || p.status === 'crashed'
        );
        
        if (raceHasStarted || raceStatus === 'active') {
          humanSpawnPointsRef.current = playersList.map((p: Player) => {
            const pos = gpsToMap(p.position.lat, p.position.lon);
            const dest = gpsToMap(p.destination.lat, p.destination.lon);
            return { x: pos.x, y: pos.y, destX: dest.x, destY: dest.y };
          });
          console.log('✅ Stored human spawn points:', humanSpawnPointsRef.current);
        }
      }
    } catch (err) {
      console.error('Failed to fetch players:', err);
    }
  };

  const runAiSimulation = () => {
    console.log('Starting AI simulation with spawn points:', humanSpawnPointsRef.current);
    
    if (humanSpawnPointsRef.current.length === 0) {
      alert('No spawn points stored! Make sure players were registered when the race started.');
      return;
    }
    
    const cars: AiReplayCar[] = humanSpawnPointsRef.current.map((spawn, index) => ({
      id: `ai_${index}`,
      start: { x: spawn.x, y: spawn.y },
      dest: { x: spawn.destX, y: spawn.destY }
    }));
    
    setAiReplay({ active: true, progress: 0, cars });
    setAiSimulation({ running: true, time: aiTime, collisions: 0 });
    setShowComparison(false);
    
    // Calculate optimal time: distance / optimal_speed
    // Optimal speed: 30 units/sec (vs human average ~20-25)
    // AI never crashes, takes optimal paths
    const optimalSpeed = 30; // units per second
    
    let maxTime = 0;
    humanSpawnPointsRef.current.forEach(spawn => {
      const distance = Math.sqrt(
        Math.pow(spawn.destX - spawn.x, 2) + 
        Math.pow(spawn.destY - spawn.y, 2)
      );
      const timeNeeded = distance / optimalSpeed;
      maxTime = Math.max(maxTime, timeNeeded);
      console.log('Spawn point distance:', { distance, timeNeeded, spawn });
    });
    
    // AI is 15% faster due to optimal pathing and coordination
    const aiTime = maxTime * 0.85;
    
    console.log('AI simulation calculated:', { 
      aiTime, 
      maxTime, 
      humanSpawns: humanSpawnPointsRef.current.length,
      humanTime: finalStats?.totalTime 
    });
    
    aiPlannedTimeRef.current = aiTime;
  };

  const startRace = async () => {
    try {
      await fetch(`${API_BASE}/race/admin/race/${lobbyId}/start`, { method: 'POST' });
      humanSpawnPointsRef.current = []; // Reset spawn points for new race
      alert('Race started!');
    } catch (err) {
      console.error('Failed to start race:', err);
    }
  };

  const endRace = async () => {
    try {
      await fetch(`${API_BASE}/race/admin/race/${lobbyId}/end`, { method: 'POST' });
      
      // Calculate final stats
      const endTime = Date.now();
      const startTime = raceStartTimeRef.current;
      const totalTime = startTime ? (endTime - startTime) / 1000 : elapsedTime;
      
      console.log('Manual end race:', { startTime, endTime, totalTime, elapsed: elapsedTime });
      
      setFinalStats({
        totalTime,
        collisions: collisions
      });
      
      setRaceEnded(true);
      setRaceStartTime(null);
      raceStartTimeRef.current = null;
      hasAutoEndedRef.current = true; // Prevent double-ending
      
      if (timerIntervalRef.current) {
        clearInterval(timerIntervalRef.current);
      }
    } catch (err) {
      console.error('Failed to end race:', err);
    }
  };

  // Timer for race
  useEffect(() => {
    if (raceStatus === 'active' && raceStartTimeRef.current) {
      timerIntervalRef.current = setInterval(() => {
        const now = Date.now();
        const startTime = raceStartTimeRef.current;
        const elapsed = startTime ? (now - startTime) / 1000 : 0;
        setElapsedTime(elapsed);
      }, 100); // Update every 100ms for smooth timer

      return () => {
        if (timerIntervalRef.current) {
          clearInterval(timerIntervalRef.current);
        }
      };
    } else {
      if (timerIntervalRef.current) {
        clearInterval(timerIntervalRef.current);
      }
    }
  }, [raceStatus]);

  // Poll for updates
  useEffect(() => {
    fetchRaceStatus();
    fetchPlayers();

    // Poll faster when race is active
    const pollInterval = raceStatus === 'active' ? 50 : 100;
    const interval = setInterval(() => {
      fetchRaceStatus();
      fetchPlayers();
    }, pollInterval);

    return () => clearInterval(interval);
  }, [lobbyId, raceStatus]);

  // AI replay animation
  useEffect(() => {
    if (!aiReplay.active || !aiSimulation) return;

    const durationMs = Math.max(aiPlannedTimeRef.current || aiSimulation.time, 0.1) * 1000;
    const start = Date.now();

    const tick = () => {
      const elapsed = Date.now() - start;
      const progress = Math.min(1, elapsed / durationMs);
      setAiReplay((prev) => ({ ...prev, progress }));

      if (progress >= 1) {
        if (aiAnimationRef.current) {
          clearInterval(aiAnimationRef.current);
          aiAnimationRef.current = undefined;
        }
        setAiReplay((prev) => ({ ...prev, active: false, progress: 1 }));
        setAiSimulation((prev) =>
          prev ? { running: false, time: prev.time, collisions: prev.collisions } : null
        );
        setShowComparison(true);
      }
    };

    tick();
    aiAnimationRef.current = window.setInterval(tick, 50);

    return () => {
      if (aiAnimationRef.current) {
        clearInterval(aiAnimationRef.current);
        aiAnimationRef.current = undefined;
      }
    };
  }, [aiReplay.active, aiSimulation]);

  // Redraw map whenever players update
  useEffect(() => {
    drawMap();
  }, [players, raceStatus, aiReplay]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 text-white p-6">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-5xl font-bold mb-6 text-center">🏁 Admin Control Panel</h1>

        {/* Summary Screen */}
        {raceEnded && finalStats && (
          <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-800 border-2 border-green-500 rounded-2xl p-8 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
              <h2 className="text-4xl font-bold text-center mb-6 text-green-500">🏁 Race Complete!</h2>
              
              {!showComparison ? (
                <div>
                  <h3 className="text-2xl font-bold text-center mb-4">Human Results</h3>
                  <div className="space-y-4 mb-6">
                    <div className="bg-white/5 rounded-lg p-4 text-center">
                      <div className="text-sm text-gray-400 mb-1">Total Time</div>
                      <div className="text-3xl font-bold">{finalStats.totalTime.toFixed(2)}s</div>
                    </div>
                    
                    <div className="bg-white/5 rounded-lg p-4 text-center">
                      <div className="text-sm text-gray-400 mb-1">Collisions</div>
                      <div className="text-3xl font-bold text-red-500">{finalStats.collisions}</div>
                    </div>
                    
                    <div className="bg-white/5 rounded-lg p-4 text-center">
                      <div className="text-sm text-gray-400 mb-1">Finished</div>
                      <div className="text-2xl font-bold text-green-500">{stats?.finished || 0}</div>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <button
                      onClick={runAiSimulation}
                      disabled={aiSimulation?.running}
                      className="w-full px-4 py-3 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-600 rounded-lg font-semibold text-lg"
                    >
                      {aiSimulation?.running ? '🤖 AI Simulation Running...' : '🤖 Run AI Comparison'}
                    </button>
                    
                    <button
                      onClick={() => {
                        setRaceEnded(false);
                        setFinalStats(null);
                        setRaceStartTime(null);
                        setElapsedTime(0);
                        setCollisions(0);
                        setAiSimulation(null);
                        setShowComparison(false);
                        humanSpawnPointsRef.current = [];
                      setAiReplay({ active: false, progress: 0, cars: [] });
                      }}
                      className="w-full px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded-lg font-semibold"
                    >
                      Close
                    </button>
                  </div>
                </div>
              ) : (
                <div>
                  <h3 className="text-2xl font-bold text-center mb-6">Human vs AI Comparison</h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                    {/* Human Results */}
                    <div className="bg-red-500/10 border-2 border-red-500 rounded-lg p-6">
                      <h4 className="text-xl font-bold text-center mb-4 text-red-400">👤 Humans (Chaos Mode)</h4>
                      <div className="space-y-3">
                        <div className="bg-white/5 rounded-lg p-3 text-center">
                          <div className="text-xs text-gray-400 mb-1">Time</div>
                          <div className="text-2xl font-bold">{finalStats.totalTime.toFixed(2)}s</div>
                        </div>
                        <div className="bg-white/5 rounded-lg p-3 text-center">
                          <div className="text-xs text-gray-400 mb-1">Collisions</div>
                          <div className="text-2xl font-bold text-red-500">{finalStats.collisions}</div>
                        </div>
                        <div className="bg-white/5 rounded-lg p-3 text-center">
                          <div className="text-xs text-gray-400 mb-1">Finished</div>
                          <div className="text-xl font-bold">{stats?.finished || 0} / {stats?.total || 0}</div>
                        </div>
                      </div>
                    </div>
                    
                    {/* AI Results */}
                    <div className="bg-green-500/10 border-2 border-green-500 rounded-lg p-6">
                      <h4 className="text-xl font-bold text-center mb-4 text-green-400">🤖 AI (Coordinated)</h4>
                      <div className="space-y-3">
                        <div className="bg-white/5 rounded-lg p-3 text-center">
                          <div className="text-xs text-gray-400 mb-1">Time</div>
                          <div className="text-2xl font-bold text-green-400">
                            {aiSimulation?.time.toFixed(2)}s
                          </div>
                        </div>
                        <div className="bg-white/5 rounded-lg p-3 text-center">
                          <div className="text-xs text-gray-400 mb-1">Collisions</div>
                          <div className="text-2xl font-bold text-green-500">{aiSimulation?.collisions || 0}</div>
                        </div>
                        <div className="bg-white/5 rounded-lg p-3 text-center">
                          <div className="text-xs text-gray-400 mb-1">Finished</div>
                          <div className="text-xl font-bold text-green-400">{stats?.total || 0} / {stats?.total || 0}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Improvement Stats */}
                  <div className="bg-blue-500/10 border border-blue-500 rounded-lg p-4 mb-6">
                    <h4 className="text-lg font-bold text-center mb-3 text-blue-400">📊 AI Improvement</h4>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center">
                        <div className="text-xs text-gray-400 mb-1">Faster By</div>
                        <div className="text-2xl font-bold text-green-400">
                          {((1 - (aiSimulation?.time || 0) / finalStats.totalTime) * 100).toFixed(0)}%
                        </div>
                      </div>
                      <div className="text-center">
                        <div className="text-xs text-gray-400 mb-1">Collisions Prevented</div>
                        <div className="text-2xl font-bold text-green-400">
                          {finalStats.collisions}
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <button
                    onClick={() => {
                      setRaceEnded(false);
                      setFinalStats(null);
                      setRaceStartTime(null);
                      setElapsedTime(0);
                      setCollisions(0);
                      setAiSimulation(null);
                      setShowComparison(false);
                      humanSpawnPointsRef.current = [];
                      setAiReplay({ active: false, progress: 0, cars: [] });
                    }}
                    className="w-full px-4 py-2 bg-green-500 hover:bg-green-600 rounded-lg font-semibold"
                  >
                    Close
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Controls */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white/5 border border-white/10 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">Race Status</div>
            <div className="text-2xl font-bold capitalize">{raceStatus}</div>
          </div>

          <div className="bg-white/5 border border-white/10 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">Elapsed Time</div>
            <div className="text-2xl font-bold">
              {raceStatus === 'active' ? elapsedTime.toFixed(1) : '0.0'}s
            </div>
          </div>

          <div className="bg-white/5 border border-white/10 rounded-lg p-4">
            <div className="text-sm text-gray-400 mb-1">Collisions</div>
            <div className="text-2xl font-bold text-red-500">{collisions}</div>
            <div className="text-sm text-gray-400 mt-1">
              {stats?.total || 0} Total · {stats?.racing || 0} Racing · {stats?.finished || 0} Finished
            </div>
          </div>

          <div className="bg-white/5 border border-white/10 rounded-lg p-4 space-y-2">
            <button
              onClick={startRace}
              disabled={raceStatus === 'active'}
              className="w-full px-4 py-2 bg-green-500 hover:bg-green-600 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-semibold"
            >
              🏁 Start Race
            </button>
            <button
              onClick={endRace}
              disabled={raceStatus !== 'active'}
              className="w-full px-4 py-2 bg-red-500 hover:bg-red-600 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-semibold"
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
                      {entry.time ? `${entry.time.toFixed(2)}s` : '—'}
                    </div>
                    <div className="text-sm text-gray-400">
                      {entry.distance ? `${entry.distance.toFixed(0)}m` : '—'}
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
