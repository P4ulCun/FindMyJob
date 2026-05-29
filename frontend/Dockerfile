# ───────────────────────── base (dependențe) ─────────────────────────
FROM node:20-alpine AS base
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci

# ───────────────────────── dev ─────────────────────────
# Codul vine prin volume mount; comanda (npm run dev) e în docker-compose.yml
FROM base AS dev

# ───────────────────────── build ─────────────────────────
FROM base AS build
COPY . .
RUN npm run build          # generează /app/dist

# ───────────────────────── prod (nginx) ─────────────────────────
FROM nginx:1.27-alpine AS prod
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]