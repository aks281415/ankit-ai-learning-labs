# Database Partitioning

Database Partitioning is the technique of splitting a large database table into smaller, independent physical files on disk, while keeping it as a **single logical table** in your application code.

Think of it like a **filing cabinet**:
* **Without Partitioning**: Storing 1,000,000 documents in one giant box. Finding a document from March 2026 requires searching through all 1,000,000 pages.
* **With Partitioning**: Separating documents into 12 folders labeled by Month. Finding a March 2026 document only requires opening the March folder (**Partition Pruning**).

---

## 1. Real-World Problems Partitioning Solves

### Problem 1: Instant Data Deletion (No CPU Spikes or Crashes)
* **The Problem**: Running `DELETE FROM orders WHERE order_date < '2023-01-01'` on a 500M row table causes CPU spikes, lock contention, transaction log (WAL) explosion, and often crashes the database.
* **The Solution**: If 2023 data is in its own physical file (`orders_2023.ibd`), the database engine simply drops the file from the OS filesystem. It takes **2 milliseconds**, causes 0 row locks, and zero CPU spikes.

### Problem 2: Faster Queries (Partition Pruning)
* When you query `SELECT * FROM orders WHERE created_at = '2026-07-15'`, the query optimizer compares `'2026-07-15'` against its partition rule and **completely ignores** all physical files from 2023, 2024, and 2025.

### Problem 3: Fixing Massive Index Slowdowns (RAM vs. Disk)
* **The Problem**: When an unpartitioned table grows to 500M rows, its single global index becomes huge (e.g., 60 GB). If your server only has 32 GB of RAM, the index no longer fits in memory, forcing slow Disk reads during index lookups (Buffer Thrashing).
* **The Solution**: Data is partitioned first into separate physical files. The database then automatically builds a smaller **Local Index** inside each partition (e.g., 5 GB each). Active queries only search the local index of the target partition, which lives 100% in fast RAM!

---

## 2. Horizontal vs. Vertical Partitioning

```
ORIGINAL TABLE (users: id, name, email, bio, profile_pic_blob)

HORIZONTAL PARTITIONING (Splitting Rows)
+------------------------------------+  -> Partition 1: 2024 Rows
+------------------------------------+  -> Partition 2: 2025 Rows

VERTICAL PARTITIONING (Splitting Columns)
+----------------+  +--------------------------------+
| id, name, email|  | id, bio, profile_pic_blob      |
| (Fast Metadata)|  | (Heavy Data / BLOBs)           |
+----------------+  +--------------------------------+
```

| Type | How It Works | Best Used For |
| :--- | :--- | :--- |
| **Horizontal Partitioning** | Splits table by **rows** into separate physical files. | Tables with millions/billions of rows. |
| **Vertical Partitioning** | Splits table by **columns** into separate tables. | Separating lightweight frequent fields from heavy text/image BLOBs. |

---

## 3. The 3 Main Horizontal Partitioning Strategies

### 1. Range Partitioning
Splits data based on continuous value ranges (dates or numeric IDs).
* **Example**: `PARTITION BY RANGE (YEAR(created_at))`
* **Best for**: Logs, time-series data, transaction histories.

### 2. List Partitioning
Splits data based on discrete lists of values (e.g., regions or customer types).
* **Example**: `PARTITION BY LIST (region)` $\rightarrow$ `['US', 'CA']`, `['UK', 'FR']`, `['IN', 'JP']`
* **Real-World Use (Multi-Tenant Isolation)**: In SaaS apps (like Shopify), isolating large clients (e.g. Nike) in their own partition ensures their heavy traffic doesn't slow down small bakery clients.

### 3. Hash Partitioning

Applies a mathematical hash function to a column and routes rows using modulo arithmetic:

$$
\text{Partition Number} = \operatorname{hash}(userId) \bmod N
$$

* **How Routing Works**: Querying `WHERE user_id = 42` computes `hash(42) % 4 = 2`. The database immediately routes the request to **Partition #2**, resulting in **O(1)** partition lookup.
* **Best for**: Evenly distributing rows across partitions to prevent hotspots when there is no natural partitioning key such as a date or geographic region.

## 4. Key Gotchas & Best Practices

> **⚠️ 1. Beware of Cross-Partition Scans (Scatter-Gather)**
> If you run `SELECT * FROM orders WHERE status = 'PENDING'` without including the partition key (`created_at`), the DB doesn't know which file has pending orders. It must scan **every single partition**, hurting performance!
> * **Fix**: Always include the partition key in your queries (e.g., `WHERE status = 'PENDING' AND created_at >= '2026-01-01'`).

> **💡 2. Partitioning vs. Sharding**
> * **Partitioning**: Splitting data on a **single database server**.
> * **Sharding**: Splitting data across **multiple separate database machines**.