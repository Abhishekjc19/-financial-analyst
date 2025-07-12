# Financial Analyst Backend - Setup Guide

## 🚀 Quick Start

### Prerequisites
- **Docker & Docker Compose** (for containerized deployment)
- **Node.js 18+** (for development)
- **Git** (for version control)

### 1. Initial Setup

```bash
# Clone the repository (if not already done)
git clone https://github.com/Abhishekjc19/-financial-analyst.git
cd backend

# Run the setup script
node scripts/setup.js

# Install dependencies
npm install
```

### 2. Environment Configuration

```bash
# Copy environment template
cp env.example .env

# Edit .env with your configuration
nano .env
```

**Required API Keys:**
- `ALPHA_VANTAGE_API_KEY` - Get from [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
- `FRED_API_KEY` - Get from [FRED](https://fred.stlouisfed.org/docs/api/api_key.html)

### 3. Start Services

```bash
# Start all services with Docker
docker-compose up -d

# Check service status
docker-compose ps
```

### 4. Initialize Database

```bash
# Run database migrations
npm run migrate

# (Optional) Seed with sample data
npm run seed
```

### 5. Start Development Server

```bash
# Start the API server
npm run dev
```

## 🌐 Access Points

- **API Server**: http://localhost:3000
- **API Documentation**: http://localhost:3000/api-docs
- **Health Check**: http://localhost:3000/health
- **Metrics**: http://localhost:3000/metrics

## 📊 API Endpoints

### Authentication
```bash
# Register user
POST /api/auth/register
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "firstName": "John",
  "lastName": "Doe"
}

# Login
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

# Refresh token
POST /api/auth/refresh
{
  "refreshToken": "your-refresh-token"
}
```

### Market Data
```bash
# Get market overview
GET /api/market/overview

# Get stock data
GET /api/market/stock/AAPL?period=1y&interval=1d

# Get real-time quote
GET /api/market/quote/AAPL

# Search stocks
GET /api/market/search?q=apple

# Get sector performance
GET /api/market/sectors
```

### Analysis (Coming Soon)
```bash
# Get technical analysis
GET /api/analysis/AAPL

# Get predictions
GET /api/prediction/AAPL?timeframe=30d
```

### Portfolio (Requires Authentication)
```bash
# Get user portfolio
GET /api/portfolio
Authorization: Bearer <your-jwt-token>

# Add position
POST /api/portfolio/add
Authorization: Bearer <your-jwt-token>
{
  "symbol": "AAPL",
  "shares": 10,
  "avgPrice": 150.00
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NODE_ENV` | Environment mode | `development` |
| `PORT` | API server port | `3000` |
| `DATABASE_URL` | PostgreSQL connection string | Auto-generated |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `JWT_SECRET` | JWT signing secret | Required |
| `ALPHA_VANTAGE_API_KEY` | Alpha Vantage API key | Required |
| `FRED_API_KEY` | FRED API key | Optional |

### Docker Services

| Service | Port | Description |
|---------|------|-------------|
| `api` | 3000 | Main API server |
| `postgres` | 5432 | PostgreSQL with TimescaleDB |
| `redis` | 6379 | Redis cache |
| `ml_service` | 8000 | Python ML service |
| `nginx` | 80, 443 | Reverse proxy |

## 🗄️ Database Schema

### Core Tables
- **users** - User accounts and authentication
- **stocks** - Stock information and metadata
- **stock_prices** - Time-series price data (TimescaleDB hypertable)
- **portfolios** - User portfolio positions
- **analysis_results** - Cached analysis results
- **refresh_tokens** - JWT refresh tokens

### TimescaleDB Features
- Automatic time-series partitioning
- Efficient time-range queries
- Continuous aggregates (coming soon)
- Data retention policies

## 🔒 Security Features

### Authentication
- JWT tokens with refresh mechanism
- Password hashing with bcrypt
- Session management with Redis
- Rate limiting on auth endpoints

### Data Protection
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CORS configuration for frontend

### Rate Limiting
- General API: 100 requests per 15 minutes
- Auth endpoints: 5 requests per 15 minutes
- Custom limits per endpoint

## 📈 Performance Optimization

### Caching Strategy
- **Redis** for API responses
- **Database query** caching
- **Market data** caching (5 minutes)
- **Analysis results** caching (30 minutes)

### Database Optimization
- **TimescaleDB** for time-series data
- **Proper indexing** strategy
- **Connection pooling**
- **Query optimization**

## 🔍 Monitoring & Logging

### Health Checks
```bash
# Overall health
GET /health

# Database health
GET /health/db

# Redis health
GET /health/redis
```

### Metrics
- **Prometheus** metrics at `/metrics`
- **Custom business** metrics
- **Performance** monitoring
- **Request/response** logging

### Log Files
- `logs/combined.log` - All logs
- `logs/error.log` - Error logs only
- `logs/api.log` - API request logs
- `logs/database.log` - Database operations
- `logs/market.log` - Market data operations

## 🚀 Deployment

### Development
```bash
npm run dev
```

### Production with Docker
```bash
# Build and start production services
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f api
```

### Production Environment Variables
```env
NODE_ENV=production
LOG_LEVEL=warn
DEBUG=false
JWT_SECRET=your-production-secret
DATABASE_URL=postgresql://user:pass@db:5432/financial_analyst
REDIS_URL=redis://redis:6379
```

## 🔗 Frontend Integration

The backend is designed to work seamlessly with your React frontend at https://abhishekjc19.github.io/-financial-analyst/

### CORS Configuration
```javascript
// Already configured for your domain
CORS_ORIGIN=https://abhishekjc19.github.io,http://localhost:3000
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

## 🛠️ Development

### Available Scripts
```bash
npm start          # Start production server
npm run dev        # Start development server
npm test           # Run tests
npm run test:watch # Run tests in watch mode
npm run lint       # Run ESLint
npm run format     # Format code with Prettier
npm run migrate    # Run database migrations
npm run seed       # Seed database with sample data
```

### Project Structure
```
backend/
├── src/
│   ├── api/routes/     # API endpoints
│   ├── config/         # Configuration files
│   ├── middleware/     # Express middleware
│   ├── services/       # Business logic
│   ├── utils/          # Utilities
│   └── server.js       # Main server file
├── scripts/            # Setup and utility scripts
├── database/           # Database initialization
├── nginx/              # Nginx configuration
├── logs/               # Log files
└── docker-compose.yml  # Docker services
```

## 🐛 Troubleshooting

### Common Issues

**1. Database Connection Failed**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres
```

**2. Redis Connection Failed**
```bash
# Check if Redis is running
docker-compose ps redis

# Check logs
docker-compose logs redis
```

**3. API Not Responding**
```bash
# Check API service
docker-compose ps api

# Check logs
docker-compose logs api

# Test health endpoint
curl http://localhost:3000/health
```

**4. CORS Issues**
- Verify CORS_ORIGIN in .env
- Check browser console for CORS errors
- Ensure frontend URL is in allowed origins

### Log Analysis
```bash
# View real-time logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f api

# Search logs for errors
docker-compose logs | grep ERROR
```

## 📞 Support

For issues and questions:
- Create GitHub issue
- Check documentation in `/docs`
- Review API examples in `/examples`
- Check logs in `/logs` directory

## 🔄 Updates

To update the system:
```bash
# Pull latest changes
git pull origin main

# Rebuild containers
docker-compose down
docker-compose up -d --build

# Run migrations if needed
npm run migrate
```

---

**Happy Trading! 📈**

Your Financial Analyst backend is now ready to power your trading decisions with real-time market data, technical analysis, and AI-powered predictions. 