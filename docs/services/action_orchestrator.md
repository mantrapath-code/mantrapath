# Action Orchestrator Service

## Description

The Action Orchestrator Service is a core component of the MantraPath platform, responsible for coordinating complex, voice-driven workflows across multiple microservices. It acts as a central hub that understands user intent from voice commands and orchestrates a sequence of actions to fulfill the user's request. This service is essential for enabling seamless, hands-free interaction with the MantraPath application.

This service solves the problem of coordinating actions between decoupled microservices. Instead of having individual services communicate directly with each other in a complex web, the Action Orchestrator centralizes workflow logic, making the system more manageable, scalable, and easier to debug.

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

- Python 3.10+
- Docker and Docker Compose
- PostgreSQL
- Redis

### Installation Commands

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/mantrapath-code/mantrapath.git
    cd mantrapath/backend/services/action_orchestrator
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

-   Environment variables are managed in a `.env` file. Copy the example file and edit it with your configuration:
    ```bash
    cp .env.example .env
    nano .env
    ```
-   Key variables to configure include `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET_KEY`, and URLs for other MantraPath services.

## Usage

The Action Orchestrator is designed to be run as a background service. It exposes a REST API for other services to interact with.

-   **Running the service locally:**
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8012 --reload
    ```

-   **Running with Docker:**
    ```bash
    docker-compose up -d action_orchestrator
    ```

-   **API Documentation:**
    Once the service is running, interactive API documentation (Swagger UI) is available at `http://localhost:8012/docs`.

## Features

-   **Voice-driven workflow coordination:** Interprets voice commands to trigger multi-service actions.
-   **Centralized workflow management:** Simplifies inter-service communication.
-   **Stateful action execution:** Tracks the state of long-running workflows.
-   **Error handling and retries:** Implements robust error handling with retry logic for failed actions.
-   **Circuit breaker pattern:** Prevents cascading failures across the system.
-   **Integration with multiple services:** Connects with Auth, Profile, Mood, Chatbot, and other services.

## Tech Stack

-   **Backend:** Python, FastAPI
-   **Database:** PostgreSQL
-   **Cache:** Redis
-   **Containerization:** Docker
-   **Testing:** Pytest

## Contributing

We welcome contributions! Please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature`).
3.  Make your changes.
4.  Ensure all tests pass (`pytest`).
5.  Submit a pull request.

## License

This project is licensed under the MantraPath License.

## Contact / Author Info

-   **Author:** Sachin Sharma
-   **Email:** sachin.sharma@mantrapath.com
-   **GitHub:** [ssharmasachin](https://github.com/ssharmasachin)

## FAQ / Troubleshooting

-   **"Service fails to start"**: Check that all required environment variables are set and that dependent services (Postgres, Redis) are running.
-   **"Connection refused" errors in logs**: Verify the URLs for other services in your `.env` file are correct and that those services are running and accessible.

## Future Implementation

-   **Visual workflow builder:** A UI for creating and managing orchestration flows.
-   **Expanded voice command library:** Support for more complex and natural language commands.
-   **Integration with more third-party services:** Connect with external calendars, to-do lists, etc.
-   **Advanced analytics:** Provide insights into workflow performance and user interaction patterns.
