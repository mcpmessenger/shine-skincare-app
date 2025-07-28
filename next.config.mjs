import nextPWA from 'next-pwa';

const withPWA = nextPWA({
  dest: 'public',
  disable: process.env.NODE_ENV === 'development',
});

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
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://shine-backend-final.eba-bpcnncyq.us-east-1.elasticbeanstalk.com',
  },
  // Disable static optimization for auth pages
  experimental: {
    // Remove invalid option
  },

}

export default withPWA(nextConfig);
