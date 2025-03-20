/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000' // Changed port to 8000
  },
  server: {
    port: 8001 // Explicitly set Next.js to run on port 8001
  }
}

module.exports = nextConfig
