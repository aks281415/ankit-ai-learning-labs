# Database Indexing

Database Indexing is a data structure technique used to quickly locate and access data in a database without searching every row in a database table every time it is queried.

Think of a database index like the **index at the back of a textbook**:
* **Without an index**: To find where a topic is discussed, you must scan every single page of the book from start to finish (**Full Table Scan**).
* **With an index**: You look up the topic alphabetically in the index, find the exact page number, and jump directly to it (**Index Lookup**).

---

## 1. How Database Indexing Works

When you run a query like:

```sql
SELECT * FROM users WHERE email = 'alex@example.com';
```

* **Without an Index (\(O(N)\) Time Complexity)**: The database engine searches sequentially through all $N$ rows in the table. If you have 10 million rows, it checks all 10 million rows.
* **With an Index (\(O(\log N)\) Time Complexity)**: The database maintains a separate data structure (e.g., a B-Tree) mapping column values (like `email`) to their physical storage location on disk.

> **💡 Core Intuition**: Just like **Binary Search**, indexing works because data is kept in a sorted tree structure, allowing the database to eliminate massive chunks of data at each step. Databases use a **B-Tree** ($N$-way split) so they can find any record out of millions in just **3 to 4 quick steps**.

---

## 2. Common Index Data Structures

1. **B-Tree / B+Tree (Most Common)**:
   * Used by default in RDBMS like PostgreSQL, MySQL (InnoDB), and Oracle.
   * Keeps data sorted and allows fast searches, sequential access, insertions, and deletions.
   * Works exceptionally well for equality (`=`), range queries (`<`, `>`, `BETWEEN`), and sorting (`ORDER BY`).

2. **Hash Index**:
   * Stores key-value pairs using a hash function.
   * Extremely fast (\(O(1)\)) for exact equality matches (`WHERE id = 5`), but **does not support range queries** or sorting.

3. **GIN / GiST (Generalized Inverted / Search Trees)**:
   * Used in databases like PostgreSQL for complex data types such as full-text search, JSON document fields, and spatial/GIS coordinates.

---

## 3. Types of Indexes

* **Clustered Index**:
  * Dictates the **physical order** of data on disk.
  * Every table can have **only one** clustered index (usually automatically created on the Primary Key).
* **Non-Clustered Index**:
  * A separate structure from the actual table data. It contains index key values and pointers (Row IDs or Primary Keys) back to the actual table rows.
  * A table can have **multiple** non-clustered indexes.
* **Composite Index (Multi-Column)**:
  * An index built on multiple columns (e.g., `(last_name, first_name)`).
  * **Important**: Follows the **leftmost prefix rule**—the query must filter by the leftmost column in the composite key for the index to be used.

---

## 4. Trade-Offs: The Cost of Indexing

Indexing is not free; it involves trade-offs:

| Pros | Cons |
| :--- | :--- |
| **Faster Queries**: Drastically speeds up `SELECT`, `JOIN`, `WHERE`, and `ORDER BY` operations. | **Slower Writes**: Every `INSERT`, `UPDATE`, or `DELETE` requires updating both the table and all associated indexes. |
| **Enforces Uniqueness**: Unique indexes guarantee value uniqueness (e.g., primary keys, email). | **Disk & Memory Overhead**: Indexes consume extra disk storage and buffer RAM. |

---

## 5. Intuition Framework: Which Column to Index?

### The CARDS Mental Framework

1. **C — Cardinality (Selectivity)**:
   * **High Cardinality (Index This)**: Columns with many unique values (e.g., `user_id`, `email`, `uuid`).
   * **Low Cardinality (Skip This)**: Columns with very few unique values (e.g., `status` [`'active'`, `'pending'`], `gender`, `is_deleted`).
2. **A — Access Patterns (`WHERE` & `JOIN`)**:
   * Index columns frequently used in `WHERE col = val`, `WHERE col IN (...)`, and `JOIN` conditions (`ON tableA.col_id = tableB.col_id`).
3. **R — Range & Sorting (`ORDER BY`, `GROUP BY`)**:
   * Indexing pre-sorts data. Indexing columns in `ORDER BY created_at DESC` avoids expensive in-memory sorts (filesorts).
4. **D — Direction & Composite Index Order (The ESR Rule)**:
   * For composite indexes, order columns as:
     $$\text{Equality (=)} \longrightarrow \text{Sort (ORDER BY)} \longrightarrow \text{Range (<, >, BETWEEN)}$$
5. **S — Storage & Write Mutation Cost**:
   * Every `INSERT`, `UPDATE`, or `DELETE` on an indexed column updates the index tree. Avoid indexing columns that update constantly unless necessary.

---

## 6. Summary: When to Index vs. When NOT to Index

### ✅ **When to create an index:**
* Columns frequently used in `WHERE` clauses.
* Columns used as foreign keys in `JOIN` conditions.
* Columns used in `ORDER BY` or `GROUP BY` operations.
* Columns with high cardinality (a large number of unique values, such as `user_id` or `email`).

### ❌ **When NOT to index:**
* Small tables (a full table scan is often faster for a few hundred rows).
* Columns with low cardinality (few unique values, like `gender` or `is_active` boolean flags).
* Tables with heavy write workloads (`INSERT`/`UPDATE` heavy) and very few reads.
* Columns that are frequently modified.


