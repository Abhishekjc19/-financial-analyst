const express = require('express');
const { body, validationResult } = require('express-validator');
const { logger } = require('../../utils/logger');
const { executeQuery } = require('../../config/database');
const { setSession, deleteSession } = require('../../config/redis');
const {
  generateTokens,
  hashPassword,
  comparePassword,
  generateSessionId,
  authRateLimit,
  logout
} = require('../../middleware/auth');

const router = express.Router();

// Validation rules
const registerValidation = [
  body('email')
    .isEmail()
    .normalizeEmail()
    .withMessage('Please provide a valid email address'),
  body('password')
    .isLength({ min: 8 })
    .withMessage('Password must be at least 8 characters long')
    .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/)
    .withMessage('Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character'),
  body('firstName')
    .trim()
    .isLength({ min: 2, max: 50 })
    .withMessage('First name must be between 2 and 50 characters'),
  body('lastName')
    .trim()
    .isLength({ min: 2, max: 50 })
    .withMessage('Last name must be between 2 and 50 characters')
];

const loginValidation = [
  body('email')
    .isEmail()
    .normalizeEmail()
    .withMessage('Please provide a valid email address'),
  body('password')
    .notEmpty()
    .withMessage('Password is required')
];

const refreshValidation = [
  body('refreshToken')
    .notEmpty()
    .withMessage('Refresh token is required')
];

// Register new user
router.post('/register', authRateLimit, registerValidation, async (req, res) => {
  try {
    // Check for validation errors
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        error: 'Validation failed',
        message: 'Please check your input',
        details: errors.array()
      });
    }

    const { email, password, firstName, lastName } = req.body;

    // Check if user already exists
    const existingUserQuery = 'SELECT id FROM users WHERE email = $1';
    const existingUserResult = await executeQuery(existingUserQuery, [email]);

    if (existingUserResult.rows.length > 0) {
      return res.status(409).json({
        success: false,
        error: 'User already exists',
        message: 'An account with this email already exists'
      });
    }

    // Hash password
    const passwordHash = await hashPassword(password);

    // Create user
    const createUserQuery = `
      INSERT INTO users (email, password_hash, first_name, last_name)
      VALUES ($1, $2, $3, $4)
      RETURNING id, email, first_name, last_name, created_at
    `;
    
    const createUserResult = await executeQuery(createUserQuery, [
      email,
      passwordHash,
      firstName,
      lastName
    ]);

    const user = createUserResult.rows[0];

    // Generate session and tokens
    const sessionId = generateSessionId();
    const { accessToken, refreshToken } = generateTokens(user.id, sessionId);

    // Store session in Redis
    await setSession(sessionId, {
      userId: user.id,
      email: user.email,
      firstName: user.firstName,
      lastName: user.lastName
    });

    // Store refresh token in database
    const storeTokenQuery = `
      INSERT INTO refresh_tokens (user_id, token, expires_at)
      VALUES ($1, $2, NOW() + INTERVAL '7 days')
    `;
    await executeQuery(storeTokenQuery, [user.id, sessionId]);

    logger.info(`New user registered: ${email}`);

    res.status(201).json({
      success: true,
      message: 'User registered successfully',
      data: {
        user: {
          id: user.id,
          email: user.email,
          firstName: user.firstName,
          lastName: user.lastName
        },
        tokens: {
          accessToken,
          refreshToken
        }
      },
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    logger.error('Registration error:', error);
    res.status(500).json({
      success: false,
      error: 'Registration failed',
      message: 'Internal server error during registration'
    });
  }
});

// Login user
router.post('/login', authRateLimit, loginValidation, async (req, res) => {
  try {
    // Check for validation errors
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        error: 'Validation failed',
        message: 'Please check your input',
        details: errors.array()
      });
    }

    const { email, password } = req.body;

    // Find user by email
    const userQuery = 'SELECT id, email, password_hash, first_name, last_name, is_active FROM users WHERE email = $1';
    const userResult = await executeQuery(userQuery, [email]);

    if (userResult.rows.length === 0) {
      return res.status(401).json({
        success: false,
        error: 'Invalid credentials',
        message: 'Email or password is incorrect'
      });
    }

    const user = userResult.rows[0];

    // Check if user is active
    if (!user.is_active) {
      return res.status(401).json({
        success: false,
        error: 'Account inactive',
        message: 'Your account has been deactivated'
      });
    }

    // Verify password
    const isPasswordValid = await comparePassword(password, user.password_hash);
    if (!isPasswordValid) {
      return res.status(401).json({
        success: false,
        error: 'Invalid credentials',
        message: 'Email or password is incorrect'
      });
    }

    // Generate session and tokens
    const sessionId = generateSessionId();
    const { accessToken, refreshToken } = generateTokens(user.id, sessionId);

    // Store session in Redis
    await setSession(sessionId, {
      userId: user.id,
      email: user.email,
      firstName: user.firstName,
      lastName: user.lastName
    });

    // Store refresh token in database
    const storeTokenQuery = `
      INSERT INTO refresh_tokens (user_id, token, expires_at)
      VALUES ($1, $2, NOW() + INTERVAL '7 days')
    `;
    await executeQuery(storeTokenQuery, [user.id, sessionId]);

    logger.info(`User logged in: ${email}`);

    res.json({
      success: true,
      message: 'Login successful',
      data: {
        user: {
          id: user.id,
          email: user.email,
          firstName: user.firstName,
          lastName: user.lastName
        },
        tokens: {
          accessToken,
          refreshToken
        }
      },
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    logger.error('Login error:', error);
    res.status(500).json({
      success: false,
      error: 'Login failed',
      message: 'Internal server error during login'
    });
  }
});

