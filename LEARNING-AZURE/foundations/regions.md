# Azure Global Infrastructure — Regions, Availability Zones & Region Pairs

---

## Why Regions Exist

If all Azure servers were in one country, every user elsewhere would face high latency, no fault isolation, and compliance risks. Microsoft solves this by distributing infrastructure globally into **Regions**.

---

## Region

> A **Region** is a geographical area containing one or more datacenters connected via a low-latency network. Azure has **60+ regions** worldwide.

**How to pick a region — 4 factors:**

| Factor | What to consider |
|---|---|
| **Latency** | Deploy close to your users |
| **Compliance** | Data residency laws (GDPR, DPDP, HIPAA) |
| **Cost** | Pricing varies by region — check Azure Pricing Calculator |
| **Service Availability** | Not every service is in every region |

---

## Availability Zones (AZ)

> An **AZ** is a physically separate, independent datacenter **within** a Region — with its own power, cooling, and networking.

Zones within a region are connected via private fibre. Microsoft's inter-zone latency target is **< 2 ms** (performance target, not a contractual SLA).

```mermaid
graph TD
    subgraph Region ["Central India Region"]
        Z1["Zone 1\nDatacenter A\n⚡ ❄️ 🌐"]
        Z2["Zone 2\nDatacenter B\n⚡ ❄️ 🌐"]
        Z3["Zone 3\nDatacenter C\n⚡ ❄️ 🌐"]
        Z1 <-->|"< 2ms"| Z2
        Z2 <-->|"< 2ms"| Z3
    end
```

> Zone numbers are **logical, not physical** — "Zone 1" in your subscription may map to a different datacenter than another subscription's "Zone 1". This distributes load across facilities.

### Single-Zone vs Multi-Zone

```mermaid
graph TD
    subgraph BAD ["❌ Single Zone — No HA"]
        LB1["Load Balancer"] --> VM1["VM-1\nZone 1"]
        FAIL["Zone 1 Fails"] -.->|"App goes down"| VM1
    end

    subgraph GOOD ["✅ Multi Zone — High Availability"]
        LB2["Load Balancer\nZone-redundant"]
        LB2 --> VM2["VM-1\nZone 1"]
        LB2 --> VM3["VM-2\nZone 2"]
        LB2 --> VM4["VM-3\nZone 3"]
    end
```

**What AZs protect against:**

| Failure | Protected? |
|---|:---:|
| Single datacenter power/network/fire | ✅ |
| Entire region going down | ❌ |

---

## Region Pair

> A **Region Pair** is two Azure regions in the same geography linked for disaster recovery. Microsoft prefers ~300 miles (480 km) separation — but this is a guideline, not a hard rule.

| Primary | Paired |
|---|---|
| Central India | South India |
| East US | West US |
| North Europe | West Europe |

**Why it matters:**
- Microsoft never updates both regions in a pair simultaneously
- In a declared disaster, Azure prioritises recovering at least one region in each pair

**DR in practice:**

```mermaid
flowchart LR
    A["Central India ✅\n(Primary Active)"] -->|"Async replication"| B["South India 🟡\n(Standby)"]
    C["Central India ❌\n(Disaster)"] -->|"DNS Failover"| D["South India ✅\n(Now Active)"]
```

- **RTO** — how fast must the system recover?
- **RPO** — how much data loss is acceptable?

---

## AZ vs Region Pair — Quick Comparison

| | Availability Zone | Region Pair |
|---|---|---|
| **Protects against** | Datacenter failure | Regional failure |
| **Distance** | Within ~100 km | ~480 km (guideline) |
| **Latency** | < 2 ms | 20–100+ ms |
| **Failover** | Automatic (with LB) | Manual / Azure Site Recovery |
| **Use case** | High Availability | Disaster Recovery |
| **VM SLA** | 99.99% | Business continuity |

---

## Architecture Options

| Option | Setup | HA | DR | Cost |
|---|---|:---:|:---:|:---:|
| A | 1 VM · 1 Zone | ❌ | ❌ | $ |
| B | Multi-VM · Multi-Zone | ✅ | ❌ | $$ |
| C | Multi-Zone + Region Pair | ✅ | ✅ | $$$ |

> Production minimum = **Option B**. Mission-critical = **Option C**.

---

## Key Takeaways

```
Region           = Deployment location (60+ worldwide)
Availability Zone = Independent DC within a region → protects against DC failure
Region Pair      = Two regions linked for DR → protects against regional failure
```

- Deploy across **multiple zones** → high availability (up to 99.99% SLA)
- Use **region pairs** → disaster recovery
- Region choice affects latency, compliance, cost, and service availability
