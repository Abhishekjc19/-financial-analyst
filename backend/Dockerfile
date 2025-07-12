# Multi-stage build for Node.js API
FROM node:18-alpine AS base

# Install dependencies for node-gyp
RUN apk add --no-cache python3 make g++

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Development stage
FROM base AS development
RUN npm ci
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]

# Production stage
FROM base AS production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]

# Final stage
FROM production AS final
USER node 