/** @type {import('next').NextConfig} */
const nextConfig = {
  // Remove static export for Vercel API routes compatibility
  trailingSlash: false,
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    domains: ['localhost', 'your-backend-domain.com'],
    unoptimized: true,
  },
  // Remove hardcoded environment variable fallbacks that override code changes
  // Let the code handle its own defaults for better control
  experimental: {
    // Remove invalid option
  },
}

export default nextConfig;
