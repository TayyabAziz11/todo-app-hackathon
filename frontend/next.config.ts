import type { NextConfig } from 'next';
import path from 'path';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
  },
  // Fix: Explicitly set the output file tracing root to the parent directory
  // This prevents Next.js from incorrectly inferring the workspace root when
  // multiple package-lock.json files exist in parent directories
  // Note: In Next.js 15, this was moved from experimental to top level
  outputFileTracingRoot: path.join(__dirname, '../'),
};

export default nextConfig;
