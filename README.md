# Stock Market Data Pipeline and Trading System

This repository contains an application that uses Apache Airflow to orchestrate a data pipeline process for storing stock market data from the Alpaca Stock Market History API. The application handles both daily and monthly data frequencies and also includes a DAG that trades [Frog in the Pan](https://www3.nd.edu/~zda/Frog.pdf) Portfolios.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the Application](#running-the-application)
- [Usage](#usage)
  - [Data Pipeline](#data-pipeline)
  - [Trading DAG](#trading-dag)

## Features

- **Data Pipeline**: Orchestrates data extraction from the Alpaca API and stores it in a PostgreSQL database.
- **Trading System**: Generates and trades "Frog in the Pan" portfolios.
- **Dockerized Deployment**: Uses Docker and Docker Compose for containerized deployment of the entire system.
- **Apache Airflow**: Manages DAGs for data extraction and trading operations.
- **PostgreSQL**: Stores extracted stock market data.

## Architecture

The application consists of the following components:

- **Apache Airflow**: Manages and schedules DAGs for data extraction and trading.
- **PostgreSQL**: Stores stock market data retrieved from the Alpaca API.
- **Docker**: Containerizes the application components.
- **Docker Compose**: Manages multi-container Docker applications.

## Getting Started

### Prerequisites

- Docker
- Docker Compose
- Git

### Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/andrewhall1124/quant_workflow.git
    cd quant_workflow
    ```

2. **Build and run the Docker containers**:
    ```bash
    docker-compose up
    ```

### Configuration

1. **Environment Variables**:
   - Create a `.env` file in the root directory and configure the following environment variables:
     ```env
     AIRFLOW_UID=50000
     ALPACA_API_KEY=your_alpaca_api_key
     ALPACA_SECRET_KEY=your_alpaca_secret_key
     ```

2. **Airflow Variables**:
   - Set the necessary Airflow variables and connections for the Alpaca API and PostgreSQL.

### Running the Application

1. **Start the Docker containers**:
    ```bash
    docker-compose up
    ```

2. **Access the Airflow UI**:
   - Open your web browser and go to `http://localhost:8080` to access the Airflow UI.
   - Use the default Airflow credentials (`airflow`/`airflow`).

## Usage

### Data Pipeline

1. **Daily Data Extraction DAG**:
   - The DAG `alpaca_stock_daily.py` extracts daily stock market data from the Alpaca API and stores it in the PostgreSQL database.

2. **Monthly Data Extraction DAG**:
   - The DAG `alpaca_stock_history.py` extracts monthly stock market data from the Alpaca API and stores it in the PostgreSQL database.

### Trading DAG

1. **Portfolio Trading DAG**:
   - The DAG `fip_trading_monthly.py` generates portfolios based on information discreteness and momentum.
   - Trades the portfolios on a monthly basis using the stored Alpaca data.

