/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable standalone output for Docker deployment
  // Source: https://nextjs.org/docs/app/api-reference/config/next-config-js/output
  // This creates a minimal server.js that can be deployed in a container
  output: "standalone",
  experimental: {
    serverActions: {
      bodySizeLimit: "10mb",
    },
  },
};

export default nextConfig;
