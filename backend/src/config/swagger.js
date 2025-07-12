const swaggerJsdoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');

const options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'Financial Analyst API',
      version: '1.0.0',
      description: 'Advanced financial analysis platform with real-time market data, technical analysis, and ML predictions',
      contact: {
        name: 'Financial Analyst Team',
        url: 'https://abhishekjc19.github.io/-financial-analyst/',
        email: 'support@financialanalyst.com'
      },
      license: {
        name: 'MIT',
        url: 'https://opensource.org/licenses/MIT'
      }
    },
    servers: [
      {
        url: 'http://localhost:3000',
        description: 'Development server'
      },
      {
        url: 'https://api.financialanalyst.com',
        description: 'Production server'
      }
    ],
    components: {
      securitySchemes: {
        bearerAuth: {
          type: 'http',
          scheme: 'bearer',
          bearerFormat: 'JWT'
        }
      },
      schemas: {
        User: {
          type: 'object',
          properties: {
            id: { type: 'string', format: 'uuid' },
            email: { type: 'string', format: 'email' },
            firstName: { type: 'string' },
            lastName: { type: 'string' },
            createdAt: { type: 'string', format: 'date-time' }
          }
        },
        StockData: {
          type: 'object',
          properties: {
            symbol: { type: 'string' },
            time: { type: 'string', format: 'date-time' },
            open: { type: 'number' },
            high: { type: 'number' },
            low: { type: 'number' },
            close: { type: 'number' },
            volume: { type: 'integer' }
          }
        },
        StockQuote: {
          type: 'object',
          properties: {
            symbol: { type: 'string' },
            price: { type: 'number' },
            change: { type: 'number' },
            changePercent: { type: 'number' },
            volume: { type: 'integer' },
            marketCap: { type: 'number' },
            high: { type: 'number' },
            low: { type: 'number' },
            open: { type: 'number' },
            previousClose: { type: 'number' },
            timestamp: { type: 'string', format: 'date-time' }
          }
        },
        AnalysisResult: {
          type: 'object',
          properties: {
            symbol: { type: 'string' },
            analysisType: { type: 'string' },
            data: { type: 'object' },
            timestamp: { type: 'string', format: 'date-time' }
          }
        },
        Portfolio: {
          type: 'object',
          properties: {
            id: { type: 'string', format: 'uuid' },
            userId: { type: 'string', format: 'uuid' },
            symbol: { type: 'string' },
            shares: { type: 'number' },
            avgPrice: { type: 'number' },
            createdAt: { type: 'string', format: 'date-time' }
          }
        },
        Error: {
          type: 'object',
          properties: {
            success: { type: 'boolean' },
            error: { type: 'string' },
            message: { type: 'string' },
            timestamp: { type: 'string', format: 'date-time' }
          }
        }
      }
    },
    security: [
      {
        bearerAuth: []
      }
    ]
  },
  apis: [
    './src/api/routes/*.js',
    './src/server.js'
  ]
};

const specs = swaggerJsdoc(options);

const setupSwagger = (app) => {
  app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(specs, {
    explorer: true,
    customCss: '.swagger-ui .topbar { display: none }',
    customSiteTitle: 'Financial Analyst API Documentation'
  }));

  // Serve swagger.json
  app.get('/api-docs.json', (req, res) => {
    res.setHeader('Content-Type', 'application/json');
    res.send(specs);
  });
};

module.exports = {
  setupSwagger,
  specs
}; 