const express = require('express');
const { query, param, validationResult } = require('express-validator');
const { logger } = require('../../utils/logger');
const marketDataService = require('../../services/marketDataService');

const router = express.Router();

// Validation rules
const symbolValidation = [
  param('symbol')
    .isLength({ min: 1, max: 10 })
    .withMessage('Symbol must be between 1 and 10 characters')
    .matches(/^[A-Z.]+$/)
    .withMessage('Symbol must contain only uppercase letters and dots')
];

const periodValidation = [
  query('period')
    .optional()
    .isIn(['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'])
    .withMessage('Invalid period. Must be one of: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max'),
  query('interval')
    .optional()
    .isIn(['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'])
    .withMessage('Invalid interval. Must be one of: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo')
];

const searchValidation = [
  query('q')
    .isLength({ min: 2, max: 50 })
    .withMessage('Search query must be between 2 and 50 characters')
];

// Get market overview
router.get('/overview', async (req, res) => {
  try {
    logger.info('Fetching market overview');
    
    const overview = await marketDataService.getMarketOverview();
    
    res.json({
      success: true,
      message: 'Market overview retrieved successfully',
      data: overview,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    logger.error('Error fetching market overview:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch market overview',
      message: error.message
    });
  }
});

// Get stock data
router.get('/stock/:symbol', symbolValidation, periodValidation, async (req, res) => {
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

    const { symbol } = req.params;
    const { period = '1y', interval = '1d' } = req.query;

    logger.info(`Fetching stock data for ${symbol} (${period}, ${interval})`);
    
    const data = await marketDataService.getStockData(symbol, period, interval);
    
    res.json({
      success: true,
      message: 'Stock data retrieved successfully',
      data: {
        symbol,
        period,
        interval,
        dataPoints: data.length,
        data
      },
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    logger.error(`Error fetching stock data for ${req.params.symbol}:`, error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch stock data',
      message: error.message
    });
  }
});

// Get stock quote
router.get('/quote/:symbol', symbolValidation, async (req, res) => {
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

    const { symbol } = req.params;

    logger.info(`Fetching quote for ${symbol}`);
    
    const quote = await marketDataService.getStockQuote(symbol);
    
    res.json({
      success: true,
      message: 'Stock quote retrieved successfully',
      data: quote,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    logger.error(`Error fetching quote for ${req.params.symbol}:`, error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch stock quote',
      message: error.message
    });
  }
});

// Get sector performance
router.get('/sectors', async (req, res) => {
  try {
    logger.info('Fetching sector performance');
    
    const sectors = await marketDataService.getSectorPerformance();
    
    res.json({
      success: true,
      message: 'Sector performance retrieved successfully',
      data: sectors,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    logger.error('Error fetching sector performance:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch sector performance',
      message: error.message
    });
  }
});

// Search stocks
router.get('/search', searchValidation, async (req, res) => {
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

    const { q } = req.query;

    logger.info(`Searching stocks for query: ${q}`);
    
    const results = await marketDataService.searchStocks(q);
    
    res.json({
      success: true,
      message: 'Stock search completed successfully',
      data: {
        query: q,
        results: results,
        count: results.length
      },
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    logger.error(`Error searching stocks for ${req.query.q}:`, error);
    res.status(500).json({
      success: false,
      error: 'Failed to search stocks',
      message: error.message
    });
  }
});

// Get company information
router.get('/company/:symbol', symbolValidation, async (req, res) => {
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

    const { symbol } = req.params;

    logger.info(`Fetching company info for ${symbol}`);
    
    const companyInfo = await marketDataService.getCompanyInfo(symbol);
    
    res.json({
      success: true,
      message: 'Company information retrieved successfully',
      data: companyInfo,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    logger.error(`Error fetching company info for ${req.params.symbol}:`, error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch company information',
      message: error.message
    });
  }
});

// Get macroeconomic indicators
router.get('/macro', async (req, res) => {
  try {
    logger.info('Fetching macroeconomic indicators');
    
    const indicators = await marketDataService.getMacroIndicators();
    
    res.json({
      success: true,
      message: 'Macroeconomic indicators retrieved successfully',
      data: indicators,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    logger.error('Error fetching macro indicators:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch macroeconomic indicators',
      message: error.message
    });
  }
});

// Get historical data from database
router.get('/historical/:symbol', symbolValidation, async (req, res) => {
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

    const { symbol } = req.params;
    const { start, end } = req.query;

    if (!start || !end) {
      return res.status(400).json({
        success: false,
        error: 'Missing parameters',
        message: 'Start and end dates are required (YYYY-MM-DD format)'
      });
    }

    // Validate date format
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (!dateRegex.test(start) || !dateRegex.test(end)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid date format',
        message: 'Dates must be in YYYY-MM-DD format'
      });
    }

    logger.info(`Fetching historical data for ${symbol} from ${start} to ${end}`);
    
    const data = await marketDataService.getHistoricalData(symbol, start, end);
    
    res.json({
      success: true,
      message: 'Historical data retrieved successfully',
      data: {
        symbol,
        startDate: start,
        endDate: end,
        dataPoints: data.length,
        data
      },
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    logger.error(`Error fetching historical data for ${req.params.symbol}:`, error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch historical data',
      message: error.message
    });
  }
});

// Get multiple stock quotes (batch request)
router.post('/quotes/batch', async (req, res) => {
  try {
    const { symbols } = req.body;

    if (!symbols || !Array.isArray(symbols) || symbols.length === 0) {
      return res.status(400).json({
        success: false,
        error: 'Invalid request',
        message: 'Symbols array is required and must not be empty'
      });
    }

    if (symbols.length > 50) {
      return res.status(400).json({
        success: false,
        error: 'Too many symbols',
        message: 'Maximum 50 symbols allowed per request'
      });
    }

    logger.info(`Fetching batch quotes for ${symbols.length} symbols`);
    
    const quotes = {};
    const errors = [];

    // Fetch quotes in parallel
    const quotePromises = symbols.map(async (symbol) => {
      try {
        const quote = await marketDataService.getStockQuote(symbol);
        quotes[symbol] = quote;
      } catch (error) {
        logger.error(`Error fetching quote for ${symbol}:`, error);
        errors.push({ symbol, error: error.message });
      }
    });

    await Promise.all(quotePromises);
    
    res.json({
      success: true,
      message: 'Batch quotes retrieved successfully',
      data: {
        quotes,
        errors,
        total: symbols.length,
        successful: Object.keys(quotes).length,
        failed: errors.length
      },
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    logger.error('Error fetching batch quotes:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch batch quotes',
      message: error.message
    });
  }
});

// Get market indices
router.get('/indices', async (req, res) => {
  try {
    const indices = ['^GSPC', '^DJI', '^IXIC', '^VIX', '^RUT', '^FTSE'];
    const quotes = {};
    const errors = [];

    logger.info('Fetching market indices');

    // Fetch indices in parallel
    const quotePromises = indices.map(async (index) => {
      try {
        const quote = await marketDataService.getStockQuote(index);
        quotes[index] = quote;
      } catch (error) {
        logger.error(`Error fetching ${index}:`, error);
        errors.push({ index, error: error.message });
      }
    });

    await Promise.all(quotePromises);
    
    res.json({
      success: true,
      message: 'Market indices retrieved successfully',
      data: {
        indices: quotes,
        errors,
        total: indices.length,
        successful: Object.keys(quotes).length,
        failed: errors.length
      },
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    logger.error('Error fetching market indices:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch market indices',
      message: error.message
    });
  }
});

module.exports = router; 