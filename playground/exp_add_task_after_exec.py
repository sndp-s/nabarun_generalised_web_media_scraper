import asyncio

# async def worker(i):
#     print(f"worker {i} running")
#     await asyncio.sleep(1)
#     print(f"worker {i} completed")

# async def workerr(q, r):
#     print(f"workerr {r} running")
#     await asyncio.sleep(1)
#     print(f"workerr {r} completed")
#     await q.task_done()

# async def manager(q):
#     a = 9
#     # while not q.empty():
#     while a != 0:
#         r = q.get()
#         if not r:
#             print("---completed---")
#             break
#         asyncio.create_task(workerr(q, await r))
#         a -= 1

# async def main():
#     # Create q, Add initial set of tasks to the q
#     tasks = [1]
#     q = asyncio.Queue()
#     for task in tasks:
#         await q.put(task)

#     # Spawn the manager background task
#     await manager(q)

#     # Wait until the queue is empty
#     await q.join()

# if __name__ == "__main__":
#     asyncio.run(main())


# #########################################

# data = [100,200,300,400,500,600]

# async def workerr(q, r):
#     print(f"workerr {r} running")
#     await asyncio.sleep(1)
#     await q.put(data.pop(0) if data else None)
#     print(f"workerr {r} completed")
#     # import pdb; pdb.set_trace();
#     q.task_done()

# async def manager(q):
#     while True:
#         r = await q.get()
#         if not r:
#             print("---completed---")
#             break
#         asyncio.create_task(workerr(q, r))
#         await asyncio.sleep(0)

# async def main():
#     # Create q, Add initial set of tasks to the q
#     tasks = [1,2,3]
#     q = asyncio.Queue()
#     for task in tasks:
#         await q.put(task)

#     manager_task = asyncio.create_task(manager(q))

#     await q.join()

#     await q.put(None)

#     await manager_task

# if __name__ == "__main__":
#     asyncio.run(main())



# ######################

# import asyncio

# data = [100, 200, 300, 400, 500, 600]

# async def workerr(q, r):
#     print(f"workerr {r} running")
#     await asyncio.sleep(1)  # Simulating I/O operation
#     if data:
#         await q.put(data.pop(0))  # Add new task if data exists
#     else:
#         await q.put(None)  # Signal completion when data is exhausted
#     print(f"workerr {r} completed")
#     q.task_done()

# async def manager(q):
#     while True:
#         r = await q.get()  # Get a task from the queue
#         if r is None:  # If we received a None, we know we should stop
#             print("---completed---")
#             break
#         asyncio.create_task(workerr(q, r))  # Create a new worker task
#         await asyncio.sleep(0)

# async def main():
#     # Create the task queue and add initial set of tasks to the queue
#     q = asyncio.Queue()
#     for task in [1, 2, 3]:  # Initial tasks
#         await q.put(task)

#     # Start the manager task
#     manager_task = asyncio.create_task(manager(q))

#     # Wait until the queue is empty
#     await q.join()  # Wait for all tasks in the queue to be marked as done

#     # Now we need to signal the manager to stop
#     await q.put(None)  # Add a sentinel value to signal completion

#     # Wait for the manager to finish
#     await manager_task

# if __name__ == "__main__":
#     asyncio.run(main())


##########################################


import asyncio
from random import randint
import time

async def worker(task_queue, seen_urls, max_depth):
    """Worker coroutine that processes tasks from the task queue."""
    while True:
        # Get the next task from the queue (blocking call)
        task = await task_queue.get()
        
        # Unpack the task (URL, current depth)
        url, depth = task
        
        # If the max depth is reached, we stop processing this task
        if depth >= max_depth:
            print(f"Reached max depth at {url}")
            task_queue.task_done()
            continue

        # Process the URL (fake scraping task)
        await process_url(url)
        
        # Simulate discovering new URLs (new tasks)
        new_urls = [f"{url}/page{i}" for i in range(randint(1, 4))]  # Fake sub-URLs
        for new_url in new_urls:
            if new_url not in seen_urls:  # Avoid revisiting the same URL
                seen_urls.add(new_url)
                print(f"Discovered new URL: {new_url}, depth {depth + 1}")
                await task_queue.put((new_url, depth + 1))  # Schedule new task
        
        # Mark the task as done in the queue
        task_queue.task_done()

async def process_url(url):
    """Simulate processing the URL (fake scraping)."""
    print(f"Processing {url}")
    await asyncio.sleep(randint(1, 3))  # Simulate network delay or processing time

async def main(seed_urls, max_depth, num_workers=5):
    task_queue = asyncio.Queue()  # A queue to store the tasks (URLs)
    seen_urls = set()  # A set to track seen URLs to avoid revisits

    # Populate the queue with seed URLs
    for url in seed_urls:
        seen_urls.add(url)
        await task_queue.put((url, 0))  # Each task is (URL, depth)
    
    # Create a set of worker tasks (coroutines)
    workers = [asyncio.create_task(worker(task_queue, seen_urls, max_depth)) for _ in range(num_workers)]

    # Wait until all tasks in the queue are processed
    await task_queue.join()

    # Once all tasks are done, cancel the worker tasks
    for w in workers:
        w.cancel()

    # Wait until all worker tasks have finished (clean shutdown)
    await asyncio.gather(*workers, return_exceptions=True)

if __name__ == "__main__":
    seed_urls = ["http://example.com", "http://another.com", "http://site.com"]
    max_depth = 3  # Stop after reaching this depth

    start_time = time.perf_counter()
    asyncio.run(main(seed_urls, max_depth))
    elapsed = time.perf_counter() - start_time
    print(f"Completed in {elapsed:0.2f} seconds")
