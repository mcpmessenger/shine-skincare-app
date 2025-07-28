'use client';

export default function TestStylesPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 text-white">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold mb-8 text-center">
          🎨 CSS Styles Test
        </h1>
        
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {/* Test Card 1 */}
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 shadow-2xl border border-white/20">
            <h2 className="text-xl font-semibold mb-4 text-blue-300">Primary Button</h2>
            <button className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition-all duration-200 transform hover:scale-105">
              Click Me
            </button>
          </div>
          
          {/* Test Card 2 */}
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 shadow-2xl border border-white/20">
            <h2 className="text-xl font-semibold mb-4 text-green-300">Secondary Button</h2>
            <button className="bg-gray-600 hover:bg-gray-700 text-white font-bold py-3 px-6 rounded-lg transition-all duration-200 transform hover:scale-105">
              Secondary
            </button>
          </div>
          
          {/* Test Card 3 */}
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 shadow-2xl border border-white/20">
            <h2 className="text-xl font-semibold mb-4 text-purple-300">Input Field</h2>
            <input 
              type="text" 
              className="bg-white/20 border border-white/30 text-white rounded-lg px-4 py-3 w-full placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400" 
              placeholder="Enter text..."
            />
          </div>
        </div>
        
        <div className="mt-12 text-center">
          <div className="bg-green-500/20 border border-green-400/30 rounded-lg p-6">
            <h3 className="text-2xl font-bold text-green-300 mb-4">✅ If you can see this styled content, CSS is working!</h3>
            <p className="text-green-200">
              This page uses Tailwind CSS classes for styling. If the styles are missing, 
              you'll see plain text and default browser styling.
            </p>
          </div>
        </div>
        
        <div className="mt-8 text-center">
          <a 
            href="/" 
            className="inline-block bg-white/10 hover:bg-white/20 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-200 border border-white/20"
          >
            ← Back to Home
          </a>
        </div>
      </div>
    </div>
  );
} 