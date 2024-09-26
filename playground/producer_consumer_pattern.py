import asyncio

async def producer(queue):
    for i in range(5):
        await asyncio.sleep(1)  # Simulate IO operation
        await queue.put(i)
        print(f"Produced {i}")

async def consumer(queue):
    while True:
        item = await queue.get()
        if item is None:  # Signal to stop consuming
            break
        print(f"Consumed {item}")
        queue.task_done()  # Signal that the item has been processed

async def main():
    queue = asyncio.Queue()

    # Start producer and consumer tasks
    producer_task = asyncio.create_task(producer(queue))
    consumer_task = asyncio.create_task(consumer(queue))

    # Wait for the producer to finish
    await producer_task

    # Signal the consumer to stop after the producer is done
    await queue.put(None)

    # Wait for the consumer to finish
    await consumer_task

# Run the event loop
asyncio.run(main())
