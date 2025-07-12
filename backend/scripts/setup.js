#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const { logger } = require('../src/utils/logger');

console.log('🚀 Setting up Financial Analyst Backend...\n');

// Create necessary directories
const directories = [
  'logs',
  'uploads',
  'data',
  'models/saved',
  'database/init',
  'nginx',
  'nginx/ssl'
];

console.log('📁 Creating directories...');
directories.forEach(dir => {
  const fullPath = path.join(__dirname, '..', dir);
  if (!fs.existsSync(fullPath)) {
    fs.mkdirSync(fullPath, { recursive: true });
    console.log(`  ✓ Created: ${dir}`);
  } else {
    console.log(`  - Exists: ${dir}`);
  }
});

// Create .env file if it doesn't exist
const envPath = path.join(__dirname, '..', '.env');
const envExamplePath = path.join(__dirname, '..', 'env.example');

if (!fs.existsSync(envPath) && fs.existsSync(envExamplePath)) {
  console.log('\n📝 Creating .env file from template...');
  fs.copyFileSync(envExamplePath, envPath);
  console.log('  ✓ Created .env file');
  console.log('  ⚠️  Please update .env with your API keys and configuration');
} else if (fs.existsSync(envPath)) {
  console.log('\n  - .env file already exists');
}

// Create database initialization script
const dbInitPath = path.join(__dirname, '..', 'database', 'init', '01-init.sql');
const dbInitContent = `
-- Financial Analyst Database Initialization
-- This script sets up the initial database schema

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "timescaledb";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create stocks table
CREATE TABLE IF NOT EXISTS stocks (
    symbol VARCHAR(10) PRIMARY KEY,
    company_name VARCHAR(255),
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create stock_prices table with TimescaleDB
CREATE TABLE IF NOT EXISTS stock_prices (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    open DECIMAL(10,2),
    high DECIMAL(10,2),
    low DECIMAL(10,2),
    close DECIMAL(10,2),
    volume BIGINT,
    PRIMARY KEY (time, symbol)
);

-- Convert to hypertable
SELECT create_hypertable('stock_prices', 'time', if_not_exists => TRUE);

-- Create portfolios table
CREATE TABLE IF NOT EXISTS portfolios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    symbol VARCHAR(10) REFERENCES stocks(symbol),
    shares DECIMAL(10,4) NOT NULL,
    avg_price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create analysis_results table
CREATE TABLE IF NOT EXISTS analysis_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(10) REFERENCES stocks(symbol),
    analysis_type VARCHAR(50),
    data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create refresh_tokens table
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol ON stock_prices (symbol);
CREATE INDEX IF NOT EXISTS idx_stock_prices_time ON stock_prices (time DESC);
CREATE INDEX IF NOT EXISTS idx_portfolios_user_id ON portfolios (user_id);
CREATE INDEX IF NOT EXISTS idx_analysis_results_symbol ON analysis_results (symbol);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens (user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token ON refresh_tokens (token);

-- Create a function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_stocks_updated_at BEFORE UPDATE ON stocks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_portfolios_updated_at BEFORE UPDATE ON portfolios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
`;

if (!fs.existsSync(dbInitPath)) {
  fs.writeFileSync(dbInitPath, dbInitContent);
  console.log('  ✓ Created database initialization script');
}

// Create nginx configuration
const nginxConfigPath = path.join(__dirname, '..', 'nginx', 'nginx.conf');
const nginxConfig = `
events {
    worker_connections 1024;
}

http {
    upstream api_backend {
        server api:3000;
    }

    upstream ml_backend {
        server ml_service:8000;
    }

    server {
        listen 80;
        server_name localhost;

        # API routes
        location /api/ {
            proxy_pass http://api_backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # ML service routes
        location /ml/ {
            proxy_pass http://ml_backend/;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # Health check
        location /health {
            proxy_pass http://api_backend/health;
        }

        # API documentation
        location /api-docs {
            proxy_pass http://api_backend/api-docs;
        }
    }
}
`;

if (!fs.existsSync(nginxConfigPath)) {
  fs.writeFileSync(nginxConfigPath, nginxConfig);
  console.log('  ✓ Created nginx configuration');
}

