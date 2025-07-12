# Financial Analysis Platform - Backend System

## Architecture Overview

### System Components
- **API Gateway**: Express.js with JWT authentication
- **Market Data Service**: Real-time data ingestion from Yahoo Finance, Alpha Vantage
- **Technical Analysis Engine**: RSI, MACD, Bollinger Bands, Moving Averages
- **Prediction Service**: ML models for trend prediction
- **Database**: PostgreSQL with TimescaleDB for time-series data
- **Cache**: Redis for performance optimization
- **Message Queue**: Redis for async processing

### Technology Stack
- **Runtime**: Node.js 18+ / Python 3.11+
- **Framework**: Express.js / FastAPI
- **Database**: PostgreSQL 15+ with TimescaleDB
- **Cache**: Redis 7+
- **Authentication**: JWT with refresh tokens
- **Containerization**: Docker & Docker Compose
- **API Documentation**: Swagger/OpenAPI

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for development)
- Python 3.11+ (for ML services)

### Installation
```bash
# Clone and setup
git clone <repository>
cd backend

# Start all services
docker-compose up -d

# Install dependencies
npm install
pip install -r requirements.txt

# Run migrations
npm run migrate

# Start development server
npm run dev
```

### Environment Variables
Copy `.env.example` to `.env` and configure:
```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/financial_analyst
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET=your-secret-key
JWT_REFRESH_SECRET=your-refresh-secret

# API Keys
YAHOO_FINANCE_API_KEY=your-key
ALPHA_VANTAGE_API_KEY=your-key
FRED_API_KEY=your-key

# External Services
REDIS_HOST=localhost
REDIS_PORT=6379
```

## API Documentation

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh JWT token
- `POST /api/auth/logout` - User logout

### Market Data Endpoints
- `GET /api/market/overview` - Market overview
- `GET /api/market/stock/:symbol` - Stock data
- `GET /api/market/indices` - Major indices
- `GET /api/market/sectors` - Sector performance

### Analysis Endpoints
- `GET /api/analysis/:symbol` - Technical analysis
- `POST /api/analysis/batch` - Batch analysis
- `GET /api/analysis/indicators/:symbol` - Technical indicators

### Prediction Endpoints
- `GET /api/prediction/:symbol` - Stock predictions
- `POST /api/prediction/portfolio` - Portfolio predictions
- `GET /api/prediction/trends` - Market trends

### Portfolio Endpoints
- `GET /api/portfolio` - User portfolio
- `POST /api/portfolio/add` - Add position
- `PUT /api/portfolio/update` - Update position
- `DELETE /api/portfolio/remove` - Remove position

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Stocks Table
```sql
CREATE TABLE stocks (
    symbol VARCHAR(10) PRIMARY KEY,
    company_name VARCHAR(255),
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Stock Prices Table (TimescaleDB)
```sql
CREATE TABLE stock_prices (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    open DECIMAL(10,2),
    high DECIMAL(10,2),
    low DECIMAL(10,2),
    close DECIMAL(10,2),
    volume BIGINT,
    PRIMARY KEY (time, symbol)
);

-- Convert to hypertable
SELECT create_hypertable('stock_prices', 'time');
```

### Portfolios Table
```sql
CREATE TABLE portfolios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    symbol VARCHAR(10) REFERENCES stocks(symbol),
    shares DECIMAL(10,4) NOT NULL,
    avg_price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Analysis Results Table
```sql
CREATE TABLE analysis_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(10) REFERENCES stocks(symbol),
    analysis_type VARCHAR(50),
    data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Development

### Project Structure
```
backend/
├── src/
│   ├── api/           # API routes
│   ├── services/      # Business logic
│   ├── models/        # Data models
│   ├── middleware/    # Express middleware
│   ├── utils/         # Utilities
│   └── config/        # Configuration
├── tests/             # Test files
├── docs/              # Documentation
├── docker/            # Docker files
└── scripts/           # Build scripts
```

### Running Tests
```bash
npm test              # Run all tests
npm run test:watch    # Watch mode
npm run test:coverage # Coverage report
```

### Code Quality
```bash
npm run lint          # ESLint
npm run format        # Prettier
npm run type-check    # TypeScript check
```

## Deployment

### Docker Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables for Production
```env
NODE_ENV=production
DATABASE_URL=postgresql://user:pass@db:5432/financial_analyst
REDIS_URL=redis://redis:6379
JWT_SECRET=production-secret-key
```

## Monitoring & Logging

### Health Checks
- `GET /health` - Service health
- `GET /health/db` - Database health
- `GET /health/redis` - Redis health

### Metrics
- Prometheus metrics at `/metrics`
- Custom business metrics
- Performance monitoring

## Security

### Authentication
- JWT tokens with refresh mechanism
- Password hashing with bcrypt
- Rate limiting on auth endpoints
- CORS configuration

### Data Protection
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- HTTPS enforcement

## Performance Optimization

### Caching Strategy
- Redis for API responses
- Database query caching
- Static asset caching
- CDN integration

### Database Optimization
- TimescaleDB for time-series data
- Proper indexing strategy
- Query optimization
- Connection pooling

## Integration with Frontend

The backend is designed to work seamlessly with your React frontend at https://abhishekjc19.github.io/-financial-analyst/

### CORS Configuration
```javascript
app.use(cors({
  origin: ['https://abhishekjc19.github.io', 'http://localhost:3000'],
  credentials: true
}));
```

### API Response Format
```json
{
  "success": true,
  "data": {},
  "message": "Success",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Support

For issues and questions:
- Create GitHub issue
- Check documentation in `/docs`
- Review API examples in `/examples` 