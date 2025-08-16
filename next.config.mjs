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
    // Remove domains config - not needed for local public folder images
    unoptimized: true,
  },

  // Remove hardcoded environment variable fallbacks that override code changes
  // Let the code handle its own defaults for better control
  // FORCE DEPLOYMENT: This comment ensures Amplify detects the change
  // TRIGGER NEW BUILD: Adding timestamp to force Amplify rebuild - August 15, 2025 8:45 PM
  experimental: {
    // Remove invalid option
  },
}

export default nextConfig;
