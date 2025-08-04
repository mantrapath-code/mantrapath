# MantraPath Service Architecture Overview

## Introduction

This document provides a comprehensive overview of the MantraPath service architecture, with the Mood Service as the central intelligence hub orchestrating all platform activities. The architecture follows a microservices approach with strong integration between services, enabling a holistic mental health platform experience.

## High-Level Architecture

```
                                    ┌───────────────────────┐
                                    │                       │
                                    │  API Gateway / Load   │
                                    │      Balancer         │
                                    │                       │
                                    └───────────┬───────────┘
                                                │
                                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                     🧠 MOOD SERVICE (Central Hub)                   │
│                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐  │
│  │     Context     │    │   Predictive    │    │    Platform     │  │
│  │   Aggregation   │◄──►│    Analytics    │◄──►│  Orchestration  │  │
│  │      Layer      │    │     Engine      │    │      Layer      │  │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘  │
│                                                                     │
└───────┬─────────────────────┬─────────────────────┬────────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│               │     │               │     │               │
│   Chatbot     │     │  Community    │     │    Journal    │
│   Service     │     │   Service     │     │   Service     │
│               │     │               │     │               │
└─────┬─────────┘     └─────┬─────────┘     └─────┬─────────┘
      │                     │                     │
      ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│               │     │               │     │               │
│   ML/AI       │     │   Profile     │     │   Content     │
│   Service     │     │   Service     │     │   Service     │
│               │     │               │     │               │
└───────────────┘     └───────────────┘     └───────────────┘
```

## Core Components

1. **Mood Service (Central Hub):**
   - Context Aggregation Layer
   - Predictive Analytics Engine
   - Platform Orchestration Layer
   - Real-Time Processor
   - Cross-Service Coordinator

2. **Satellite Services:**
   - Chatbot Service
   - Community Service
   - Journal Service
   - ML/AI Service
   - Profile Service
   - Content Service
   - Voice Service
   - Translation Service

## Key Integration Patterns

1. **Event-Driven Communication:**
   - Platform-wide event bus
   - Real-time event processing
   - Service-specific event handlers

2. **Context Propagation:**
   - User context shared across services
   - Centralized context management
   - Real-time context updates

3. **Cross-Service Learning:**
   - Federated learning across services
   - Centralized knowledge repository
   - Continuous learning pipeline

## Data Flow Principles

1. **User-Centric Data Aggregation:**
   - All data centralized in Mood Service
   - Strong privacy controls and consent management
   - Comprehensive data governance

2. **Real-Time Intelligence:**
   - Sub-second context updates
   - Immediate adaptation across services
   - Continuous learning from all interactions

3. **Bidirectional Flow:**
   - Services both consume and generate insights
   - Feedback loops enhance platform intelligence
   - Cross-service data enrichment

## Deployment Architecture

The architecture supports deployment as:

1. **Containerized Microservices:**
   - Docker containers for each service
   - Kubernetes for orchestration
   - Horizontal scaling for high-demand services

2. **Service Mesh:**
   - Istio for service communication
   - Advanced traffic management
   - Centralized monitoring and observability

3. **API-First Design:**
   - RESTful APIs with OpenAPI specifications
   - GraphQL for complex data retrieval
   - Websockets for real-time communication

## Next Steps

For detailed documentation of each component:

1. See [Service Definitions](02_service_definitions.md) for individual service capabilities
2. See [Integration Patterns](03_integration_patterns.md) for service interaction details
3. See [Data Models](04_data_models.md) for shared data structures
4. See [API Specifications](05_api_specifications.md) for interface definitions
5. See [Deployment Architecture](06_deployment_architecture.md) for infrastructure details
