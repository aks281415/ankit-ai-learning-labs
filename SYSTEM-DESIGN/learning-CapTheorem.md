# CAP Theorem

## Assumption: We Are Talking About a Distributed System

The CAP Theorem only applies to **distributed systems**. So before anything else, let's understand what that means.

---

## What is a Distributed System?

A **distributed system** is when your database is NOT running on just one single machine. Instead, the data is spread across **multiple machines** that work together and communicate over a network.

You do this when one machine is no longer enough — too much data, too many requests, or you need the system to survive hardware failures.

---

## What is a Node?

Each individual machine in a distributed system is called a **Node**.

* A node is just a server — a computer with its own CPU, RAM, and disk.
* Each node holds a copy of (or a portion of) your data.
* Nodes talk to each other over the network to stay in sync.

```
  [ Node A ]      [ Node B ]      [ Node C ]
  (Server 1)      (Server 2)      (Server 3)
      |                |                |
      └────────────────┴────────────────┘
              (Network connections)
```

---

## What is a Cluster?

A **Cluster** is the name for the entire group of nodes working together as one logical database.

* Your application talks to the **cluster** as if it's a single database.
* Internally, the cluster routes requests to the right node(s).

```
            DATABASE CLUSTER
  ┌──────────────────────────────────────┐
  │  [ Node A ]  [ Node B ]  [ Node C ]  │
  └──────────────────────────────────────┘
                    ↑
      Your app talks to this as one unit
```

> **Simple Rule**: Node = one player. Cluster = the entire team.

---

## What is the CAP Theorem?

The **CAP Theorem** says:

> In a distributed system, you can only guarantee **2 out of these 3 properties** at the same time: **Consistency**, **Availability**, and **Partition Tolerance**.

These three letters — **C**, **A**, **P** — each describe a promise your distributed database can make. Let's understand each one.

---

### C — Consistency

**Every node in the cluster always returns the same, up-to-date data.**

If you write a value to Node A, then immediately read from Node B, you will get that same updated value. All nodes are perfectly in sync at all times.

```
  Client writes: user.balance = $500 → Node A

  Client reads from Node B → gets $500  ✅ (Consistent)
  Client reads from Node C → gets $500  ✅ (Consistent)
```

* Think of it as: **"Every node sees the same truth at the same time."**

---

### A — Availability

**Every working node in the system must return a valid response — without throwing an error — even if it cannot communicate with the rest of the cluster.**

This is the strict CAP definition of Availability. It is not just about the system staying "up." It specifically means: a healthy, running node is **not allowed to refuse a request or return an error** just because it lost contact with its peer nodes during a partition.

```
  [ Node A ]  ~~[PARTITION]~~  [ Node B ]
  (healthy)                    (healthy)
       |                            |
  Client asks Node B          Node B cannot reach Node A
                                    |
                     ❌  NOT allowed: "Error — I can't reach Node A"
                     ✅  Must do:    Return the data it has (even if stale)
```

* **The key point**: A working node must always serve a response. It cannot use "I can't reach the other nodes" as an excuse to return an error. The only nodes that are allowed to not respond are nodes that have actually failed or crashed.
* Think of it as: **"Every healthy node must always answer — no matter what is happening inside the cluster."**

---

### P — Partition Tolerance

The system continues to operate even if there is a communication breakdown or network partition between different nodes.

A **network partition** is NOT a node dying. All nodes are healthy and running — the only problem is that the internal network link between some nodes has gone down, so they can no longer communicate with each other.

```
  [ Node A ] ─── [ Node C ]
                      |
               ~~[PARTITION]~~
                      |
                 [ Node B ]
```

A network partition happens that separates Node B from Node A and Node C. Node B can still function and serve requests, but it cannot communicate with Node A or Node C.

---

## The Core Insight: Why You Can Only Pick 2 of 3

Here is the key idea:

> **In any real distributed system, Partition Tolerance (P) is NOT optional.** Networks between nodes WILL fail at some point — it is not a matter of if, but when. So you cannot simply say "I won't support P."

Since **P is forced on you**, the real decision is:

> **"When a partition (internal network failure) happens, do you want your system to stay Consistent or Available?"**

This is why CAP practically becomes a choice between:
* **CP** — Consistency + Partition Tolerance
* **AP** — Availability + Partition Tolerance

---

