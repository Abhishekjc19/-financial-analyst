const { Pool } = require('pg');
const { logger } = require('../utils/logger');

let pool = null;

const createPool = () => {
  const config = {
    host: process.env.DB_HOST || 'localhost',
    port: process.env.DB_PORT || 5432,
    database: process.env.DB_NAME || 'financial_analyst',
    user: process.env.DB_USER || 'financial_user',
    password: process.env.DB_PASSWORD || 'financial_password',
    max: 20, // Maximum number of clients in the pool
    idleTimeoutMillis: 30000, // Close idle clients after 30 seconds
    connectionTimeoutMillis: 2000, // Return an error after 2 seconds if connection could not be established
    ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
  };

  return new Pool(config);
};

const connectDatabase = async () => {
  try {
    pool = createPool();
    
    // Test the connection
    const client = await pool.connect();
    await client.query('SELECT NOW()');
    client.release();
    
    logger.info('Database connection established successfully');
    
    // Set up event listeners
    pool.on('error', (err) => {
      logger.error('Unexpected error on idle client', err);
    });
    
    pool.on('connect', (client) => {
      logger.debug('New client connected to database');
    });
    
    return pool;
  } catch (error) {
    logger.error('Database connection failed:', error);
    throw error;
  }
};

const getPool = () => {
  if (!pool) {
    throw new Error('Database not connected. Call connectDatabase() first.');
  }
  return pool;
};

const closeDatabase = async () => {
  if (pool) {
    await pool.end();
    logger.info('Database connection closed');
  }
};

// Database initialization functions
const initializeTables = async () => {
  const client = await getPool().connect();
  
  try {
    // Enable TimescaleDB extension
    await client.query('CREATE EXTENSION IF NOT EXISTS timescaledb;');
    
    // Create users table
    await client.query(`
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
    `);
    
    // Create stocks table
    await client.query(`
      CREATE TABLE IF NOT EXISTS stocks (
        symbol VARCHAR(10) PRIMARY KEY,
        company_name VARCHAR(255),
        sector VARCHAR(100),
        industry VARCHAR(100),
        market_cap BIGINT,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
      );
    `);
    
    // Create stock_prices table with TimescaleDB
    await client.query(`
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
    `);
    
    // Convert to hypertable if not already done
    const hypertableResult = await client.query(`
      SELECT create_hypertable('stock_prices', 'time', if_not_exists => TRUE);
    `);
    
    // Create portfolios table
    await client.query(`
      CREATE TABLE IF NOT EXISTS portfolios (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES users(id) ON DELETE CASCADE,
        symbol VARCHAR(10) REFERENCES stocks(symbol),
        shares DECIMAL(10,4) NOT NULL,
        avg_price DECIMAL(10,2) NOT NULL,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
      );
    `);
    
    // Create analysis_results table
    await client.query(`
      CREATE TABLE IF NOT EXISTS analysis_results (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        symbol VARCHAR(10) REFERENCES stocks(symbol),
        analysis_type VARCHAR(50),
        data JSONB,
        created_at TIMESTAMP DEFAULT NOW()
      );
    `);
    
    // Create refresh_tokens table
    await client.query(`
      CREATE TABLE IF NOT EXISTS refresh_tokens (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES users(id) ON DELETE CASCADE,
        token VARCHAR(255) UNIQUE NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT NOW()
      );
    `);
    
    // Create indexes for better performance
    await client.query(`
      CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol ON stock_prices (symbol);
      CREATE INDEX IF NOT EXISTS idx_stock_prices_time ON stock_prices (time DESC);
      CREATE INDEX IF NOT EXISTS idx_portfolios_user_id ON portfolios (user_id);
      CREATE INDEX IF NOT EXISTS idx_analysis_results_symbol ON analysis_results (symbol);
      CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens (user_id);
      CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token ON refresh_tokens (token);
    `);
    
    logger.info('Database tables initialized successfully');
  } catch (error) {
    logger.error('Error initializing database tables:', error);
    throw error;
  } finally {
    client.release();
  }
};

// Helper functions for common database operations
const executeQuery = async (query, params = []) => {
  const client = await getPool().connect();
  try {
    const result = await client.query(query, params);
    return result;
  } finally {
    client.release();
  }
};

const executeTransaction = async (queries) => {
  const client = await getPool().connect();
  try {
    await client.query('BEGIN');
    
    const results = [];
    for (const { query, params } of queries) {
      const result = await client.query(query, params || []);
      results.push(result);
    }
    
    await client.query('COMMIT');
    return results;
  } catch (error) {
    await client.query('ROLLBACK');
    throw error;
  } finally {
    client.release();
  }
};

module.exports = {
  connectDatabase,
  getPool,
  closeDatabase,
  initializeTables,
  executeQuery,
  executeTransaction
}; 