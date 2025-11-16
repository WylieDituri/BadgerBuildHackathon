import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 text-white flex items-center justify-center p-5">
      <div className="max-w-4xl w-full">
        <h1 className="text-6xl font-bold text-center mb-4">🏁 Carmonic Racing</h1>
        <p className="text-xl text-center text-gray-400 mb-12">AI-Powered Traffic Coordination Demo</p>

        <div className="flex justify-center">
          {/* Player Card - Only visible option */}
          <Link href="/race">
            <div className="bg-white/5 border-2 border-green-500/50 rounded-2xl p-8 hover:bg-white/10 hover:border-green-500 transition cursor-pointer group max-w-md">
              <div className="text-6xl mb-4 text-center">🏎️</div>
              <h2 className="text-3xl font-bold text-center mb-3 text-green-500">Join Race</h2>
              <p className="text-center text-gray-400">
                Compete against other players in real-time. Use arrow keys or WASD to drive. Stay on the road!
              </p>
              <div className="mt-6 text-center">
                <span className="px-6 py-3 bg-green-500/20 rounded-lg text-green-400 font-semibold group-hover:bg-green-500/30">
                  Play Now →
                </span>
              </div>
            </div>
          </Link>
        </div>

        <div className="mt-12 p-6 bg-white/5 border border-white/10 rounded-xl">
          <h3 className="text-xl font-semibold mb-3 text-center">How It Works</h3>
          <div className="grid md:grid-cols-3 gap-4 text-sm text-gray-400">
            <div className="text-center">
              <div className="text-3xl mb-2">1️⃣</div>
              <p><strong className="text-white">Enter</strong> your name and join the lobby</p>
            </div>
            <div className="text-center">
              <div className="text-3xl mb-2">2️⃣</div>
              <p><strong className="text-white">Wait</strong> for the race to start</p>
            </div>
            <div className="text-center">
              <div className="text-3xl mb-2">3️⃣</div>
              <p><strong className="text-white">Race!</strong> Get to your destination first</p>
            </div>
          </div>
        </div>

        <div className="mt-6 text-center text-sm text-gray-500">
          Built with Next.js + FastAPI • Carmonic Traffic Intelligence System
        </div>
      </div>
    </div>
  );
}
