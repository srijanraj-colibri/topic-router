# Alfresco AI Event Router (Community Edition)

A **generic, extensible, event-driven router** for Alfresco Community Edition that enables
external AI processing (auto-tagging, metadata extraction, vector embeddings, etc.)
**without using any Enterprise-only features**.

This service **subscribes durably to Alfresco repository events via ActiveMQ** and
**fans out events into feature-specific queues**, keeping the Alfresco repository fast,
safe, and upgrade-friendly.

---

## 🚀 Why This Exists

Alfresco Community Edition:

- Does **not** provide AI auto-tagging
- Does **not** provide vector generation
- Does **not** expose an external Event Gateway
- Must remain fast and stable under heavy uploads

AI workloads are:
- Slow
- Failure-prone
- Not suitable for repository JVM threads

This router enables **AI-driven extensions** using a **clean, decoupled, event-driven architecture**.

---

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
┌──────────────┬──────────────┬──────────────┐
| Autotag Q | Metadata Q | Vector Q |
└──────────────┴──────────────┴──────────────┘
|
v
Independent AI / Processing Workers

**Key principle:**  
> Alfresco announces *what happened*.  
> Python decides *what needs to be done*.  
> Queues guarantee *reliable execution*.

---

## ✅ Key Features

- ✅ **Community Edition compatible**
- ✅ Uses Alfresco’s built-in **ActiveMQ**
- ✅ **Durable topic subscription**
- ✅ **CLIENT_ACK semantics**
- ✅ Reliable fan-out to multiple queues
- ✅ Extensible plugin-based routing
- ✅ No AI processing inside Alfresco JVM
- ✅ Safe under high upload volume
- ✅ Future-proof and upgrade-safe

---

router-service/
├── core/ # Router framework (stable)
│ ├── base.py # Abstract route definition
│ ├── listener.py # Topic listener (fan-out logic)
│ ├── publisher.py # ActiveMQ queue publisher
│ ├── registry.py # Dynamic route discovery
│ └── schema.py # Event schema
│
├── routes/ # Feature plugins (extend here)
│ └── autotag.py # Auto-tagging route
│
├── main.py # Application entrypoint
├── settings.py # Pydantic-validated config
├── requirements.txt
│
├── docker/
│ ├── Dockerfile
│ ├── docker-compose.yml
│ └── .dockerignore
│
├── .gitignore
└── .env # Local only (ignored)


## 🔌 Configuration

All configuration is injected via **environment variables**.

`.env` is used **only by Docker Compose** and is **not included in the image**.

### Example `.env`

```env
# ActiveMQ
ACTIVEMQ_HOST= <activemq host>
ACTIVEMQ_PORT= <activemq port>
ACTIVEMQ_USER= <activemq user>
ACTIVEMQ_PASSWORD= <activemq password>

# Router
EVENT_TOPIC= <alfresco upload events topic>
ROUTER_SUBSCRIPTION_NAME= <router subscription name>

# Feature queues
AUTOTAG_QUEUE=<autotag queue eg: /queue/alfresco.autotag>

LOG_LEVEL=INFO


🧩 Routing Model (Extensible by Design)

Each feature is implemented as a route plugin.

Route responsibilities

Decide whether to process an event

Optionally transform the payload

Declare which queue to publish to

Routes do not:

Talk to ActiveMQ directly

Perform AI processing

Manage retries

Example Route: Auto-Tagging
class AutoTagRoute(BaseRoute):
    def should_route(self, event):
        return event.eventType == "CREATE"

Adding a New Feature (Example)

To add automatic metadata extraction:

Create routes/autometa.py

Define a new route class

Add an env variable:

AUTOMETA_QUEUE=/queue/alfresco.autometa


Restart the router

✔ No changes to core
✔ No changes to Alfresco
✔ No redeploy of existing features

🔐 Reliability & Safety Guarantees

Durable topic subscription

CLIENT_ACK

Message is ACKed only after all queue publishes succeed

Failure → no ACK → broker redelivery

No data loss

Safe restarts


🐳 Running with Docker

From the project root:

docker-compose --env-file .env -f docker/docker-compose.yaml up --build

Docker Compose will:

Load .env

Inject environment variables

Build the image

Start the router


🧪 What This Service Does NOT Do

❌ AI processing

❌ Tagging logic

❌ Metadata extraction

❌ Vector generation

❌ Direct Alfresco API calls

Those belong in downstream workers, not here.