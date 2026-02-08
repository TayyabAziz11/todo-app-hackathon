import type { NextConfig } from 'next';
import path from 'path';

// INTERNAL_BACKEND_URL is used server-side only (for proxy rewrites).
// It can be set at runtime (K8s env var) without rebuilding the image.
// NEXT_PUBLIC_API_BASE_URL is baked into the browser bundle at build time.
// When empty, the browser uses relative URLs (/api/...) which go through the proxy.
const INTERNAL_BACKEND = process.env.INTERNAL_BACKEND_URL || process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  // Proxy all /api/* requests to the FastAPI backend.
  // Uses INTERNAL_BACKEND_URL (server-only) so the proxy target is the internal
  // cluster DNS name, not the public LoadBalancer IP (which would cause a loop).
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${INTERNAL_BACKEND}/api/:path*`,
      },
    ];
  },
  // Fix: Explicitly set the output file tracing root to the parent directory
  // This prevents Next.js from incorrectly inferring the workspace root when
  // multiple package-lock.json files exist in parent directories
  // Note: In Next.js 15, this was moved from experimental to top level
  outputFileTracingRoot: path.join(__dirname, '../'),
};

export default nextConfig;