// Refresh access token
router.post('/refresh', refreshValidation, async (req, res) => {
  try {
    // Check for validation errors
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        error: 'Validation failed',
        message: 'Please check your input',
        details: errors.array()
      });
    }

    const { refreshToken } = req.body;

    // Verify refresh token
    const jwt = require('jsonwebtoken');
    let decoded;
    
    try {
      decoded = jwt.verify(refreshToken, process.env.JWT_REFRESH_SECRET);
    } catch (jwtError) {
      return res.status(401).json({
        success: false,
        error: 'Invalid refresh token',
        message: 'Refresh token is invalid or expired'
      });
    }

    // Check if refresh token exists in database
    const tokenQuery = `
      SELECT user_id, expires_at 
      FROM refresh_tokens 
      WHERE token = $1 AND expires_at > NOW()
    `;
    const tokenResult = await executeQuery(tokenQuery, [decoded.sessionId]);

    if (tokenResult.rows.length === 0) {
      return res.status(401).json({
        success: false,
        error: 'Invalid refresh token',
        message: 'Refresh token not found or expired'
      });
    }

    // Check if user is still active
    const userQuery = 'SELECT id, email, first_name, last_name, is_active FROM users WHERE id = $1';
    const userResult = await executeQuery(userQuery, [decoded.userId]);

    if (userResult.rows.length === 0 || !userResult.rows[0].is_active) {
      return res.status(401).json({
        success: false,
        error: 'User not found or inactive',
        message: 'User account is inactive or deleted'
      });
    }

    // Generate new access token
    const newAccessToken = jwt.sign(
      { userId: decoded.userId, sessionId: decoded.sessionId },
      process.env.JWT_SECRET,
      { expiresIn: '15m' }
    );

    logger.info(`Token refreshed for user: ${userResult.rows[0].email}`);

    res.json({
      success: true,
      message: 'Token refreshed successfully',
      data: {
        accessToken: newAccessToken
      },
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    logger.error('Token refresh error:', error);
    res.status(500).json({
      success: false,
      error: 'Token refresh failed',
      message: 'Internal server error during token refresh'
    });
  }
});

// Logout user
router.post('/logout', logout, (req, res) => {
  res.json({
    success: true,
    message: 'Logout successful',
    timestamp: new Date().toISOString()
  });
});

// Get current user profile
router.get('/profile', async (req, res) => {
  try {
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({
        success: false,
        error: 'Authentication required',
        message: 'Access token required'
      });
    }

    const token = authHeader.substring(7);
    const jwt = require('jsonwebtoken');
    
    try {
      const decoded = jwt.verify(token, process.env.JWT_SECRET);
      
      const userQuery = 'SELECT id, email, first_name, last_name, created_at FROM users WHERE id = $1';
      const userResult = await executeQuery(userQuery, [decoded.userId]);

      if (userResult.rows.length === 0) {
        return res.status(404).json({
          success: false,
          error: 'User not found',
          message: 'User profile not found'
        });
      }

      const user = userResult.rows[0];

      res.json({
        success: true,
        data: {
          user: {
            id: user.id,
            email: user.email,
            firstName: user.firstName,
            lastName: user.lastName,
            createdAt: user.created_at
          }
        },
        timestamp: new Date().toISOString()
      });

    } catch (jwtError) {
      return res.status(401).json({
        success: false,
        error: 'Invalid token',
        message: 'Token is invalid or expired'
      });
    }

  } catch (error) {
    logger.error('Profile fetch error:', error);
    res.status(500).json({
      success: false,
      error: 'Profile fetch failed',
      message: 'Internal server error while fetching profile'
    });
  }
});

module.exports = router; 