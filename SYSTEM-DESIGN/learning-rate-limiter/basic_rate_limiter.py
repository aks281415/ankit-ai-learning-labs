import time


class RateLimiterPoC:
    def __init__(self):
        # This dictionary simulates what REDIS would store in memory.
        # Format: { "user_id": {"tokens": float, "last_updated": float} }
        self.redis_mock_db = {}

        # Simulated Rules Database (in reality, pulled by workers into local cache)
        self.rules_cache = {
            "free_user":    {"capacity": 5,  "refill_rate_per_sec": 1},
            "premium_user": {"capacity": 20, "refill_rate_per_sec": 5}
        }

    def allow_request(self, user_id):
        """
        This method simulates the EXACT logic that would run inside the Redis Lua Script.
        It must execute Atomically (we simulate that by just making it a synchronous Python function).
        """
        now = time.time()

        # 1. Fetch rules from local cache
        rule = self.rules_cache.get(user_id, self.rules_cache["free_user"])
        capacity = rule["capacity"]
        refill_rate = rule["refill_rate_per_sec"]

        # 2. Fetch current state from "Redis"
        if user_id not in self.redis_mock_db:
            # First time seeing this user: give them a full bucket
            self.redis_mock_db[user_id] = {
                "tokens": capacity,
                "last_updated": now
            }

        state = self.redis_mock_db[user_id]
        current_tokens = state["tokens"]
        last_updated = state["last_updated"]

        # --- THE PRODUCTION SECRET: LAZY REFILL ---
        # We don't have a background process refilling this.
        # We calculate how many tokens they EARNED since they last visited.
        elapsed_time = now - last_updated
        tokens_earned = elapsed_time * refill_rate

        # Add earned tokens, but DO NOT exceed the bucket capacity
        current_tokens = min(capacity, current_tokens + tokens_earned)

        # 3. Check if they have enough tokens to process the request (cost = 1)
        if current_tokens >= 1:
            # Process request: subtract 1 token
            current_tokens -= 1
            allowed = True
        else:
            # Block request
            allowed = False

        # 4. Save the new state back to "Redis"
        self.redis_mock_db[user_id] = {
            "tokens": current_tokens,
            "last_updated": now
        }

        # Format output for the simulation
        status = "[ALLOWED]" if allowed else "[BLOCKED (429)]"
        print(f"[{status}] User: {user_id} | Tokens Left: {current_tokens:.2f}")
        return allowed


# ==========================================
# SIMULATION ENGINE
# ==========================================

if __name__ == "__main__":
    limiter = RateLimiterPoC()

    print("--- SCENARIO 1: The Burst (Free User) ---")
    print("Free user has a capacity of 5. Let's send 7 rapid requests.")
    for i in range(7):
        limiter.allow_request("free_user")
        time.sleep(0.1)  # 100ms between clicks

    print("\n--- SCENARIO 2: Waiting for Refill ---")
    print("User was blocked. Waiting 2.5 seconds...")
    time.sleep(2.5)

    print("Sending 3 rapid requests (they should have earned ~2.5 tokens while waiting).")
    for i in range(3):
        limiter.allow_request("free_user")
        time.sleep(0.1)

    print("\n--- SCENARIO 3: Premium User ---")
    print("Premium user has capacity of 20. They can easily handle this burst.")
    for i in range(7):
        limiter.allow_request("premium_user")
        time.sleep(0.1)
