const winston = require('winston');
const path = require('path');

// Define log levels
const levels = {
  error: 0,
  warn: 1,
  info: 2,
  http: 3,
  debug: 4
};

// Define colors for each level
const colors = {
  error: 'red',
  warn: 'yellow',
  info: 'green',
  http: 'magenta',
  debug: 'white'
};

// Tell winston that you want to link the colors
winston.addColors(colors);

// Define which level to log based on environment
const level = () => {
  const env = process.env.NODE_ENV || 'development';
  const isDevelopment = env === 'development';
  return isDevelopment ? 'debug' : 'warn';
};

// Define format for logs
const format = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss:ms' }),
  winston.format.colorize({ all: true }),
  winston.format.printf(
    (info) => `${info.timestamp} ${info.level}: ${info.message}`
  )
);

// Define format for file logs (without colors)
const fileFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss:ms' }),
  winston.format.errors({ stack: true }),
  winston.format.json()
);

// Define transports
const transports = [
  // Console transport
  new winston.transports.Console({
    format
  }),
  
  // Error log file
  new winston.transports.File({
    filename: path.join('logs', 'error.log'),
    level: 'error',
    format: fileFormat,
    maxsize: 5242880, // 5MB
    maxFiles: 5
  }),
  
  // Combined log file
  new winston.transports.File({
    filename: path.join('logs', 'combined.log'),
    format: fileFormat,
    maxsize: 5242880, // 5MB
    maxFiles: 5
  })
];

// Create the logger
const logger = winston.createLogger({
  level: level(),
  levels,
  transports
});

// Create a stream object for Morgan HTTP logging
const stream = {
  write: (message) => {
    logger.http(message.trim());
  }
};

// Create a custom logger for API requests
const apiLogger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({
      filename: path.join('logs', 'api.log'),
      maxsize: 5242880, // 5MB
      maxFiles: 5
    })
  ]
});

// Create a custom logger for database operations
const dbLogger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({
      filename: path.join('logs', 'database.log'),
      maxsize: 5242880, // 5MB
      maxFiles: 5
    })
  ]
});

// Create a custom logger for market data operations
const marketLogger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({
      filename: path.join('logs', 'market.log'),
      maxsize: 5242880, // 5MB
      maxFiles: 5
    })
  ]
});

// Helper functions for structured logging
const logRequest = (req, res, next) => {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = Date.now() - start;
    const logData = {
      method: req.method,
      url: req.url,
      status: res.statusCode,
      duration: `${duration}ms`,
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

const logError = (error, req = null) => {
  const errorData = {
    message: error.message,
    stack: error.stack,
    name: error.name,
    timestamp: new Date().toISOString()
  };
  
  if (req) {
    errorData.request = {
      method: req.method,
      url: req.url,
      ip: req.ip || req.connection.remoteAddress,
      userId: req.user?.id || 'anonymous'
    };
  }
  
  logger.error('Application Error', errorData);
};

const logDatabase = (operation, table, duration, success = true) => {
  const logData = {
    operation,
    table,
    duration: `${duration}ms`,
    success,
    timestamp: new Date().toISOString()
  };
  
  if (success) {
    dbLogger.info('Database Operation', logData);
  } else {
    dbLogger.error('Database Operation Failed', logData);
  }
};

const logMarketData = (operation, symbol, duration, success = true, dataPoints = 0) => {
  const logData = {
    operation,
    symbol,
    duration: `${duration}ms`,
    success,
    dataPoints,
    timestamp: new Date().toISOString()
  };
  
  if (success) {
    marketLogger.info('Market Data Operation', logData);
  } else {
    marketLogger.error('Market Data Operation Failed', logData);
  }
};

// Export the logger and helper functions
module.exports = {
  logger,
  apiLogger,
  dbLogger,
  marketLogger,
  stream,
  logRequest,
  logError,
  logDatabase,
  logMarketData
}; 