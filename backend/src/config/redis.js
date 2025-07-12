const redis = require('redis');
const { logger } = require('../utils/logger');

let client = null;

const createClient = () => {
  const config = {
    url: process.env.REDIS_URL || 'redis://localhost:6379',
    socket: {
      host: process.env.REDIS_HOST || 'localhost',
      port: process.env.REDIS_PORT || 6379,
      connectTimeout: 10000,
      lazyConnect: true
    },
    retry_strategy: (options) => {
      if (options.error && options.error.code === 'ECONNREFUSED') {
        logger.error('Redis server refused connection');
        return new Error('Redis server refused connection');
      }
      if (options.total_retry_time > 1000 * 60 * 60) {
        logger.error('Redis retry time exhausted');
        return new Error('Redis retry time exhausted');
      }
      if (options.attempt > 10) {
        logger.error('Redis max retry attempts reached');
        return undefined;
      }
      return Math.min(options.attempt * 100, 3000);
    }
  };

  return redis.createClient(config);
};

const connectRedis = async () => {
  try {
    client = createClient();
    
    // Set up event listeners
    client.on('error', (err) => {
      logger.error('Redis Client Error:', err);
    });
    
    client.on('connect', () => {
      logger.info('Redis client connected');
    });
    
    client.on('ready', () => {
      logger.info('Redis client ready');
    });
    
    client.on('end', () => {
      logger.info('Redis client disconnected');
    });
    
    // Connect to Redis
    await client.connect();
    
    // Test the connection
    await client.ping();
    logger.info('Redis connection established successfully');
    
    return client;
  } catch (error) {
    logger.error('Redis connection failed:', error);
    throw error;
  }
};

const getClient = () => {
  if (!client) {
    throw new Error('Redis not connected. Call connectRedis() first.');
  }
  return client;
};

const closeRedis = async () => {
  if (client) {
    await client.quit();
    logger.info('Redis connection closed');
  }
};

// Cache helper functions
const setCache = async (key, value, ttl = 3600) => {
  try {
    const serializedValue = typeof value === 'object' ? JSON.stringify(value) : value;
    await getClient().setEx(key, ttl, serializedValue);
    logger.debug(`Cache set: ${key}`);
  } catch (error) {
    logger.error(`Error setting cache for key ${key}:`, error);
  }
};

const getCache = async (key) => {
  try {
    const value = await getClient().get(key);
    if (value) {
      logger.debug(`Cache hit: ${key}`);
      try {
        return JSON.parse(value);
      } catch {
        return value;
      }
    }
    logger.debug(`Cache miss: ${key}`);
    return null;
  } catch (error) {
    logger.error(`Error getting cache for key ${key}:`, error);
    return null;
  }
};

const deleteCache = async (key) => {
  try {
    await getClient().del(key);
    logger.debug(`Cache deleted: ${key}`);
  } catch (error) {
    logger.error(`Error deleting cache for key ${key}:`, error);
  }
};

const clearCache = async (pattern = '*') => {
  try {
    const keys = await getClient().keys(pattern);
    if (keys.length > 0) {
      await getClient().del(keys);
      logger.info(`Cleared ${keys.length} cache entries with pattern: ${pattern}`);
    }
  } catch (error) {
    logger.error(`Error clearing cache with pattern ${pattern}:`, error);
  }
};

// Session management functions
const setSession = async (sessionId, userData, ttl = 86400) => {
  const key = `session:${sessionId}`;
  await setCache(key, userData, ttl);
};

const getSession = async (sessionId) => {
  const key = `session:${sessionId}`;
  return await getCache(key);
};

const deleteSession = async (sessionId) => {
  const key = `session:${sessionId}`;
  await deleteCache(key);
};

// Rate limiting functions
const incrementRateLimit = async (key, windowMs) => {
  try {
    const current = await getClient().incr(key);
    if (current === 1) {
      await getClient().expire(key, Math.floor(windowMs / 1000));
    }
    return current;
  } catch (error) {
    logger.error(`Error incrementing rate limit for key ${key}:`, error);
    return 0;
  }
};

const getRateLimit = async (key) => {
  try {
    const current = await getClient().get(key);
    return current ? parseInt(current) : 0;
  } catch (error) {
    logger.error(`Error getting rate limit for key ${key}:`, error);
    return 0;
  }
};

// Market data caching
const setMarketData = async (symbol, data, ttl = 300) => {
  const key = `market:${symbol}`;
  await setCache(key, data, ttl);
};

const getMarketData = async (symbol) => {
  const key = `market:${symbol}`;
  return await getCache(key);
};

const setAnalysisResult = async (symbol, analysisType, data, ttl = 1800) => {
  const key = `analysis:${symbol}:${analysisType}`;
  await setCache(key, data, ttl);
};

const getAnalysisResult = async (symbol, analysisType) => {
  const key = `analysis:${symbol}:${analysisType}`;
  return await getCache(key);
};

// Health check
const healthCheck = async () => {
  try {
    await getClient().ping();
    return { status: 'healthy', timestamp: new Date().toISOString() };
  } catch (error) {
    return { status: 'unhealthy', error: error.message, timestamp: new Date().toISOString() };
  }
};

module.exports = {
  connectRedis,
  getClient,
  closeRedis,
  setCache,
  getCache,
  deleteCache,
  clearCache,
  setSession,
  getSession,
  deleteSession,
  incrementRateLimit,
  getRateLimit,
  setMarketData,
  getMarketData,
  setAnalysisResult,
  getAnalysisResult,
  healthCheck
}; 