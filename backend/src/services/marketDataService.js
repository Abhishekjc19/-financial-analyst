const yahooFinance = require('yahoo-finance2');
const axios = require('axios');
const { logger } = require('../utils/logger');
const { executeQuery } = require('../config/database');
const { setMarketData, getMarketData } = require('../config/redis');

class MarketDataService {
  constructor() {
    this.cacheTTL = 300; // 5 minutes for market data
    this.alphaVantageKey = process.env.ALPHA_VANTAGE_API_KEY;
    this.fredApiKey = process.env.FRED_API_KEY;
  }

  // Helper method to convert period to days
  getPeriodInDays(period) {
    const periodMap = {
      '1d': 1,
      '5d': 5,
      '1mo': 30,
      '3mo': 90,
      '6mo': 180,
      '1y': 365,
      '2y': 730,
      '5y': 1825,
      '10y': 3650,
      'ytd': 365,
      'max': 3650
    };
    return periodMap[period] || 365;
  }

  // Get stock data from Yahoo Finance
  async getStockData(symbol, period = '1y', interval = '1d') {
    try {
      // Check cache first
      const cacheKey = `stock_data:${symbol}:${period}:${interval}`;
      const cachedData = await getMarketData(cacheKey);
      
      if (cachedData) {
        logger.debug(`Cache hit for stock data: ${symbol}`);
        return cachedData;
      }

      logger.info(`Fetching stock data for ${symbol} from Yahoo Finance`);
      
      const data = await yahooFinance.historical(symbol, {
        period1: new Date(Date.now() - this.getPeriodInDays(period) * 24 * 60 * 60 * 1000),
        period2: new Date(),
        interval: interval
      });

      if (!data || data.length === 0) {
        throw new Error(`No data found for symbol: ${symbol}`);
      }

      // Transform data to our format
      const transformedData = data.map(row => ({
        time: row.Date,
        open: parseFloat(row.Open),
        high: parseFloat(row.High),
        low: parseFloat(row.Low),
        close: parseFloat(row.Close),
        volume: parseInt(row.Volume)
      }));

      // Store in cache
      await setMarketData(cacheKey, transformedData, this.cacheTTL);

      // Store in database for historical analysis
      await this.storeStockData(symbol, transformedData);

      return transformedData;
    } catch (error) {
      logger.error(`Error fetching stock data for ${symbol}:`, error);
      throw new Error(`Failed to fetch stock data for ${symbol}: ${error.message}`);
    }
  }

  // Get real-time stock quote
  async getStockQuote(symbol) {
    try {
      const cacheKey = `quote:${symbol}`;
      const cachedQuote = await getMarketData(cacheKey);
      
      if (cachedQuote) {
        return cachedQuote;
      }

      logger.info(`Fetching real-time quote for ${symbol}`);
      
      const quote = await yahooFinance.quote(symbol);

      if (!quote) {
        throw new Error(`No quote found for symbol: ${symbol}`);
      }

      const quoteData = {
        symbol: quote.symbol,
        price: quote.regularMarketPrice,
        change: quote.regularMarketChange,
        changePercent: quote.regularMarketChangePercent,
        volume: quote.regularMarketVolume,
        marketCap: quote.marketCap,
        high: quote.regularMarketDayHigh,
        low: quote.regularMarketDayLow,
        open: quote.regularMarketOpen,
        previousClose: quote.regularMarketPreviousClose,
        timestamp: new Date().toISOString()
      };

      // Cache for 1 minute for real-time data
      await setMarketData(cacheKey, quoteData, 60);

      return quoteData;
    } catch (error) {
      logger.error(`Error fetching quote for ${symbol}:`, error);
      throw new Error(`Failed to fetch quote for ${symbol}: ${error.message}`);
    }
  }

  // Get market overview (major indices)
  async getMarketOverview() {
    try {
      const cacheKey = 'market_overview';
      const cachedOverview = await getMarketData(cacheKey);
      
      if (cachedOverview) {
        return cachedOverview;
      }

      const indices = ['^GSPC', '^DJI', '^IXIC', '^VIX']; // S&P 500, Dow, NASDAQ, VIX
      const overview = {};

      for (const index of indices) {
        try {
          const quote = await this.getStockQuote(index);
          overview[index] = quote;
        } catch (error) {
          logger.error(`Error fetching ${index}:`, error);
          overview[index] = { error: error.message };
        }
      }

      // Cache for 2 minutes
      await setMarketData(cacheKey, overview, 120);

      return overview;
    } catch (error) {
      logger.error('Error fetching market overview:', error);
      throw new Error(`Failed to fetch market overview: ${error.message}`);
    }
  }

