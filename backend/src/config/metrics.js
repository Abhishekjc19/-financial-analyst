const promClient = require('prom-client');

// Create a Registry to register the metrics
const register = new promClient.Registry();

// Add default metrics (CPU, memory, etc.)
promClient.collectDefaultMetrics({ register });

// Custom metrics
const httpRequestDurationMicroseconds = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.1, 0.5, 1, 2, 5]
});

const httpRequestsTotal = new promClient.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status_code']
});

const activeConnections = new promClient.Gauge({
  name: 'active_connections',
  help: 'Number of active connections'
});

const marketDataRequests = new promClient.Counter({
  name: 'market_data_requests_total',
  help: 'Total number of market data requests',
  labelNames: ['symbol', 'endpoint']
});

const analysisRequests = new promClient.Counter({
  name: 'analysis_requests_total',
  help: 'Total number of analysis requests',
  labelNames: ['type', 'symbol']
});

const predictionRequests = new promClient.Counter({
  name: 'prediction_requests_total',
  help: 'Total number of prediction requests',
  labelNames: ['model', 'symbol']
});

// Register all metrics
register.registerMetric(httpRequestDurationMicroseconds);
register.registerMetric(httpRequestsTotal);
register.registerMetric(activeConnections);
register.registerMetric(marketDataRequests);
register.registerMetric(analysisRequests);
register.registerMetric(predictionRequests);

function setupMetrics(app) {
  // Metrics endpoint
  app.get('/metrics', async (req, res) => {
    try {
      res.set('Content-Type', register.contentType);
      res.end(await register.metrics());
    } catch (error) {
      res.status(500).end(error);
    }
  });

  // Middleware to collect metrics
  app.use((req, res, next) => {
    const start = Date.now();
    
    res.on('finish', () => {
      const duration = Date.now() - start;
      const route = req.route ? req.route.path : req.path;
      
      httpRequestDurationMicroseconds
        .labels(req.method, route, res.statusCode)
        .observe(duration / 1000);
      
      httpRequestsTotal
        .labels(req.method, route, res.statusCode)
        .inc();
    });
    
    next();
  });
}

module.exports = {
  setupMetrics,
  register,
  httpRequestDurationMicroseconds,
  httpRequestsTotal,
  activeConnections,
  marketDataRequests,
  analysisRequests,
  predictionRequests
}; 