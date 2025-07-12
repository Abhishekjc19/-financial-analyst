const { logger } = require('../utils/logger');

/**
 * Request logging middleware
 * Logs incoming requests with relevant information
 */
const requestLogger = (req, res, next) => {
  const start = Date.now();
  
  // Log the incoming request
  logger.info('Incoming request', {
    method: req.method,
    url: req.originalUrl,
    ip: req.ip || req.connection.remoteAddress,
    userAgent: req.get('User-Agent'),
    timestamp: new Date().toISOString()
  });

  // Override res.end to log response
  const originalEnd = res.end;
  res.end = function(chunk, encoding) {
    const duration = Date.now() - start;
    
    // Log the response
    logger.info('Request completed', {
      method: req.method,
      url: req.originalUrl,
      statusCode: res.statusCode,
      duration: `${duration}ms`,
      contentLength: res.get('Content-Length') || 0,
      timestamp: new Date().toISOString()
    });

    // Call the original end method
    originalEnd.call(this, chunk, encoding);
  };

  next();
};

/**
 * Error logging middleware
 * Logs errors that occur during request processing
 */
const errorLogger = (err, req, res, next) => {
  logger.error('Request error', {
    method: req.method,
    url: req.originalUrl,
    error: err.message,
    stack: err.stack,
    timestamp: new Date().toISOString()
  });

  next(err);
};

/**
 * Performance monitoring middleware
 * Logs slow requests
 */
const performanceLogger = (threshold = 1000) => (req, res, next) => {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = Date.now() - start;
    
    if (duration > threshold) {
      logger.warn('Slow request detected', {
        method: req.method,
        url: req.originalUrl,
        duration: `${duration}ms`,
        threshold: `${threshold}ms`,
        timestamp: new Date().toISOString()
      });
    }
  });

  next();
};

/**
 * Security logging middleware
 * Logs potential security issues
 */
const securityLogger = (req, res, next) => {
  // Log suspicious requests
  const suspiciousPatterns = [
    /\.\.\//, // Directory traversal
    /<script/i, // XSS attempts
    /union\s+select/i, // SQL injection
    /eval\s*\(/i, // Code injection
  ];

  const url = req.originalUrl.toLowerCase();
  const userAgent = req.get('User-Agent') || '';

  for (const pattern of suspiciousPatterns) {
    if (pattern.test(url) || pattern.test(userAgent)) {
      logger.warn('Suspicious request detected', {
        method: req.method,
        url: req.originalUrl,
        ip: req.ip || req.connection.remoteAddress,
        userAgent,
        pattern: pattern.toString(),
        timestamp: new Date().toISOString()
      });
      break;
    }
  }

  next();
};

/**
 * API usage logging middleware
 * Logs API endpoint usage for analytics
 */
const apiUsageLogger = (req, res, next) => {
  // Only log API requests
  if (req.path.startsWith('/api/')) {
    const endpoint = req.path;
    const method = req.method;
    
    logger.info('API usage', {
      endpoint,
      method,
      ip: req.ip || req.connection.remoteAddress,
      timestamp: new Date().toISOString()
    });
  }

  next();
};

/**
 * Request body logging middleware (for debugging)
 * Logs request body for debugging purposes
 */
const bodyLogger = (req, res, next) => {
  if (req.body && Object.keys(req.body).length > 0) {
    logger.debug('Request body', {
      method: req.method,
      url: req.originalUrl,
      body: req.body,
      timestamp: new Date().toISOString()
    });
  }

  next();
};

/**
 * Response logging middleware (for debugging)
 * Logs response data for debugging purposes
 */
const responseLogger = (req, res, next) => {
  const originalSend = res.send;
  
  res.send = function(data) {
    logger.debug('Response data', {
      method: req.method,
      url: req.originalUrl,
      statusCode: res.statusCode,
      responseSize: data ? data.length : 0,
      timestamp: new Date().toISOString()
    });

    originalSend.call(this, data);
  };

  next();
};

module.exports = {
  requestLogger,
  errorLogger,
  performanceLogger,
  securityLogger,
  apiUsageLogger,
  bodyLogger,
  responseLogger
}; 