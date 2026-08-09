# SQL vs. NoSQL Databases & When to Use Which

In system design, choosing between a **SQL (Relational)** and a **NoSQL (Non-Relational)** database is one of the most critical architectural decisions. The right choice depends on data structure, transaction requirements, scaling needs, and query patterns.

---

## 1. Core Philosophical Difference

* **SQL Databases**: Built around **structure and integrity**. Data is stored in fixed tables with predefined columns and strict rules (schemas). They focus on keeping data consistent and avoiding duplication.
* **NoSQL Databases**: Built around **flexibility and scalability**. Data is stored without rigid schemas, often optimized for specific read/write patterns and designed to distribute easily across multiple servers.

```
SQL Structure (Tables & Relationships):
┌──────────────┐         ┌──────────────┐
│  Users Table │──1:N───>│ Orders Table │
└──────────────┘         └──────────────┘

NoSQL Structure (Self-Contained Documents / Keys):
{
  "user_id": 101,
  "name": "Alice",
  "orders": [ {"order_id": 5001, "total": 45.00} ]
}
```

---

## 2. Deep Dive: SQL (Relational Databases)

SQL databases organize data into **Tables** consisting of **Rows** and **Columns**. Relationships between tables are defined using **Foreign Keys**.

### Key Characteristics

1. **Strict Schema**

   You must define tables, column names, and data types before inserting data. Changing the schema later on large datasets can require migrations.

2. **ACID Guarantees**

   Relational databases prioritize strict transactional integrity:

   - **Atomicity:** Either all operations in a transaction succeed together, or the entire transaction is completely undone if any part fails (all-or-nothing).
   
   - **Consistency:** Data must follow all predefined rules and constraints (such as non-negative balances, unique emails, or valid foreign keys) before and after a transaction, ensuring invalid data can never enter the database.
   
   - **Isolation:** Concurrent transactions running at the exact same time operate independently without seeing or interfering with each other's in-progress changes.
   
   - **Durability:** Once a transaction is committed, its changes are permanently stored on disk and will survive system crashes or power outages.

3. **Powerful Querying (SQL)**

   Support complex `JOIN` operations, aggregations, and filtering across multiple tables in a single query.

4. **Scaling Model**

   Primarily **Vertical Scaling** (scaling up by adding more CPU, RAM, or faster SSDs to a single server). Read replicas can offload reads, but distributed writes are harder to manage.

### Popular Examples
* **PostgreSQL** (Feature-rich, strong JSON support, enterprise favorite)
* **MySQL** (Widely adopted, powering web platforms)
* **SQLite** (Embedded, single-file database for mobile and lightweight apps)

---

## 3. Deep Dive: NoSQL (Non-Relational Databases)

NoSQL databases abandon the rigid tabular model to optimize for horizontal expansion and varied data structures.

### The 4 Major Types of NoSQL Databases

#### 1. Key-Value Stores
Stores data as a hash table with a unique lookup key mapped to a value.
* **How it works**: Direct key lookup → `Get("user_session_101") → {data}`
* **Best for**: Caching, session management, user preferences.
* **Examples**: **Redis**, **Amazon DynamoDB**, **Memcached**.

#### 2. Document Databases
Stores data as flexible documents (usually JSON or BSON format). Each document can have a different structure.
* **How it works**: Hierarchical objects stored together without needing JOINs.
* **Best for**: Content management systems, e-commerce product catalogs, user profiles.
* **Examples**: **MongoDB**, **CouchDB**.

#### 3. Wide-Column (Column-Family) Stores
Stores data in column families rather than rows. Data stored in the same column is stored together on disk.
* **How it works**: Optimized for high write throughput and aggregations over huge datasets.
* **Best for**: Time-series logging, IoT telemetry, analytics, event tracing.
* **Examples**: **Apache Cassandra**, **Apache HBase**, **ScyllaDB**.

#### 4. Graph Databases
Stores data as **Nodes** (entities) and **Edges** (relationships between entities).
* **How it works**: Queries traverse connections directly without costly SQL JOIN operations.
* **Best for**: Social networks, fraud detection networks, recommendation engines.
* **Examples**: **Neo4j**, **Amazon Neptune**.

### Scaling & Consistency Model
* **BASE Model**: NoSQL systems often sacrifice strict ACID consistency for high availability and performance (BASE: **B**asically **A**vailable, **S**oft-state, **E**ventual consistency).
* **Horizontal Scaling**: Designed to scale out easily across dozens or hundreds of servers (sharding and distributed partitions).

---

## 4. Side-by-Side Comparison

| Feature | SQL Databases | NoSQL Databases |
| :--- | :--- | :--- |
| **Data Model** | Structured tables (rows and columns) | Key-value, Document, Column-Family, Graph |
| **Schema** | Fixed / Rigid (Schema-on-write) | Dynamic / Flexible (Schema-on-read) |
| **Scaling** | Vertical (scale-up) | Horizontal (scale-out) |
| **Joins** | Native and highly optimized | Disencouraged / Rare (Requires app-level logic) |
| **Data Integrity** | ACID compliance (High consistency) | BASE model (Eventual consistency focus) |
| **Primary Focus** | Data safety, relationships, complex queries | High throughput, large volumes, flexible models |

---

## 5. Decision Framework: When to Use Which?

```
                      [ Start Decision ]
                              │
               Is your data structure predictable 
                 and highly relational (JOINs)?
                       ┌──────┴──────┐
                      YES            NO
                       │             │
                [ Choose SQL ]  [ Choose NoSQL ]
                                     │
                    What is your primary access pattern?
                       ├─ Key lookup / Caching  → Key-Value (Redis)
                       ├─ Rich JSON / Catalogs  → Document (MongoDB)
                       ├─ Time-series / Logging → Wide-Column (Cassandra)
                       └─ Connected Networks   → Graph (Neo4j)
```

### Choose SQL When:
1. **Financial or Transactional Systems**: Banking, payment processing, e-commerce order management where an incomplete write or inconsistent state is unacceptable.
2. **Structured & Stable Schema**: Your entity relationships are well-known and rarely change unpredictably.
3. **Complex Reporting & Analysis**: You rely heavily on multi-table JOINs, complex filters, and aggregate calculations.

### Choose NoSQL When:
1. **Massive Scale & High Write Velocity**: Logging millions of metrics per second across thousands of devices.
2. **Unstructured or Rapidly Changing Data**: E-commerce catalogs where different categories have completely distinct attributes (e.g., Shoes have sizes; Laptops have RAM/CPU specs).
3. **Low Latency & Simple Access Patterns**: Caching session data or retrieving user profiles by ID in single-digit milliseconds.
4. **Global Distributed Deployments**: Multi-region setups where high availability and partition tolerance are prioritized over immediate global consistency.