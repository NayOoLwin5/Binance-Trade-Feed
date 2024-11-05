# Crypto Trading Data Service

A FastAPI-based service that provides real-time cryptocurrency trading data from Binance via WebSocket connections.

## Features

- Real-time trade data streaming from Binance
- WebSocket connections for multiple trading pairs
- Configurable trading pair subscriptions
- Automatic cleanup of stale trade data
- REST API endpoints for trade data access

## Setup

- Clone the repository

- Create a `.env` file similar to `.env.sample`:
```
cp .env.sample .env
```

- Build the Docker image:
```
docker build -t binance-trade-feed .
```

- Run the Docker container:
```
docker run -p 3333:3333 binance-trade-feed
```
