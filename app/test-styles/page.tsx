'use client';

export default function TestStylesPage() {
  return (
    <div className="min-h-screen bg-black text-white p-8">
      <h1 className="text-4xl font-bold mb-8">Tailwind CSS Test</h1>
      
      <div className="space-y-4">
        <div className="bg-blue-500 text-white p-4 rounded-lg">
          <h2 className="text-2xl font-semibold">Blue Card</h2>
          <p>This should have a blue background if Tailwind is working.</p>
        </div>
        
        <div className="bg-green-500 text-white p-4 rounded-lg">
          <h2 className="text-2xl font-semibold">Green Card</h2>
          <p>This should have a green background if Tailwind is working.</p>
        </div>
        
        <div className="bg-red-500 text-white p-4 rounded-lg">
          <h2 className="text-2xl font-semibold">Red Card</h2>
          <p>This should have a red background if Tailwind is working.</p>
        </div>
        
        <button className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded">
          Test Button
        </button>
        
        <input 
          type="text" 
          placeholder="Test input" 
          className="bg-white text-black p-2 rounded border"
        />
      </div>
      
      <div className="mt-8 p-4 bg-gray-800 rounded">
        <h3 className="text-xl font-semibold mb-2">CSS Variables Test</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-background text-foreground p-2 rounded border">
            Background/Foreground
          </div>
          <div className="bg-card text-card-foreground p-2 rounded border">
            Card/Card Foreground
          </div>
          <div className="bg-primary text-primary-foreground p-2 rounded border">
            Primary/Primary Foreground
          </div>
          <div className="bg-secondary text-secondary-foreground p-2 rounded border">
            Secondary/Secondary Foreground
          </div>
        </div>
      </div>
    </div>
  )
} 