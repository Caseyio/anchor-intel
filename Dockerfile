# 1. Use official Node image (ARM64 & AMD64 compatible)
FROM node:20-bullseye

# 2. Set working directory
WORKDIR /app

# 3. Install only lockfile-defined dependencies (ensures deterministic builds)
COPY package*.json ./
RUN npm install

# 4. Copy source code after installing deps (preserves cache)
COPY . .

# 5. Rebuild native modules for target platform (especially for esbuild/rollup on ARM)
RUN npm rebuild esbuild \
 && npm rebuild @rollup/rollup-linux-arm64-gnu || echo "⚠️ rollup ARM64 rebuild skipped or not needed"

# 6. Optional: fix OpenSSL-related issues in some node environments
ENV NODE_OPTIONS="--openssl-legacy-provider"

# 7. Expose Vite development server port
EXPOSE 5173

# 8. Start Vite dev server (with hot reloading)
CMD ["npm", "run", "dev"]
