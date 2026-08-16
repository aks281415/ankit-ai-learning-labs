# Introduction to System Design

At its core, **System Design is the process of designing a system's architecture, components, data flow and trade-offs to meet its functional and non-functional requirements.** While it is crucial for massive scale, even a system with 100 users requires thoughtful architecture to ensure reliability, security and maintainability.

When you build a basic prototype, you might just spin up a single server, attach a single database and write your code. However, as requirements grow, that naive architecture breaks:
* Your single server's CPU hits 100% and crashes.
* Your database hits critical bottlenecks (e.g., exhausting CPU, memory, IOPS, connection limits, or query locks).
* Users in Australia complain the app takes 10 seconds to load because your only server is in New York.

System Design is the process of defining the architecture, components and data flow of a system to achieve goals like:
1. **Scalability:** The system can efficiently handle growing traffic and data without degrading performance.
2. **Reliability:** The system survives hardware or software failures. This involves configuring replication, health checks, load balancers and automatic failover to meet strict RTO/RPO targets.
3. **Maintainability:** The architecture enforces clear ownership boundaries, modularity, and strong development practices, allowing teams to scale and work independently.

The golden rule of System Design is that **there are no perfect solutions, only trade-offs.** You cannot have infinite speed, infinite accuracy and infinite storage for free. System Design is the art of making the right mathematical and architectural trade-offs for your specific business problem.

---

## The Two Types of System Design

System design is generally broken down into two distinct phases:

### 1. High-Level Design (HLD)

HLD focuses on the overall architecture of the entire system. At this stage, you abstract away the code and focus on the major building blocks.
* **What you design:** System boundaries, component communication, data flow, deployment architecture, load balancers, microservices and high-level technology choices (e.g., SQL vs NoSQL).
* **The Goal:** Ensuring the overall system won't bottleneck under heavy traffic and that it meets the business requirements for uptime and speed.
* **Example:** "When a user uploads a video, the request hits a Load Balancer, goes to the Video Service, which drops an event in a Kafka Queue so the Encoding Service can process it in the background."

### 2. Low-Level Design (LLD)

LLD zooms in on specific components from your High-Level Design and defines exactly how to build them in code. 
* **What you design:** Detailed interaction flows, interfaces, class diagrams, database schemas (tables, indexes), exact JSON API contracts, and specific algorithms.
* **The Goal:** Giving developers the exact technical specifications they need so they can sit down and start writing the code.
* **Example:** "The `Users` database table will have a `user_id` as a UUID primary key, and the `uploadVideo()` API will accept a POST request returning a 202 Accepted status with a JSON payload containing the `video_status`."

---

## Core Terminology

* **Latency:** The actual time it takes for a single request to travel to the backend, get processed, and return to the client. You usually measure this in milliseconds. If latency is high, the app feels sluggish and unresponsive to the user.
* **Throughput:** The total volume of traffic your system can handle at any given time, typically measured in Requests Per Second (RPS). While latency is about raw speed, throughput is about total capacity.
* **Availability:** The percentage of time your system is actually up and serving traffic. You'll often hear this described in "nines" (for example, "Five Nines" means 99.999% uptime).
* **Fault Tolerance:** How well your system handles inevitable crashes. A fault-tolerant architecture assumes that hardware and software will eventually break, and is designed to keep the application running smoothly even when internal components fail.
* **SPOF (Single Point of Failure):** That one critical piece of infrastructure that, if it goes down, takes your entire system offline with it. Good system design is essentially a constant hunt to find and eliminate SPOFs using redundancy.
* **Strong Consistency:** The guarantee that the moment a piece of data is updated, *every* subsequent read will see the new data. It is very safe for things like financial transactions, but waiting for all servers to sync makes it slower.
* **Eventual Consistency:** Data takes a few milliseconds or seconds to sync across all your database nodes. For a brief window, a user might see slightly stale data, but it will *eventually* become accurate. This trade-off gives you incredible speed and is heavily used in microservices and CDNs.
* **Stateless:** The server treats every single request as brand new and remembers nothing about past interactions. Because the client passes all necessary context (like auth tokens) directly in the request, you can easily spin up hundreds of stateless servers to handle massive traffic.
* **Stateful:** The server actively remembers data (like user session info) between requests. This makes horizontal scaling much harder, because you have to ensure a user's future requests are routed back to the exact same server they originally talked to.
* **Coupling:** How deeply tangled your components are. **Tight coupling** means updating one service will likely break another. Microservices aim for **loose coupling**, where services interact strictly through APIs or event queues so teams can deploy changes independently without causing a domino effect.
* **Server / Node:** A physical or virtual computer that runs your code. In distributed systems (like Kubernetes), you'll usually hear them called "Nodes", which represent individual worker machines within a massive cluster.
* **Virtual Machine (VM):** A software emulation of a physical computer. It lets you run multiple, completely independent operating systems on a single physical server, maximizing hardware usage.
* **Container (Docker):** A lightweight, standalone package that bundles your code and all its dependencies. Because it shares the host machine's OS kernel instead of booting up an entire operating system like a VM does, a container can start in milliseconds.
* **Pod:** The absolute smallest unit you can deploy in Kubernetes. Think of it as a wrapper around your container (usually one container per pod). When traffic surges, Kubernetes scales out by simply spinning up more of these pods.
* **Replicas:** Synchronized backup copies of your primary database. If the main database crashes, a replica instantly takes over. Teams also route heavy "read" traffic to replicas to take the pressure off the primary database.
* **Throttling (Rate Limiting):** A defense mechanism that restricts how many requests a specific client or IP address can make within a certain timeframe. It protects your backend from getting exhausted by abuse, bots, or sudden traffic spikes.