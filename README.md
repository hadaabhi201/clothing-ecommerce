# clothing-ecommerce
# Clothing Ecommerce Bootstrap

Simple Kafka based clothing ecommerce skeleton with Cart, Order, Payment, Inventory, Shipping, and Notification services.

## Quick start
1. Copy `.env.example` to `.env`.
2. `make install`
3. `make up` to start Kafka if you use this compose.
4. `make topics` to create project topics.

## Services
Each service has `producer.py`, `consumer.py`, and `main.py`. You can run them locally or add service blocks to `docker-compose.yml`.
