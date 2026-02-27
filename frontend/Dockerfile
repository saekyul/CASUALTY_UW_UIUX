# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

# Install serve to run the app
RUN npm install -g serve

# Copy built application from build stage
COPY --from=build /app/build ./build

# Expose port
EXPOSE 3000

# Run the application
CMD ["serve", "-s", "build", "-l", "3000"]
