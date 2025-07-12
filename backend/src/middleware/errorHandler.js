const { logger, logError } = require('../utils/logger');

// Error handling middleware
const errorHandler = (err, req, res, next) => {
  // Log the error
  logError(err, req);

  // Default error values
  let statusCode = err.statusCode || 500;
  let message = err.message || 'Internal Server Error';
  let error = err.name || 'InternalServerError';

  // Handle specific error types
  if (err.name === 'ValidationError') {
    statusCode = 400;
    error = 'ValidationError';
    message = 'Validation failed';
  } else if (err.name === 'CastError') {
    statusCode = 400;
    error = 'CastError';
    message = 'Invalid data format';
  } else if (err.code === 11000) {
    statusCode = 409;
    error = 'DuplicateError';
    message = 'Duplicate entry found';
  } else if (err.name === 'JsonWebTokenError') {
    statusCode = 401;
    error = 'TokenError';
    message = 'Invalid token';
  } else if (err.name === 'TokenExpiredError') {
    statusCode = 401;
    error = 'TokenExpiredError';
    message = 'Token expired';
  } else if (err.name === 'UnauthorizedError') {
    statusCode = 401;
    error = 'UnauthorizedError';
    message = 'Unauthorized access';
  } else if (err.name === 'ForbiddenError') {
    statusCode = 403;
    error = 'ForbiddenError';
    message = 'Access forbidden';
  } else if (err.name === 'NotFoundError') {
    statusCode = 404;
    error = 'NotFoundError';
    message = 'Resource not found';
  } else if (err.name === 'RateLimitError') {
    statusCode = 429;
    error = 'RateLimitError';
    message = 'Too many requests';
  }

  // Prepare error response
  const errorResponse = {
    success: false,
    error: error,
    message: message,
    timestamp: new Date().toISOString(),
    path: req.originalUrl,
    method: req.method
  };

  // Add validation details if available
  if (err.details) {
    errorResponse.details = err.details;
  }

  // Add stack trace in development
  if (process.env.NODE_ENV === 'development') {
    errorResponse.stack = err.stack;
  }

  // Send error response
  res.status(statusCode).json(errorResponse);
};

// Async error wrapper
const asyncHandler = (fn) => {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};

// Custom error classes
class ValidationError extends Error {
  constructor(message, details = null) {
    super(message);
    this.name = 'ValidationError';
    this.statusCode = 400;
    this.details = details;
  }
}

class NotFoundError extends Error {
  constructor(message = 'Resource not found') {
    super(message);
    this.name = 'NotFoundError';
    this.statusCode = 404;
  }
}

class UnauthorizedError extends Error {
  constructor(message = 'Unauthorized access') {
    super(message);
    this.name = 'UnauthorizedError';
    this.statusCode = 401;
  }
}

class ForbiddenError extends Error {
  constructor(message = 'Access forbidden') {
    super(message);
    this.name = 'ForbiddenError';
    this.statusCode = 403;
  }
}

class DuplicateError extends Error {
  constructor(message = 'Duplicate entry found') {
    super(message);
    this.name = 'DuplicateError';
    this.statusCode = 409;
  }
}

class RateLimitError extends Error {
  constructor(message = 'Too many requests') {
    super(message);
    this.name = 'RateLimitError';
    this.statusCode = 429;
  }
}

class DatabaseError extends Error {
  constructor(message = 'Database operation failed') {
    super(message);
    this.name = 'DatabaseError';
    this.statusCode = 500;
  }
}

class ExternalServiceError extends Error {
  constructor(message = 'External service error') {
    super(message);
    this.name = 'ExternalServiceError';
    this.statusCode = 502;
  }
}

// Error response helper
const sendErrorResponse = (res, statusCode, error, message, details = null) => {
  const errorResponse = {
    success: false,
    error: error,
    message: message,
    timestamp: new Date().toISOString()
  };

  if (details) {
    errorResponse.details = details;
  }

  res.status(statusCode).json(errorResponse);
};

// Success response helper
const sendSuccessResponse = (res, data, message = 'Success', statusCode = 200) => {
  const response = {
    success: true,
    message: message,
    data: data,
    timestamp: new Date().toISOString()
  };

  res.status(statusCode).json(response);
};

module.exports = {
  errorHandler,
  asyncHandler,
  ValidationError,
  NotFoundError,
  UnauthorizedError,
  ForbiddenError,
  DuplicateError,
  RateLimitError,
  DatabaseError,
  ExternalServiceError,
  sendErrorResponse,
  sendSuccessResponse
}; 