  // Get sector performance
  async getSectorPerformance() {
    try {
      const cacheKey = 'sector_performance';
      const cachedSectors = await getMarketData(cacheKey);
      
      if (cachedSectors) {
        return cachedSectors;
      }

      const sectorETFs = {
        'XLK': 'Technology',
        'XLF': 'Financials',
        'XLE': 'Energy',
        'XLV': 'Healthcare',
        'XLI': 'Industrials',
        'XLP': 'Consumer Staples',
        'XLY': 'Consumer Discretionary',
        'XLU': 'Utilities',
        'XLB': 'Materials',
        'XLRE': 'Real Estate'
      };

      const sectors = {};

      for (const [etf, sectorName] of Object.entries(sectorETFs)) {
        try {
          const quote = await this.getStockQuote(etf);
          sectors[sectorName] = {
            etf: etf,
            name: sectorName,
            price: quote.price,
            change: quote.change,
            changePercent: quote.changePercent
          };
        } catch (error) {
          logger.error(`Error fetching ${etf}:`, error);
          sectors[sectorName] = { error: error.message };
        }
      }

      // Cache for 5 minutes
      await setMarketData(cacheKey, sectors, 300);

      return sectors;
    } catch (error) {
      logger.error('Error fetching sector performance:', error);
      throw new Error(`Failed to fetch sector performance: ${error.message}`);
    }
  }

  // Search for stocks
  async searchStocks(query) {
    try {
      if (!query || query.length < 2) {
        return [];
      }

      const cacheKey = `search:${query.toLowerCase()}`;
      const cachedResults = await getMarketData(cacheKey);
      
      if (cachedResults) {
        return cachedResults;
      }

      logger.info(`Searching stocks for query: ${query}`);
      
      // Use Yahoo Finance search
      const searchResults = await yahooFinance.search(query, { quotesCount: 10 });
      
      const results = searchResults.quotes.map(quote => ({
        symbol: quote.symbol,
        name: quote.shortname || quote.longname,
        exchange: quote.exchange,
        type: quote.quoteType
      }));

      // Cache for 1 hour
      await setMarketData(cacheKey, results, 3600);

      return results;
    } catch (error) {
      logger.error(`Error searching stocks for ${query}:`, error);
      return [];
    }
  }

  // Get company information
  async getCompanyInfo(symbol) {
    try {
      const cacheKey = `company_info:${symbol}`;
      const cachedInfo = await getMarketData(cacheKey);
      
      if (cachedInfo) {
        return cachedInfo;
      }

      logger.info(`Fetching company info for ${symbol}`);
      
      const ticker = yahooFinance.Ticker(symbol);
      const info = await ticker.info;

      if (!info) {
        throw new Error(`No company info found for symbol: ${symbol}`);
      }

      const companyInfo = {
        symbol: info.symbol,
        name: info.longName || info.shortName,
        sector: info.sector,
        industry: info.industry,
        marketCap: info.marketCap,
        employees: info.fullTimeEmployees,
        website: info.website,
        description: info.longBusinessSummary,
        country: info.country,
        currency: info.currency,
        exchange: info.exchange,
        timestamp: new Date().toISOString()
      };

      // Cache for 1 hour
      await setMarketData(cacheKey, companyInfo, 3600);

      return companyInfo;
    } catch (error) {
      logger.error(`Error fetching company info for ${symbol}:`, error);
      throw new Error(`Failed to fetch company info for ${symbol}: ${error.message}`);
    }
  }

