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



# Cart Service API

## Description
This project implements a simple cart service using the FastAPI framework. It allows users to add and remove items from a shopping cart. The service provides a RESTful API for managing cart contents, interacting with an external inventory service to validate item and stock availability.

## API Endpoints

This section demonstrates how to interact with the API endpoints using `curl` from your terminal.

### Add item to the cart
This endpoint adds a specified item and quantity to a user's cart. The request body is a JSON object with the `item_id` and `quantity`.

#### Request
```sh
## Add item to the cart for user_is 1123
curl -X POST http://localhost:8002/cart/1123/add \-H "Content-Type: application/json" \-d '{"item_id": "1-1", "quantity": 2}'
## See the cart
curl -X GET http://localhost:8002/cart/1123
## Remove item to the cart for user_is 1123
curl -X DELETE  http://localhost:8002/cart/1123/remove/1-1

## Update item to the cart for user_is 1123
curl -X PUT  http://localhost:8002/cart/1123/update/1-1 \-H 'Content-Type: application/json' \-d '{    "quantity": 5  }'