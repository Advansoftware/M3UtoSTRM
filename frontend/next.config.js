/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  images: {
    unoptimized: true
  },
  basePath: '',
  distDir: 'dist',
  assetPrefix: './',  // Importante para caminhos relativos
  env: {
    API_URL: process.env.NODE_ENV === 'development' 
      ? 'http://localhost:8000/api' 
      : '/api'
  }
}

module.exports = nextConfig
