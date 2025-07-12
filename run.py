#!/usr/bin/env python3
"""
Financial Analyst - Startup Script
Run this script to start the Financial Analyst application
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'flask', 'pandas', 'numpy', 'yfinance', 'plotly', 
        'scikit-learn', 'ta', 'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing required packages: {', '.join(missing_packages)}")
        logger.error("Please install them using: pip install -r requirements.txt")
        return False
    
    return True

def create_directories():
    """Create necessary directories"""
    directories = ['logs', 'data', 'models/saved']
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")

def main():
    """Main startup function"""
    logger.info("Starting Financial Analyst Application...")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create necessary directories
    create_directories()
    
    # Check if .env file exists
    env_file = Path('.env')
    if not env_file.exists():
        logger.warning("No .env file found. Creating from example...")
        if Path('env_example.txt').exists():
            import shutil
            shutil.copy('env_example.txt', '.env')
            logger.info("Created .env file from example. Please edit it with your API keys.")
        else:
            logger.warning("No env_example.txt found. Please create a .env file manually.")
    
    try:
        # Import and run the Flask app
        from app import app
        
        logger.info("Financial Analyst Application started successfully!")
        logger.info("Access the dashboard at: http://localhost:5000")
        logger.info("Press Ctrl+C to stop the application")
        
        # Run the Flask app
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True
        )
        
    except ImportError as e:
        logger.error(f"Failed to import application: {e}")
        logger.error("Please ensure all dependencies are installed correctly")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 