# Source: https://github.com/vercel/next.js/tree/canary/examples/with-docker
# Next.js official Docker deployment example
# Docs: https://nextjs.org/docs/app/getting-started/deploying#docker
# Production checklist: https://nextjs.org/docs/app/guides/production-checklist

FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
# libc6-compat needed for Next.js on Alpine
# Ref: https://github.com/nodejs/docker-node/tree/main#nodealpine
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install pnpm via corepack (included in Node 20+)
RUN corepack enable pnpm

# Copy dependency manifest
COPY package.json pnpm-lock.yaml* ./

# Install dependencies with --frozen-lockfile for reproducible builds
# Ref: https://pnpm.io/cli/install#--frozen-lockfile
RUN --mount=type=cache,id=pnpm,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app

# Enable pnpm in builder stage
RUN corepack enable pnpm

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy application source
COPY . .

# Disable telemetry during build
# Ref: https://nextjs.org/telemetry
ENV NEXT_TELEMETRY_DISABLED=1

# Build Next.js with standalone output for minimal production image
# Ref: https://nextjs.org/docs/app/api-reference/config/next-config-js/output
RUN pnpm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

# Set production environment
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create system user for Next.js (security best practice)
# Ref: https://nextjs.org/docs/app/guides/production-checklist#security
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy public assets
COPY --from=builder /app/public ./public

# Set correct permissions for prerender cache
RUN mkdir .next && chown nextjs:nodejs .next

# Leverage output traces to reduce image size
# Ref: https://nextjs.org/docs/app/api-reference/config/next-config-js/output#automatically-copying-traced-files
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Switch to non-root user
USER nextjs

EXPOSE 3000

ENV PORT=3000
# HOSTNAME 0.0.0.0 allows connections from outside the container
ENV HOSTNAME="0.0.0.0"

# Run standalone server.js created by Next.js build
# Ref: https://nextjs.org/docs/app/api-reference/config/next-config-js/output#how-it-works
CMD ["node", "server.js"]
