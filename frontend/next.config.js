/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',  // Habilita exportação estática
  images: {
    unoptimized: true
  },
  trailingSlash: true,
  distDir: 'dist'
}

module.exports = nextConfig
