# ============================================================
# Multi-Stage Dockerfile for Next.js 15 Todo Frontend
# Target: Kubernetes deployment with minimal image size (<100MB)
# ============================================================

# ============================================================
# Stage 1: Dependencies Installation
# Purpose: Install all dependencies in a separate layer for caching
# ============================================================
FROM node:20-alpine AS deps

# Install libc6-compat for better Node.js compatibility on Alpine
RUN apk add --no-cache libc6-compat

WORKDIR /app

# Copy package files for dependency installation
# This layer is cached unless package files change
COPY package.json package-lock.json ./

# Install dependencies using npm ci for reproducible builds
# --omit=dev is not used here as we need devDependencies for build
RUN npm ci

# ============================================================
# Stage 2: Builder
# Purpose: Build the Next.js application with standalone output
# ============================================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy application source code
COPY . .

# Build arguments for Next.js environment variables
# INTERNAL_BACKEND_URL: server-side proxy destination (baked at build, not exposed to browser)
# NEXT_PUBLIC_API_BASE_URL: browser-side API base (empty = relative URLs through proxy)
ARG INTERNAL_BACKEND_URL=http://localhost:8000
ARG NEXT_PUBLIC_API_BASE_URL=
ARG NEXT_PUBLIC_CHAT_API_URL=
ARG NEXT_PUBLIC_OPENAI_DOMAIN_KEY=placeholder

# Set environment variables for build
ENV INTERNAL_BACKEND_URL=${INTERNAL_BACKEND_URL}
ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}
ENV NEXT_PUBLIC_CHAT_API_URL=${NEXT_PUBLIC_CHAT_API_URL}
ENV NEXT_PUBLIC_OPENAI_DOMAIN_KEY=${NEXT_PUBLIC_OPENAI_DOMAIN_KEY}
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

# Build Next.js application
# The standalone output will create a minimal server in .next/standalone/
RUN npm run build

# ============================================================
# Stage 3: Runner (Production Image)
# Purpose: Minimal production image with only runtime dependencies
# ============================================================
FROM node:20-alpine AS runner

WORKDIR /app

# Set production environment
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user with specific UID for security
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy necessary files from builder
# The standalone output includes all required dependencies
# Note: Next.js standalone output creates an 'app' subdirectory with server.js
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone/app ./
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Switch to non-root user
USER nextjs

# Expose port 3000
EXPOSE 3000

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/api/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})" || exit 1

# Set PORT environment variable (Next.js standalone uses this)
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Start the Next.js standalone server
CMD ["node", "server.js"]
