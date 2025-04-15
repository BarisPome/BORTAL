# BIST Stock Market Portal

## Project Overview
BIST Stock Market Portal is a comprehensive web application for tracking, analyzing, and visualizing stock market data for Borsa Istanbul (BIST). The project serves dual purposes: providing a practical tool for tracking investments in the Turkish stock market and serving as a platform to develop and showcase technical skills in web development, data analysis, and potentially machine learning.

## Motivation
As a computer science student with a strong interest in finance and active investments in BIST, this project provides:
- A personalized portal to track stocks and market indices
- A platform to apply programming and data analysis skills to real-world financial data
- An evolving codebase that can incorporate new features and technologies

## Technology Stack

### Backend
- **Framework**: Django (Python)
- **Database**: PostgreSQL
- **API**: Django REST Framework
- **Data Processing**: Pandas, NumPy
- **Financial Data**: Yahoo Finance API

### Frontend
- **Framework**: React.js
- **Build Tool**: Vite
- **State Management**: React Hooks
- **Routing**: React Router
- **UI Components**: Custom-built components
- **Styling**: CSS with modular architecture
- **Data Visualization**: Recharts

### DevOps & Infrastructure
- **Version Control**: Git
- **Containerization**: Docker (planned)
- **Deployment**: TBD

## Core Features

### Stock Market Data
- Display and track BIST indices (BIST100, BIST50, BIST30, sector indices)
- Stock listings with detailed information and price history
- Daily price updates and historical data
- Sector-based categorization and filtering

### Analysis Tools
- Technical indicators (RSI, MACD, Moving Averages, etc.)
- Price charts with customizable timeframes
- Fundamental analysis data (P/E ratio, EPS, dividend yield)
- Comparative analysis between stocks

### User Features
- Watchlists for tracking favorite stocks
- Portfolio management for tracking investments
- Transaction history and performance tracking
- Custom alerts for price movements and events
- User activity tracking for personalized experiences

### News & Information
- Financial news related to stocks
- Market overview and sector performance
- Recent market activities
- Top performers and market movers

### Future Enhancements (Planned)
- Machine Learning predictions for stock price movements
- Advanced screening tools for stock discovery
- Backtesting of trading strategies
- Mobile application

## Database Schema
The project uses a comprehensive PostgreSQL database with models for:
- Stock and index data (prices, relationships)
- Fundamental financial information
- Technical indicators
- User data (profiles, watchlists, portfolios)
- News and events
- Transaction history
- ML predictions and alerts

## Project Structure
- Modular architecture for both backend and frontend
- Separation of concerns with dedicated components for UI, data fetching, and business logic
- Scalable folder structure for future enhancement

## Current Status
The project is in active development with core functionality being implemented incrementally. The backend database schema and API endpoints are being established first, followed by the frontend UI components and data visualization features.

## Project Goals
- Create a professional-grade financial portal for BIST stocks
- Implement best practices in web development
- Build a scalable architecture that can grow with new features
- Apply data analysis and machine learning techniques to financial data
- Develop skills in full-stack development through practical application
