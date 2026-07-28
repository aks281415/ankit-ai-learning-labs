# Database Sharding

## 1. What is Database Sharding?

**Database Sharding** is a distributed architecture technique where a single, massive database table is split across **multiple independent physical servers (machines)**. Each individual server holding a subset of the data is called a **Shard**.

To your application, all shards together represent a single giant logical database.

---

## 2. Sharding vs. Partitioning (The Core Difference)

> **The Golden Rule**: Partitioning splits data **on ONE single machine**. Sharding splits data **across MULTIPLE physical machines**.

| Feature | Database Partitioning | Database Sharding |
| :--- | :--- | :--- |
| **Physical Hardware** | Single Database Server | Multiple Independent Servers (Cluster) |
| **Primary Goal** | Smaller indexes, fast data deletion, query pruning. | Unlimited **Write Throughput** and storage scaling. |
| **Write Scaling** | Limited to 1 server's CPU, RAM, & Disk IOPS. | Multiplies CPU, RAM, & Disk IOPS across $N$ servers. |
| **System Complexity** | Low (Handled natively inside DB engine). | High (Requires router/proxy, distributed transactions). |
| **Cost** | Low (Single node). | High (Requires running multiple servers). |

---

## 3. What is a Shard Key?

A **Shard Key** is the column (e.g. `user_id`) used to determine which server holds a given row.

* **Purpose**: Routes queries directly to the correct server.
* **Goal**: Pick a key that distributes data evenly to avoid overloading any single server.

---

## 4. Scaling Individual Shards (Master-Slave / Primary-Secondary)

Within a sharded architecture, each individual shard can be scaled further using a **Master-Slave** setup:

* **Master (Primary)**: Handles all write operations (`INSERT`, `UPDATE`, `DELETE`).
* **Slaves (Replicas)**: Replicate data from the Master and handle read queries (`SELECT`) to offload read traffic.

---

## 5. Sharding Strategies

1. **Range-Based Sharding**: Routes data based on value ranges.
   * *Example*: Server 1 handles `user_id` 1–1,000,000; Server 2 handles 1,000,001–2,000,000.
2. **Directory / Lookup-Based Sharding**: Uses a lookup table (e.g. Redis) to map `user_id -> server_ip`.
   * *Benefit*: Extremely flexible to move users between servers.
3. **Geographic / Region-Based Sharding**: Routes data based on location.
   * *Example*: US users $\rightarrow$ US DB Server; EU users $\rightarrow$ EU DB Server (Great for low latency & GDPR compliance).
4. **Hash-Based Sharding & Consistent Hashing**: Uses hash functions (`hash(user_id) % N`) to evenly scatter data.
   * *Consistent Hashing*: A 360° hash ring algorithm that prevents moving 80%+ of existing data when adding or removing servers.

---

## 6. Disadvantages of Database Sharding

1. **Manual Application Routing Logic**:
   * Standard SQL databases do not natively know how to route to 10 servers. Developers must manually write application code (or deploy an intermediate proxy) to decide which shard to query from and which shard to write new records into.
2. **Complex & Slow Cross-Shard Joins**:
   * Joining tables residing on different physical shards (e.g. `users` on Server 1 and `orders` on Server 3) cannot be executed natively. The application must fetch raw rows over the network from multiple servers and merge them manually in code.
3. **Manual Handling of New Record Insertion**:
   * Every time a new record is added, the application code must explicitly evaluate the shard key logic to calculate and connect to the target shard database before executing the `INSERT`.
4. **Loss of Native ACID Transactions**:
   * Performing an atomic transaction across multiple shards requires complex, high-latency protocols (like Two-Phase Commit / 2PC) rather than native database transactions.
5. **Rebalancing Complexity**:
   * Adding or removing a shard server requires complex data migration tasks to rebalance data without causing downtime.

---

## 7. Database Scaling Intuition

When scaling a database, follow these techniques in order. Start with the simplest solution and only move to the next one when the previous approach is no longer sufficient.

### 1. Start with Vertical Scaling

Always try to make your existing database server more powerful first by upgrading its CPU, RAM, or storage. Vertical scaling is the simplest, cheapest, and least complex way to improve database performance because it doesn't require architectural changes.

### 2. Optimize Before Scaling

Before adding more hardware or servers, optimize your database.

- Add appropriate indexes.
- Tune slow queries.
- Cache frequently accessed data.

Many performance issues are caused by inefficient queries rather than insufficient hardware.

### 3. If Your Application Is Read-Heavy, Add Read Replicas

Keep one **primary** database responsible for writes and use one or more **read replicas** to serve read requests. This increases read capacity significantly without changing your application's data model.

### 4. If a Single Table Becomes Very Large, Use Partitioning

If a table grows to billions of rows, partition it into smaller pieces based on criteria such as date, region, or user ID. Partitioning keeps all data on the same database server while making queries and maintenance more efficient.

### 5. When The Incoming Traffic Is Write Heavy

If your application receives a very high volume of write requests and a single database server cannot process them efficiently, sharding can distribute the writes across multiple servers. This allows the write workload to scale horizontally and prevents a single machine from becoming a bottleneck.