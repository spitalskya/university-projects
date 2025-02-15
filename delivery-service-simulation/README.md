# Delivery Service Simulation

This project simulates a delivery service where customers can send packages using basic or first-class couriers. The system calculates delivery prices, assigns packages to couriers, and simulates the delivery process, ensuring that couriers take the shortest possible path. The service also logs all package status changes to a file and allows customers to track the status of their packages.

## Features

- **Package Delivery**: Customers can send packages, choosing between basic or first-class couriers.
- **Routing**: Couriers take the shortest possible path using Dijkstra's algorithm.
- **Time Simulation**: The simulation moves forward in days, updating courier and package statuses.
- **Logging**: All package status changes are logged to a text file.
- **Tracking**: Customers can check the status of their packages.

## Classes

- `DeliveryService`: Handles package delivery requests and manages couriers and packages.
- `Package`: Stores information about each package, including its current location and delivery status.
- `CourierHandler`: Manages couriers, assigns packages, and handles courier movements.
- `Courier`: Represents a courier, manages their deliveries, and simulates their movements.
- `Map`: Stores cities and calculates shortest paths between them.
- `City`: Represents a city and its neighbors, including distances to neighboring cities.

This simulation allows for flexible testing of different courier types, package weights, and city networks, with detailed logging and status updates for each package.

A more detailed documentation can be found in the [documentation file](delivery-service/documentation/documentation.md)