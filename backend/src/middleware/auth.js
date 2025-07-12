const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const { logger } = require('../utils/logger');
const { getSession, deleteSession } = require('../config/redis');
const { executeQuery } = require('../config/database');

// JWT token validation middleware
const validateToken = async (req, res, next) => {
  try {
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({
        success: false,
        error: 'Access token required',
        message: 'No authorization header or invalid format'
      });
    }

    const token = authHeader.substring(7); // Remove 'Bearer ' prefix
    
    if (!token) {
      return res.status(401).json({
        success: false,
        error: 'Access token required',
        message: 'Token not provided'
      });
    }

    try {
      // Verify JWT token
      const decoded = jwt.verify(token, process.env.JWT_SECRET);
      
      // Check if user session exists in Redis
      const session = await getSession(decoded.sessionId);
      if (!session) {
        return res.status(401).json({
          success: false,
          error: 'Invalid session',
          message: 'Session expired or invalid'
        });
      }

      // Verify user is still active
      const userQuery = 'SELECT id, email, first_name, last_name, is_active FROM users WHERE id = $1';
      const userResult = await executeQuery(userQuery, [decoded.userId]);
      
      if (userResult.rows.length === 0 || !userResult.rows[0].is_active) {
        // Delete invalid session
        await deleteSession(decoded.sessionId);
        return res.status(401).json({
          success: false,
          error: 'User not found or inactive',
          message: 'User account is inactive or deleted'
        });
      }

      // Attach user data to request
      req.user = {
        id: decoded.userId,
        sessionId: decoded.sessionId,
        email: userResult.rows[0].email,
        firstName: userResult.rows[0].first_name,
        lastName: userResult.rows[0].last_name
      };

      next();
    } catch (jwtError) {
      logger.error('JWT verification failed:', jwtError);
      return res.status(401).json({
        success: false,
        error: 'Invalid token',
        message: 'Token is invalid or expired'
      });
    }
  } catch (error) {
    logger.error('Authentication middleware error:', error);
    return res.status(500).json({
      success: false,
      error: 'Authentication error',
      message: 'Internal server error during authentication'
    });
  }
};

// Optional token validation (doesn't fail if no token)
const optionalAuth = async (req, res, next) => {
  try {
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return next(); // Continue without authentication
    }

    const token = authHeader.substring(7);
    
    if (!token) {
      return next(); // Continue without authentication
    }

    try {
      const decoded = jwt.verify(token, process.env.JWT_SECRET);
      const session = await getSession(decoded.sessionId);
      
      if (session) {
        const userQuery = 'SELECT id, email, first_name, last_name, is_active FROM users WHERE id = $1';
        const userResult = await executeQuery(userQuery, [decoded.userId]);
        
        if (userResult.rows.length > 0 && userResult.rows[0].is_active) {
          req.user = {
            id: decoded.userId,
            sessionId: decoded.sessionId,
            email: userResult.rows[0].email,
            firstName: userResult.rows[0].first_name,
            lastName: userResult.rows[0].last_name
          };
        }
      }
    } catch (jwtError) {
      // Token is invalid, but we continue without authentication
      logger.debug('Optional auth: Invalid token provided');
    }

    next();
  } catch (error) {
    logger.error('Optional authentication middleware error:', error);
    next(); // Continue without authentication
  }
};

// Generate JWT tokens
const generateTokens = (userId, sessionId) => {
  const accessToken = jwt.sign(
    { userId, sessionId },
    process.env.JWT_SECRET,
    { expiresIn: '15m' }
  );

  const refreshToken = jwt.sign(
    { userId, sessionId },
    process.env.JWT_REFRESH_SECRET,
    { expiresIn: '7d' }
  );

  return { accessToken, refreshToken };
};

// Hash password
const hashPassword = async (password) => {
  const saltRounds = 12;
  return await bcrypt.hash(password, saltRounds);
};

// Compare password
const comparePassword = async (password, hash) => {
  return await bcrypt.compare(password, hash);
};

// Generate session ID
const generateSessionId = () => {
  return require('crypto').randomBytes(32).toString('hex');
};

// Rate limiting for authentication endpoints
const authRateLimit = async (req, res, next) => {
  try {
    const ip = req.ip || req.connection.remoteAddress;
    const key = `auth_rate_limit:${ip}`;
    
    const { incrementRateLimit } = require('../config/redis');
    const current = await incrementRateLimit(key, 15 * 60 * 1000); // 15 minutes
    
    if (current > 5) { // 5 attempts per 15 minutes
      return res.status(429).json({
        success: false,
        error: 'Rate limit exceeded',
        message: 'Too many authentication attempts. Please try again later.'
      });
    }
    
    next();
  } catch (error) {
    logger.error('Rate limiting error:', error);
    next(); // Continue if rate limiting fails
  }
};

// Admin role validation
const requireAdmin = async (req, res, next) => {
  try {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        error: 'Authentication required',
        message: 'User must be authenticated'
      });
    }

    // Check if user has admin role (you can extend this based on your role system)
    const userQuery = 'SELECT role FROM users WHERE id = $1';
    const userResult = await executeQuery(userQuery, [req.user.id]);
    
    if (userResult.rows.length === 0 || userResult.rows[0].role !== 'admin') {
      return res.status(403).json({
        success: false,
        error: 'Insufficient permissions',
        message: 'Admin access required'
      });
    }

    next();
  } catch (error) {
    logger.error('Admin validation error:', error);
    return res.status(500).json({
      success: false,
      error: 'Authorization error',
      message: 'Internal server error during authorization'
    });
  }
};

// Logout middleware
const logout = async (req, res, next) => {
  try {
    if (req.user && req.user.sessionId) {
      await deleteSession(req.user.sessionId);
      
      // Also delete refresh token from database
      const deleteTokenQuery = 'DELETE FROM refresh_tokens WHERE user_id = $1 AND token = $2';
      await executeQuery(deleteTokenQuery, [req.user.id, req.user.sessionId]);
    }
    
    next();
  } catch (error) {
    logger.error('Logout error:', error);
    next(); // Continue even if logout cleanup fails
  }
};

module.exports = {
  validateToken,
  optionalAuth,
  generateTokens,
  hashPassword,
  comparePassword,
  generateSessionId,
  authRateLimit,
  requireAdmin,
  logout
}; 