## Real-World Example 1: Stock Market (CP System)

A stock trading platform shows live stock prices. The cluster has 3 nodes, all holding the current price of a stock.

**Scenario: A partition occurs between Node A and Node B.**

```
  Node A (price = $150)  ~~[PARTITION]~~  Node B (price = $148, stale)
        |                                          |
  Trader 1 reads: $150                   Trader 2 reads: ???
```

**What should Node B do?**

* If Node B responds with $148 (stale) → Trader 2 buys or sells based on a WRONG price. This causes real financial damage.
* If Node B refuses to respond until the partition heals and it gets the latest data → Trader 2 sees a temporary error, but no financial damage is done.

**Decision: The stock market MUST choose Consistency.** Returning wrong data here is dangerous. The system goes **CP** — it sacrifices availability (returns errors temporarily) rather than ever show stale prices.

> Real examples: Financial databases, trading platforms, payment systems — all CP systems.

---

## Real-World Example 2: Instagram Like Count (AP System)

A post on Instagram has a "like" counter. The cluster has 3 nodes, all holding the like count for a post.

**Scenario: A partition occurs between Node A and Node B.**

```
  Node A (likes = 10,248)  ~~[PARTITION]~~  Node B (likes = 10,241, slightly stale)
         |                                           |
  User 1 reads: 10,248                    User 2 reads: 10,241
```

**What should Node B do?**

* If Node B refuses to respond until synced → Millions of users around the world see errors loading Instagram. Terrible experience.
* If Node B responds with 10,241 (7 likes behind) → User 2 sees a slightly stale count. Nobody is hurt. They won't even notice.

**Decision: Instagram chooses Availability.** Showing a like count that is a few seconds behind is completely acceptable. Being unavailable is not. The system goes **AP** — it sacrifices perfect consistency to always stay up.

> Real examples: Social media feeds, YouTube view counts, product review counts, DNS — all AP systems.

---

## What to Choose: CP or AP?

The guiding question is: **"What is worse for your users — wrong data, or no data?"**

---

### Choose CP when: Wrong data causes real damage

If your system returns stale or incorrect data during a partition, it causes financial loss, safety issues, or broken correctness guarantees. In these cases, it is better to go temporarily offline (return an error) than to serve wrong data.

| Real-World System | Why CP? |
| :--- | :--- |
| **Banking / Payments** | If two nodes show different balances, a user could overdraw or a payment could be processed twice. Wrong data = real money lost. |
| **Stock Trading Platform** | A stale price shown to a trader leads to buying/selling at the wrong rate. Milliseconds of wrong data = financial damage. |
| **Inventory Management** | If two nodes both show "1 item left in stock" and both sell it, the product gets oversold. Consistency prevents double-selling. |
| **Distributed Locks / Leader Election** | Systems like Zookeeper elect one "leader" node to coordinate work. If two nodes both think they are the leader at the same time, the entire system breaks. Must be consistent. |
| **Airline Seat Booking** | Two users cannot both book the same seat. The system must confirm a seat is actually available before confirming a booking. |

> **Examples of CP Databases**: Zookeeper, etcd, HBase, traditional relational databases (PostgreSQL, MySQL).

---

### Choose AP when: Being unavailable is worse than showing slightly old data

If your system going offline for even a few seconds causes a terrible user experience or business loss, but showing data that is a few seconds old causes no real harm, then availability is the right choice.

| Real-World System | Why AP? |
| :--- | :--- |
| **Instagram / Twitter Feed** | A post or like count being a few seconds behind is invisible to users. But Instagram going down for millions of people is a disaster. |
| **YouTube View Count** | A video showing 1,000,482 views instead of 1,000,491 causes zero harm. Refusing to load the page does. |
| **Amazon Shopping Cart** | Amazon's own Dynamo system is AP. If two devices both add items during a partition, both carts get merged when it heals. Availability wins over strict consistency. |
| **DNS (Domain Name System)** | DNS propagation takes up to 48 hours worldwide. Different servers may return slightly different IPs during this period. But DNS never goes down — it is the backbone of the internet. |
| **Product Catalog / Prices on E-Commerce** | Showing a price that is 5 seconds old is fine. Showing users a blank product page because nodes are syncing is not. |

> **Examples of AP Databases**: Cassandra, DynamoDB, CouchDB, Riak.