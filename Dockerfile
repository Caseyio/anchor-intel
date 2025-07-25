<<<<<<< HEAD
FROM python:3.11-slim

# Install WeasyPrint and system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libxml2 \
    libxslt1.1 \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy only the requirements file first (for caching purposes)
COPY requirements.txt ./

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the backend code
COPY . .

# Set environment (optional but recommended)
ENV ENVIRONMENT=production

# Expose FastAPI port
EXPOSE 8000

# Run Alembic migrations and start FastAPI with Uvicorn
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]
=======
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
>>>>>>> 15d4666c8d0bf3f9f370d56a403f13d0d2affe74
