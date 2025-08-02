export default function SimpleTest() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-blue-600 mb-8 text-center">
          Simple Tailwind Test
        </h1>
        
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            If you can see this styled content, Tailwind is working!
          </h2>
          <p className="text-gray-600 mb-4">
            This is a simple test page to verify that Tailwind CSS is loading properly.
          </p>
          <div className="flex gap-4">
            <button className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded">
              Blue Button
            </button>
            <button className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded">
              Green Button
            </button>
            <button className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded">
              Red Button
            </button>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-blue-100 p-6 rounded-lg">
            <h3 className="text-lg font-semibold text-blue-800 mb-2">Blue Card</h3>
            <p className="text-blue-600">This card should have a blue background.</p>
          </div>
          <div className="bg-green-100 p-6 rounded-lg">
            <h3 className="text-lg font-semibold text-green-800 mb-2">Green Card</h3>
            <p className="text-green-600">This card should have a green background.</p>
          </div>
          <div className="bg-purple-100 p-6 rounded-lg">
            <h3 className="text-lg font-semibold text-purple-800 mb-2">Purple Card</h3>
            <p className="text-purple-600">This card should have a purple background.</p>
          </div>
        </div>
      </div>
    </div>
  )
} 