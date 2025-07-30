export default function TestPage() {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>🧪 Test Page</h1>
      <p>If you can see this, Next.js is working!</p>
              <p>Backend URL: {process.env.NEXT_PUBLIC_BACKEND_URL || 'https://d1kmi2r0duzr21.cloudfront.net'}</p>
      <p>Time: {new Date().toLocaleString()}</p>
    </div>
  );
} 