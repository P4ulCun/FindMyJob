FROM node:20-alpine

# Set working directory
WORKDIR /app

# Install dependencies (package.json is volume-mounted, but we copy for layer caching)
COPY package.json package-lock.json* ./
RUN npm install

# App code is volume-mounted, not copied (for HMR)