// Create a basic health check route
const healthRoutePath = path.join(__dirname, '..', 'src', 'api', 'routes', 'health.js');
const healthRouteContent = `
const express = require('express');
const { logger } = require('../../utils/logger');
const { getPool } = require('../../config/database');
const { healthCheck: redisHealthCheck } = require('../../config/redis');

const router = express.Router();

// Health check endpoint
router.get('/', async (req, res) => {
  try {
    const health = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      environment: process.env.NODE_ENV || 'development',
      version: '1.0.0'
    };

    res.json({
      success: true,
      data: health
    });
  } catch (error) {
    logger.error('Health check error:', error);
    res.status(500).json({
      success: false,
      error: 'Health check failed',
      message: error.message
    });
  }
});

// Database health check
router.get('/db', async (req, res) => {
  try {
    const pool = getPool();
    const client = await pool.connect();
    await client.query('SELECT NOW()');
    client.release();

    res.json({
      success: true,
      data: {
        status: 'healthy',
        database: 'connected',
        timestamp: new Date().toISOString()
      }
    });
  } catch (error) {
    logger.error('Database health check error:', error);
    res.status(500).json({
      success: false,
      error: 'Database health check failed',
      message: error.message
    });
  }
});

// Redis health check
router.get('/redis', async (req, res) => {
  try {
    const health = await redisHealthCheck();
    res.json({
      success: true,
      data: health
    });
  } catch (error) {
    logger.error('Redis health check error:', error);
    res.status(500).json({
      success: false,
      error: 'Redis health check failed',
      message: error.message
    });
  }
});

module.exports = router;
`;

if (!fs.existsSync(healthRoutePath)) {
  fs.writeFileSync(healthRoutePath, healthRouteContent);
  console.log('  ✓ Created health check routes');
}

// Create metrics configuration
const metricsConfigPath = path.join(__dirname, '..', 'src', 'config', 'metrics.js');
const metricsConfig = `
const promClient = require('prom-client');

// Create a Registry to register the metrics
const register = new promClient.Registry();

// Enable the collection of default metrics
promClient.collectDefaultMetrics({ register });

// Custom metrics
const httpRequestDurationMicroseconds = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.1, 0.5, 1, 2, 5]
});

const httpRequestsTotal = new promClient.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status_code']
});

const activeConnections = new promClient.Gauge({
  name: 'active_connections',
  help: 'Number of active connections'
});

const databaseQueryDuration = new promClient.Histogram({
  name: 'database_query_duration_seconds',
  help: 'Duration of database queries in seconds',
  labelNames: ['operation', 'table'],
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 2, 5]
});

const marketDataRequests = new promClient.Counter({
  name: 'market_data_requests_total',
  help: 'Total number of market data requests',
  labelNames: ['symbol', 'type']
});

// Register the metrics
register.registerMetric(httpRequestDurationMicroseconds);
register.registerMetric(httpRequestsTotal);
register.registerMetric(activeConnections);
register.registerMetric(databaseQueryDuration);
register.registerMetric(marketDataRequests);

const setupMetrics = (app) => {
  // Metrics endpoint
  app.get('/metrics', async (req, res) => {
    try {
      res.set('Content-Type', register.contentType);
      res.end(await register.metrics());
    } catch (error) {
      res.status(500).end(error);
    }
  });
};

module.exports = {
  register,
  httpRequestDurationMicroseconds,
  httpRequestsTotal,
  activeConnections,
  databaseQueryDuration,
  marketDataRequests,
  setupMetrics
};
`;

if (!fs.existsSync(metricsConfigPath)) {
  fs.writeFileSync(metricsConfigPath, metricsConfig);
  console.log('  ✓ Created metrics configuration');
}

// Create request logger middleware
const requestLoggerPath = path.join(__dirname, '..', 'src', 'middleware', 'requestLogger.js');
const requestLoggerContent = `
const { logger } = require('../utils/logger');

const requestLogger = (req, res, next) => {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = Date.now() - start;
    const logData = {
      method: req.method,
      url: req.url,
      status: res.statusCode,
      duration: \`\${duration}ms\`,
      userAgent: req.get('User-Agent'),
      ip: req.ip || req.connection.remoteAddress,
      userId: req.user?.id || 'anonymous'
    };
    
    if (res.statusCode >= 400) {
      logger.warn('API Request', logData);
    } else {
      logger.http('API Request', logData);
    }
  });
  
  next();
};

module.exports = { requestLogger };
`;

if (!fs.existsSync(requestLoggerPath)) {
  fs.writeFileSync(requestLoggerPath, requestLoggerContent);
  console.log('  ✓ Created request logger middleware');
}

console.log('\n✅ Setup completed successfully!');
console.log('\n📋 Next steps:');
console.log('  1. Copy env.example to .env and configure your settings');
console.log('  2. Install dependencies: npm install');
console.log('  3. Start the services: docker-compose up -d');
console.log('  4. Run database migrations: npm run migrate');
console.log('  5. Start the development server: npm run dev');
console.log('\n🌐 Your API will be available at: http://localhost:3000');
console.log('📚 API Documentation: http://localhost:3000/api-docs');
console.log('💚 Health Check: http://localhost:3000/health'); 