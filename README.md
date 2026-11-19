# ApexMart: Enterprise Industrial E-Commerce Microservices Platform

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-cyan.svg)](https://react.dev/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)
[![RabbitMQ](https://img.shields.io/badge/RabbitMQ-AMQP-orange.svg)](https://www.rabbitmq.com/)
[![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-red.svg)](https://prometheus.io/)

A complete, production-grade, enterprise-scale e-commerce platform built to simulate real-world industrial systems (like Amazon and Flipkart). The application features 15 independent microservices, distributed transaction management via the Saga pattern, asynchronous event-driven messaging via RabbitMQ, W3C distributed tracing, Prometheus & Grafana observability, and a Chaos Engineering Fault Simulation Studio.

---

## 1. Architecture Overview

ApexMart adopts a modular microservices architecture with an API Gateway routing to 15 domain-driven services:

```
                                  +------------------------------------+
                                  |         React TypeScript UI        |
                                  |      (Port: 3000 / Modern SPA)     |
                                  +-----------------+------------------+
                                                    |
                                                    v
                                  +------------------------------------+
                                  |         Nginx / API Gateway        |
                                  |            (Port: 8000)            |
                                  +-----------------+------------------+
                                                    |
         +--------------------+---------------------+--------------------+--------------------+
         |                    |                     |                    |                    |
         v                    v                     v                    v                    v
  +--------------+     +--------------+      +--------------+     +--------------+     +--------------+
  | Auth Service |     | Catalog Serv |      | Search Serv  |     | Cart Service |     | Pricing Serv |
  | (Port: 8001) |     | (Port: 8002) |      | (Port: 8003) |     | (Port: 8005) |     | (Port: 8006) |
  +--------------+     +--------------+      +--------------+     +--------------+     +--------------+
         |                    |                     |                    |                    |
         v                    v                     v                    v                    v
  +--------------+     +--------------+      +--------------+     +--------------+     +--------------+
  |Inventory Serv|     | Checkout Serv|      | Payment Serv |     | Order Serv   |     | Shipping Serv|
  | (Port: 8004) |     | (Port: 8007) |      | (Port: 8008) |     | (Port: 8009) |     | (Port: 8010) |
  +--------------+     +--------------+      +--------------+     +--------------+     +--------------+
         |                    |                     |                    |                    |
         v                    v                     v                    v                    v
  +--------------+     +--------------+      +--------------+     +--------------+     +--------------+
  | Notif Serv   |     | Support Serv |      | Review Serv  |     | Analytics    |     | Admin Serv   |
  | (Port: 8011) |     | (Port: 8012) |      | (Port: 8013) |     | (Port: 8014) |     | (Port: 8015) |
  +--------------+     +--------------+      +--------------+     +--------------+     +--------------+
         |                    |                     |                    |                    |
         +--------------------+---------------------+--------------------+--------------------+
                                                    |
                                                    v
                                  +------------------------------------+
                                  |         RabbitMQ Event Broker      |
                                  |     (Exchange: ecommerce_events)   |
                                  +-----------------+------------------+
                                                    |
                                                    v
                                  +------------------------------------+
                                  |    Centralized Observability Hub   |
                                  |     (Endpoint: /api/telemetry/*)   |
                                  +------------------------------------+
```

---

## 2. The 15 Core Microservices

| Service | Port | Key Responsibilities |
| :--- | :---: | :--- |
| **User Authentication** | 8001 | Registration, login, bcrypt password hashing, JWT tokens, RBAC roles (`customer`, `admin`, `support_agent`), customer profile & saved addresses. |
| **Product Catalog** | 8002 | 112+ realistic products across 20 categories, ratings, specifications JSON, pricing, discount percentages, and complementary recommendations. |
| **Search Service** | 8003 | Full-text keyword search across titles and descriptions, multi-parameter filtering (category, price range), sorting, and real-time autocomplete suggestions. |
| **Inventory Service** | 8004 | Real-time stock counts, warehouse locations (`BLR-FC-01`, `BOM-FC-04`, `DEL-FC-02`), stock reservation with TTL, confirmation on payment, and low-stock alerts. |
| **Shopping Cart** | 8005 | User and guest session cart persistence, quantity adjustment, subtotal computation, and stock availability checks. |
| **Pricing & Promotions** | 8006 | Promotional coupons (`SAVE10`, `SUPER50`, `FREESHIP`, `FESTIVE25`, `FLAT500`), 18% GST tax breakdown, and free shipping logic (orders ≥ ₹499). |
| **Checkout Service** | 8007 | **Distributed Saga Orchestrator**: coordinates inventory reservation, order creation, payment execution, stock commit/release, and compensating transactions. |
| **Payment Service** | 8008 | Sandboxed payment gateway supporting Credit/Debit Cards, UPI (`john.doe@okaxis`), Net Banking, and COD. Supports idempotency keys and simulated gateway failures. |
| **Order Management** | 8009 | Generates `ORD-YYYYMMDD-XXXX` IDs, manages order lifecycle (`PLACED`, `CONFIRMED`, `PROCESSING`, `SHIPPED`, `DELIVERED`, `CANCELLED`), returns and refunds. |
| **Shipping & Delivery** | 8010 | Generates tracking IDs (`TRK-BLR-XXXXXX`), assigns carriers (*Amazon Logistics, BlueDart, Delhivery, FedEx, DHL*), and maintains timeline milestones. |
| **Notification Service** | 8011 | Dispatches asynchronous email & SMS alerts for order confirmation, payment status, shipping dispatches, and delivery confirmations. |
| **Customer Support** | 8012 | Generates `TCK-XXXX` support tickets, categories (Order Issue, Refund, Return, Technical), threaded chat messages between customer and support agents. |
| **Review & Rating** | 8013 | Customer product reviews, 1-5 star ratings, star distribution aggregations, helpful votes, and moderation flags. |
| **Analytics Service** | 8014 | Tracks total platform GMV, completed orders count, average order value, 7-day revenue trend charts, top-selling products, and payment success rate. |
| **Administration Service** | 8015 | Enterprise oversight dashboard, product CRUD, inventory stock adjustment, orders fulfillment status override, and user account management. |

---

## 3. Real-World Business Workflow & Distributed Saga

When a customer places an order, the system coordinates an 8-step Saga workflow:

```
[1. Validate Stock] ──> [2. Reserve Stock] ──> [3. Calculate Pricing] ──> [4. Create Order]
                                                                                │
   ┌─────────────────────── SUCCESS PATH ◄──────────────────────────────────────┴────────┐
   ▼                                                                                     ▼
[5. Process Payment: OK]                                                      [5. Process Payment: FAIL]
   │                                                                                     │
[6. Confirm Inventory Deduction]                                              [COMPENSATING ROLLBACK]
   │                                                                           • Release Stock
[7. Dispatch Shipment via Carrier]                                             • Mark Order CANCELLED
   │                                                                           • Publish payment.failed
[8. Send Confirmation & Clear Cart]                                            • Alert Customer
```

---

## 4. Observability & Telemetry

ApexMart provides enterprise-grade observability:
- **W3C Distributed Tracing**: Generates and propagates `traceparent`, `x-correlation-id`, and `x-transaction-id` headers across all service hops.
- **Structured JSON Logging**: Centralized into an in-memory high-throughput telemetry stream.
- **Prometheus Metrics**: Exposes metrics on `/metrics` (requests total, error count, p95 latency, system CPU & RAM).
- **Grafana Dashboard**: Pre-configured dashboards in `docker/grafana/provisioning/dashboards/`.
- **Live Telemetry Stream (`GET /api/telemetry/stream`)**: Real-time Server-Sent Events stream for autonomous live monitoring.
- **Microservices Health Matrix (`GET /api/telemetry/services-health`)**: Returns status, latency percentiles, error rates, and dependencies for all 15 services.

---

## 5. Chaos Engineering Studio (Fault Injection)

The built-in **Chaos Studio** enables testing 18 synthetic failure modes and 6 predefined industrial scenarios without damaging persistent data:

### Predefined Scenarios (1-Click Trigger):
1. **Scenario 1: Payment Gateway Timeout** (4.5s latency + bank decline, tests Saga compensation).
2. **Scenario 2: Inventory Service Degradation** (Gradual response slowdown up to 5s).
3. **Scenario 3: Product Database Outage** (Connection pool exhaustion, HTTP 500 on catalog/search).
4. **Scenario 4: RabbitMQ Broker Failure** (AMQP outage, downstream fulfillment delayed).
5. **Scenario 5: Shipping Partner Failure** (Carrier partner 503 error, orders stuck in processing).
6. **Scenario 6: Cascading Latency Spike** (Payment delay propagates to checkout timeout).

### Granular Sliders:
- Target service selector
- Failure mode (Timeout, Latency, HTTP 500, DB dropped, RabbitMQ down, Redis down, Process crash)
- Latency injection (0 to 8000 ms)
- Error rate probability (10% to 100%)
- Duration countdown (15s to 300s with auto-recovery)

---

## 6. Getting Started

### Option A: Quick Run (Local Mode - Zero Docker Dependencies)

1. **Install Python requirements**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Seed the database** (populates 112 products, 20 categories, reviews, coupons, demo accounts):
   ```bash
   python scripts/seed_data.py
   ```

3. **Start the Backend API Gateway & 15 Microservices**:
   ```bash
   python scripts/run_local.py
   ```
   *Backend is live on: `http://127.0.0.1:8000` (API Docs on `/docs`)*

4. **Start the Frontend UI**:
   ```bash
   cd frontend
   npm run dev
   ```
   *Frontend is live on: `http://localhost:3000`*

---

### Option B: Complete Docker Compose Deployment

Run the full distributed containerized stack:
```bash
docker-compose up --build
```

**Port Mappings**:
- Frontend UI: `http://localhost:3000`
- API Gateway & Swagger: `http://localhost:8000`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3001` (Credentials: `admin` / `admin`)
- RabbitMQ Management: `http://localhost:15672` (Credentials: `guest` / `guest`)

---

## 7. Demo Accounts & Test Credentials

| Role | Email | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Customer** | `john.doe@example.com` | `customer123` | Browsing, shopping cart, checkout, order tracking, reviews, tickets. |
| **Admin** | `admin@ecommerce.com` | `admin123` | KPI dashboard, product CRUD, inventory adjustments, orders fulfillment. |
| **Support Lead**| `support@ecommerce.com`| `support123` | Support ticket response and resolution management. |

### Active Promotional Coupons:
- `SAVE10` - 10% discount on orders above ₹500
- `SUPER50` - 50% discount up to ₹1,500
- `FREESHIP` - Free delivery on any order
- `FESTIVE25` - 25% discount up to ₹3,000
- `FLAT500` - Flat ₹500 discount on orders above ₹2,500
