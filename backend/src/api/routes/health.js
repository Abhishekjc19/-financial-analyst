const express = require('express');
const { logger } = require('../../utils/logger');
const { connectDatabase } = require('../../config/database');
const { connectRedis } = require('../../config/redis');

const router = express.Router();

// Health check endpoint
router.get('/', async (req, res) => {
  try {
    const health = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      environment: process.env.NODE_ENV || 'development',
      version: '1.0.0',
      services: {
        database: 'unknown',
        redis: 'unknown',
        api: 'healthy'
      }
    };

    // Check database connection
    try {
      await connectDatabase();
      health.services.database = 'healthy';
    } catch (error) {
      health.services.database = 'unhealthy';
      health.status = 'degraded';
      logger.error('Database health check failed:', error);
    }

    // Check Redis connection
    try {
      await connectRedis();
      health.services.redis = 'healthy';
    } catch (error) {
      health.services.redis = 'unhealthy';
      health.status = 'degraded';
      logger.error('Redis health check failed:', error);
    }

    const statusCode = health.status === 'healthy' ? 200 : 503;
    res.status(statusCode).json(health);

  } catch (error) {
    logger.error('Health check failed:', error);
    res.status(503).json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: error.message
    });
  }
});

// Detailed health check
router.get('/detailed', async (req, res) => {
  try {
    const detailedHealth = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      environment: process.env.NODE_ENV || 'development',
      version: '1.0.0',
      memory: {
        used: process.memoryUsage().heapUsed,
        total: process.memoryUsage().heapTotal,
        external: process.memoryUsage().external,
        rss: process.memoryUsage().rss
      },
      cpu: {
        usage: process.cpuUsage()
      },
      services: {
        database: {
          status: 'unknown',
          responseTime: 0,
          error: null
        },
        redis: {
          status: 'unknown',
          responseTime: 0,
          error: null
        },
        api: {
          status: 'healthy',
          responseTime: 0,
          error: null
        }
      },
      dependencies: {
        express: '4.18.2',
        node: process.version,
        platform: process.platform
      }
    };

    // Test database connection with timing
    const dbStart = Date.now();
    try {
      await connectDatabase();
      detailedHealth.services.database = {
        status: 'healthy',
        responseTime: Date.now() - dbStart,
        error: null
      };
    } catch (error) {
      detailedHealth.services.database = {
        status: 'unhealthy',
        responseTime: Date.now() - dbStart,
        error: error.message
      };
      detailedHealth.status = 'degraded';
    }

    // Test Redis connection with timing
    const redisStart = Date.now();
    try {
      await connectRedis();
      detailedHealth.services.redis = {
        status: 'healthy',
        responseTime: Date.now() - redisStart,
        error: null
      };
    } catch (error) {
      detailedHealth.services.redis = {
        status: 'unhealthy',
        responseTime: Date.now() - redisStart,
        error: error.message
      };
      detailedHealth.status = 'degraded';
    }

    const statusCode = detailedHealth.status === 'healthy' ? 200 : 503;
    res.status(statusCode).json(detailedHealth);

  } catch (error) {
    logger.error('Detailed health check failed:', error);
    res.status(503).json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      error: error.message
    });
  }
});

// Readiness check
router.get('/ready', async (req, res) => {
  try {
    const readiness = {
      ready: true,
      timestamp: new Date().toISOString(),
      checks: {
        database: false,
        redis: false,
        api: true
      }
    };

    // Check if database is ready
    try {
      await connectDatabase();
      readiness.checks.database = true;
    } catch (error) {
      readiness.checks.database = false;
      readiness.ready = false;
    }

    // Check if Redis is ready
    try {
      await connectRedis();
      readiness.checks.redis = true;
    } catch (error) {
      readiness.checks.redis = false;
      readiness.ready = false;
    }

    const statusCode = readiness.ready ? 200 : 503;
    res.status(statusCode).json(readiness);

  } catch (error) {
    logger.error('Readiness check failed:', error);
    res.status(503).json({
      ready: false,
      timestamp: new Date().toISOString(),
      error: error.message
    });
  }
});

// Liveness check
router.get('/live', (req, res) => {
  res.status(200).json({
    alive: true,
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

// System information
router.get('/system', (req, res) => {
  const systemInfo = {
    timestamp: new Date().toISOString(),
    process: {
      pid: process.pid,
      version: process.version,
      platform: process.platform,
      arch: process.arch,
      uptime: process.uptime()
    },
    memory: {
      used: process.memoryUsage().heapUsed,
      total: process.memoryUsage().heapTotal,
      external: process.memoryUsage().external,
      rss: process.memoryUsage().rss
    },
    environment: {
      nodeEnv: process.env.NODE_ENV || 'development',
      port: process.env.PORT || 3000
    },
    dependencies: {
      express: '4.18.2',
      node: process.version
    }
  };

  res.json(systemInfo);
});

// Metrics endpoint (redirects to Prometheus metrics)
router.get('/metrics', (req, res) => {
  res.redirect('/metrics');
});

module.exports = router; 