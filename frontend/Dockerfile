# Stage 1: Build the React application
FROM node:20-alpine AS build-stage

WORKDIR /app

# Configure npm for better network reliability
RUN npm config set registry https://registry.npmmirror.com/ && \
    npm config set fetch-retry-mintimeout 20000 && \
    npm config set fetch-retry-maxtimeout 120000 && \
    npm config set fetch-retries 3

COPY package.json pnpm-lock.yaml ./

# Install pnpm and configure it
RUN npm install -g pnpm@latest && \
    pnpm config set registry https://registry.npmmirror.com/ && \
    pnpm config set network-timeout 300000

# Install dependencies with retry logic
RUN pnpm install --frozen-lockfile --prefer-offline || \
    pnpm install --frozen-lockfile || \
    npm install

COPY . .

# Build the React app
RUN pnpm build || npm run build

# Stage 2: Serve the application with Nginx
FROM nginx:1.25-alpine AS production-stage

# Copy Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built React app from build-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