  // Store stock data in database
  async storeStockData(symbol, data) {
    try {
      const client = await require('../config/database').getPool().connect();
      
      try {
        await client.query('BEGIN');

        // Insert or update stock info
        const stockQuery = `
          INSERT INTO stocks (symbol, company_name, sector, industry, market_cap, updated_at)
          VALUES ($1, $2, $3, $4, $5, NOW())
          ON CONFLICT (symbol) 
          DO UPDATE SET 
            company_name = EXCLUDED.company_name,
            sector = EXCLUDED.sector,
            industry = EXCLUDED.industry,
            market_cap = EXCLUDED.market_cap,
            updated_at = NOW()
        `;

        // Get company info for the stock
        const companyInfo = await this.getCompanyInfo(symbol);
        
        await client.query(stockQuery, [
          symbol,
          companyInfo.name,
          companyInfo.sector,
          companyInfo.industry,
          companyInfo.marketCap
        ]);

        // Insert price data
        const priceQuery = `
          INSERT INTO stock_prices (time, symbol, open, high, low, close, volume)
          VALUES ($1, $2, $3, $4, $5, $6, $7)
          ON CONFLICT (time, symbol) 
          DO UPDATE SET 
            open = EXCLUDED.open,
            high = EXCLUDED.high,
            low = EXCLUDED.low,
            close = EXCLUDED.close,
            volume = EXCLUDED.volume
        `;

        for (const row of data) {
          await client.query(priceQuery, [
            row.time,
            symbol,
            row.open,
            row.high,
            row.low,
            row.close,
            row.volume
          ]);
        }

        await client.query('COMMIT');
        logger.debug(`Stored ${data.length} data points for ${symbol}`);
      } catch (error) {
        await client.query('ROLLBACK');
        throw error;
      } finally {
        client.release();
      }
    } catch (error) {
      logger.error(`Error storing stock data for ${symbol}:`, error);
      // Don't throw error as this is not critical for the main flow
    }
  }

  // Get historical data from database
  async getHistoricalData(symbol, startDate, endDate) {
    try {
      const query = `
        SELECT time, open, high, low, close, volume
        FROM stock_prices
        WHERE symbol = $1 AND time BETWEEN $2 AND $3
        ORDER BY time ASC
      `;
      
      const result = await executeQuery(query, [symbol, startDate, endDate]);
      return result.rows;
    } catch (error) {
      logger.error(`Error fetching historical data for ${symbol}:`, error);
      throw new Error(`Failed to fetch historical data: ${error.message}`);
    }
  }

  // Get macroeconomic indicators
  async getMacroIndicators() {
    try {
      const cacheKey = 'macro_indicators';
      const cachedIndicators = await getMarketData(cacheKey);
      
      if (cachedIndicators) {
        return cachedIndicators;
      }

      const indicators = {};

      // Get VIX (Fear Index)
      try {
        const vixQuote = await this.getStockQuote('^VIX');
        indicators.vix = {
          value: vixQuote.price,
          change: vixQuote.change,
          changePercent: vixQuote.changePercent,
          interpretation: this.interpretVIX(vixQuote.price)
        };
      } catch (error) {
        logger.error('Error fetching VIX:', error);
      }

      // Get Treasury yields (if Alpha Vantage key is available)
      if (this.alphaVantageKey) {
        try {
          const treasuryData = await this.getTreasuryYields();
          indicators.treasury = treasuryData;
        } catch (error) {
          logger.error('Error fetching treasury yields:', error);
        }
      }

      // Cache for 15 minutes
      await setMarketData(cacheKey, indicators, 900);

      return indicators;
    } catch (error) {
      logger.error('Error fetching macro indicators:', error);
      throw new Error(`Failed to fetch macro indicators: ${error.message}`);
    }
  }

  // Get Treasury yields from Alpha Vantage
  async getTreasuryYields() {
    try {
      const response = await axios.get(
        `https://www.alphavantage.co/query?function=TREASURY_YIELD&interval=daily&maturity=10year&apikey=${this.alphaVantageKey}`
      );

      if (response.data['Error Message']) {
        throw new Error(response.data['Error Message']);
      }

      const data = response.data['data'];
      if (!data || data.length === 0) {
        throw new Error('No treasury yield data available');
      }

      const latest = data[0];
      return {
        '10Y': parseFloat(latest.value),
        date: latest.timestamp,
        trend: this.getYieldTrend(data.slice(0, 5))
      };
    } catch (error) {
      logger.error('Error fetching treasury yields:', error);
      throw error;
    }
  }

  // Interpret VIX levels
  interpretVIX(vixLevel) {
    if (vixLevel < 15) return 'Low volatility - Complacent market';
    if (vixLevel < 20) return 'Normal volatility';
    if (vixLevel < 30) return 'Elevated volatility - Caution advised';
    if (vixLevel < 40) return 'High volatility - Fear in market';
    return 'Extreme volatility - Panic in market';
  }

  // Get yield trend
  getYieldTrend(data) {
    if (data.length < 2) return 'stable';
    
    const values = data.map(d => parseFloat(d.value));
    const first = values[values.length - 1];
    const last = values[0];
    
    const change = last - first;
    if (change > 0.1) return 'rising';
    if (change < -0.1) return 'falling';
    return 'stable';
  }
}

module.exports = new MarketDataService(); 