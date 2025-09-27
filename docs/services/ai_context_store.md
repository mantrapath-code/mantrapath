# AI Context Store Service

## Description

The AI Context Store Service acts as the central nervous system for the MantraPath platform. Its primary role is to aggregate and maintain a real-time, holistic view of each user's context. It consumes events and data from all other microservices to build a rich, dynamic user profile. This unified context is then made available to other services, enabling intelligent, personalized, and proactive features across the entire application.

This service solves the critical problem of data silos in a microservices architecture. By creating a centralized repository for user context, it ensures that actions and recommendations in one part of the platform are informed by user activities in another, leading to a more cohesive and intelligent user experience.

## Table of Contents

- [Installation / Setup](#installation--setup)
- [Usage](#usage)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Contributing](#contributing)
- [License](#license)
- [Contact / Author Info](#contact--author-info)
- [FAQ / Troubleshooting](#faq--troubleshooting)
- [Future Implementation](#future-implementation)

## Installation / Setup

### Prerequisites

-   Python 3.10+
-   Docker and Docker Compose
-   Redis
-   PostgreSQL (for user data)

### Installation Commands

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/mantrapath-code/mantrapath.git
    cd mantrapath/backend/services/ai_context_store
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

-   Configuration is managed via environment variables. Create a `.env` file by copying the example:
    ```bash
    cp .env.example .env
    nano .env
    ```
-   Essential variables include `REDIS_URL`, `DATABASE_URL`, and settings for the event bus connection.

## Usage

The AI Context Store is primarily an event-driven service that runs in the background, but it also exposes an API for other services to query user context directly.

-   **Running the service locally:**
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8006 --reload
    ```

-   **Running with Docker:**
    ```bash
    docker-compose up -d ai_context_store
    ```

-   **API for Context Retrieval:**
    Other services can fetch the latest context for a user by making a GET request to `/context/{user_id}`. The API documentation is available at `http://localhost:8006/docs`.

## Features

-   **Real-time Event Aggregation:** Listens to events from all services (mood, community, voice, etc.) to update user context instantly.
-   **Contextual User Profile Building:** Creates a comprehensive profile that includes mood history, community interactions, content preferences, and more.
-   **Cross-Service Intelligence:** Provides the data foundation for features like personalized recommendations and proactive assistance.
-   **Event-Driven Architecture:** Context is updated asynchronously through an event bus, ensuring low latency and high throughput.
-   **Historical Context Analysis:** Stores and provides access to historical user context for trend analysis and deeper insights.
-   **High-Performance Caching:** Utilizes Redis for fast read/write access to user context data.

## Tech Stack

-   **Backend:** Python, FastAPI
-   **Data Stores:** Redis (for caching and real-time context), PostgreSQL (for persistent storage)
-   **Messaging:** NATS JetStream (via shared event bus)
-   **Containerization:** Docker

## Contributing

Contributions are highly encouraged! Please adhere to the following process:

1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/new-context-source`).
3.  Implement your changes.
4.  Add or update tests and ensure they all pass.
5.  Submit a pull request with a detailed description of your changes.

## License

This project is licensed under the MantraPath License.

## Contact / Author Info

-   **Author:** Sachin Sharma
-   **Email:** sachin.sharma@mantrapath.com
-   **GitHub:** [ssharmasachin](https://github.com/ssharmasachin)

## FAQ / Troubleshooting

-   **"Context data is not updating"**: Ensure the service is correctly connected to the event bus and that other services are publishing events. Check the logs for any connection errors.
-   **"High latency in context retrieval"**: Verify that Redis is running and properly configured. Check the Redis memory usage and connection pool settings.

## Future Implementation

-   **Predictive Context:** Implement machine learning models to predict a user's future context or needs based on historical data.
-   **Long-Term Behavior Modeling:** Develop models to understand long-term user behavior patterns and mental wellness trajectories.
-   **External Data Integration:** Allow users to connect external data sources (e.g., calendars, fitness trackers) to enrich their context further.
-   **Context-Aware Anomaly Detection:** Proactively identify unusual patterns in user behavior that may indicate a need for support.
