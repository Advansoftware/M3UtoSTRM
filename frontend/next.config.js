/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  images: {
    unoptimized: true
  },
  trailingSlash: true,
  distDir: 'dist',
  basePath: '',
  assetPrefix: './'
}

module.exports = nextConfig