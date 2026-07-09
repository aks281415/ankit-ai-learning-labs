import time
import queue
import threading

NUM_EMAILS = 10
EMAIL_SEND_TIME = 0.5


def send_newsletter_sync():
    """
    Simulates a synchronous API endpoint that sends emails one by one.
    The admin (the person who clicked 'Send Newsletter') is blocked until it is completely finished.
    """
    print("[Sync API] Admin clicked 'Send Newsletter' to 10 subscribers.")
    start_time = time.time()

    for i in range(1, NUM_EMAILS + 1):
        print(f"  [Sync API] Sending email {i} to subscriber...")
        time.sleep(EMAIL_SEND_TIME)

    end_time = time.time()
    print(
        f"[Sync API] Done! The admin was frozen on the loading screen for "
        f"{end_time - start_time:.2f} seconds."
    )


email_queue = queue.Queue()


def email_worker(worker_id):
    """
    A background server whose only job is to watch the queue and send emails.
    """
    while True:
        job = email_queue.get()

        if job is None:
            break

        print(
            f"  [Worker {worker_id}] Picked up '{job}' from queue... sending email."
        )
        time.sleep(EMAIL_SEND_TIME)
        email_queue.task_done()


def send_newsletter_async():
    """
    Simulates an asynchronous API endpoint. It just dumps jobs in the queue and replies immediately.
    """
    print("[Async API] Admin clicked 'Send Newsletter' to 10 subscribers.")
    start_time = time.time()

    for i in range(1, NUM_EMAILS + 1):
        email_queue.put(f"Email Job #{i}")

    end_time = time.time()
    print(
        f"[Async API] Success! Responded to admin in "
        f"{end_time - start_time:.4f} seconds."
    )
    print(
        "[Async API] The admin can now close the browser while "
        "the servers work in the background.\n"
    )


if __name__ == "__main__":
    """
    Main execution block to run both scenarios and compare blocking vs non-blocking behavior.
    """
    print("=== SCENARIO 1: The Monolith (Synchronous) ===")
    send_newsletter_sync()

    print("\n" + "=" * 50 + "\n")

    print("=== SCENARIO 2: The Distributed System (Asynchronous) ===")

    threading.Thread(
        target=email_worker,
        args=("A",),
        daemon=True
    ).start()

    threading.Thread(
        target=email_worker,
        args=("B",),
        daemon=True
    ).start()

    send_newsletter_async()

    email_queue.join()

    print(
        "\n[System] All emails have finally been sent by the background workers."
    )