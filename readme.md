# Alfresco AI Event Router (Community Edition)

A generic, extensible, event-driven routing service for Alfresco Community Edition that enables external AI processing (auto-tagging, metadata extraction, vector embeddings, etc.) without using any Enterprise-only features.

The router subscribes durably to Alfresco repository events via ActiveMQ and fans out events into feature-specific queues, ensuring the Alfresco repository remains fast, safe, and upgrade-friendly.

---

## 🎯 Purpose

This service exists to solve a fundamental limitation of Alfresco Community Edition:

- ❌ No built-in AI auto-tagging  
- ❌ No vector embedding generation  
- ❌ No external event gateway  
- ❌ AI workloads cannot safely run inside the repository JVM  

AI workloads are inherently:

- **Slow**  
- **Failure-prone**  
- **Resource intensive**  
- **Unsuitable for synchronous repository execution**  

This router introduces a clean, decoupled, asynchronous architecture that allows AI and external processing without compromising Alfresco stability.

---

## 🧠 Core Idea

&gt; **Alfresco announces what happened.**  
&gt; **Python decides what needs to be done.**  
&gt; **Queues guarantee reliable execution.**

---

## 🏗 High-Level Architecture

Alfresco Community Repository
|
| emits repository events (CREATE / UPDATE / DELETE)
v
ActiveMQ Topic
(alfresco.upload.events)
|
| Durable subscription + CLIENT_ACK
v
Python Event Router
|
| Feature-based routing
v
+----------------+----------------+----------------+
| AutoTag Queue  | Metadata Queue | Vector Queue   |
+----------------+----------------+----------------+
|
v
Independent AI / Processing Workers

---

## ✨ Key Features

- ✅ Compatible with Alfresco Community Edition  
- ✅ Uses Alfresco’s built-in ActiveMQ  
- ✅ Durable topic subscription  
- ✅ CLIENT_ACK semantics  
- ✅ Reliable fan-out to multiple queues  
- ✅ Plugin-based, extensible routing model  
- ✅ No AI logic inside Alfresco JVM  
- ✅ Safe under high upload volume  
- ✅ Future-proof and upgrade-safe design  

---

## 📂 Base Project Structure

router-service/
├── core/                     # Stable router framework
│   ├── base.py               # Abstract route definition
│   ├── listener.py           # Topic listener & fan-out logic
│   ├── publisher.py          # ActiveMQ queue publisher
│   ├── registry.py           # Dynamic route discovery
│   └── schema.py             # Event schema (Pydantic)
│
├── routes/                   # Feature plugins (extend here)
│   └── autotag.py            # Auto-tagging route
│
├── main.py                   # Application entrypoint
├── settings.py               # Validated configuration
├── requirements.txt
│
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yaml
│   └── .dockerignore
│
├── .gitignore
└── .env                      # Local only (ignored)

---

## ⚙️ Configuration

All configuration is provided via environment variables (12-factor application compliant).

`.env` is used only by Docker Compose and is never baked into the image.

### Example `.env`

```env
# ActiveMQ
ACTIVEMQ_HOST=<activemq host>
ACTIVEMQ_PORT=<activemq port>
ACTIVEMQ_USER=<activemq user>
ACTIVEMQ_PASSWORD=<activemq password>

# Router
EVENT_TOPIC=<alfresco upload events topic>
ROUTER_CLIENT_ID=<durable client id>
ROUTER_SUBSCRIPTION_NAME=<durable subscription name>

# Feature queues
AUTOTAG_QUEUE=/queue/alfresco.autotag
<add your other feature queue based on usecase>

# Logging
LOG_LEVEL=INFO
```
---

## 📂 Base Project Structure

🧩 Routing Model (Extensible by Design)
Each feature is implemented as an independent route plugin.
Route Responsibilities
A route must:
Decide whether to process an event
Optionally transform the event payload
Declare which queue to publish to
A route must not:
Talk to ActiveMQ directly
Perform AI processing
Manage retries or failures

Example: Auto-Tagging Route

class AutoTagRoute(BaseRoute):
    def should_route(self, event):
        return event.event_type == "BINARY_CHANGED"

### ➕ Adding a New Feature (Example: Metadata Extraction)

Create a new route file: routes/autometa.py
Implement a route class:

class AutoMetaRoute(BaseRoute):
    ...

Add a new environment variable:
AUTOMETA_QUEUE=/queue/alfresco.autometa
Restart the router
✅ No changes to core
✅ No changes to Alfresco
✅ No redeploy of existing features

---

## 🚫 What This Service Does NOT Do

This service intentionally does not:
❌ Perform AI processing
❌ Apply tags
❌ Extract metadata
❌ Generate vectors
❌ Call Alfresco APIs directly
All of that belongs in downstream workers, not in the router.

## 🐳 Running with Docker

From the project root:

docker-compose --env-file .env -f docker/docker-compose.yaml up --build

Docker Compose will:
Load environment variables
Build the router image
Start the router service