'use client'

import { useState } from 'react'
import { products } from '@/lib/products'

export default function TestImagesPage() {
  const [imageStatus, setImageStatus] = useState<Record<string, string>>({})

  const testImage = (productId: string, imagePath: string) => {
    setImageStatus(prev => ({ ...prev, [productId]: 'Loading...' }))
    
    const img = new Image()
    img.onload = () => {
      setImageStatus(prev => ({ ...prev, [productId]: '✅ Loaded successfully' }))
    }
    img.onerror = () => {
      setImageStatus(prev => ({ ...prev, [productId]: '❌ Failed to load' }))
    }
    img.src = imagePath
  }

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <h1 className="text-3xl font-bold mb-8">Product Image Test Page</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {products.map(product => (
          <div key={product.id} className="bg-white rounded-lg p-6 shadow-md">
            <h3 className="text-lg font-semibold mb-2">{product.name}</h3>
            <p className="text-sm text-gray-600 mb-2">ID: {product.id}</p>
            <p className="text-sm text-gray-600 mb-4">Path: {product.image}</p>
            
            <div className="mb-4">
              <img
                src={product.image}
                alt={product.name}
                className="w-full h-32 object-cover rounded border"
                onLoad={() => setImageStatus(prev => ({ ...prev, [product.id]: '✅ Loaded successfully' }))}
                onError={() => setImageStatus(prev => ({ ...prev, [product.id]: '❌ Failed to load' }))}
              />
            </div>
            
            <div className="mb-4">
              <button
                onClick={() => testImage(product.id, product.image)}
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                Test Image
              </button>
            </div>
            
            <div className="text-sm">
              <strong>Status:</strong> {imageStatus[product.id] || 'Not tested'}
            </div>
            
            <div className="mt-4 p-3 bg-gray-100 rounded text-xs">
              <strong>Debug Info:</strong><br/>
              Full URL: {typeof window !== 'undefined' ? window.location.origin + product.image : 'N/A'}<br/>
              Environment: {process.env.NODE_ENV}<br/>
              Is Local Dev: {process.env.NEXT_PUBLIC_IS_LOCAL_DEV}
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-8 p-6 bg-blue-50 rounded-lg">
        <h2 className="text-xl font-semibold mb-4">Environment Information</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <strong>NODE_ENV:</strong> {process.env.NODE_ENV}
          </div>
          <div>
            <strong>NEXT_PUBLIC_IS_LOCAL_DEV:</strong> {process.env.NEXT_PUBLIC_IS_LOCAL_DEV}
          </div>
          <div>
            <strong>Base URL:</strong> {typeof window !== 'undefined' ? window.location.origin : 'N/A'}
          </div>
          <div>
            <strong>Current Path:</strong> {typeof window !== 'undefined' ? window.location.pathname : 'N/A'}
          </div>
        </div>
      </div>
    </div>
  )
}
