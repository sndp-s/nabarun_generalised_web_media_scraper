import logging
import asyncio
import random


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('greedy_workers_model.log', mode='w')
    ]
)
logger = logging.getLogger("greedy_workers_model")


class Machine:
    def __init__(self):
        logger.debug("Initialising the Machine")

        # setup task queue
        self.queue = asyncio.Queue()
        self.max_workers = 5
        self.next_tasks = ['A', 'B', 'C', 'D', 'E']

        logger.debug("Machine initialised")

    async def simulate_async_work(self):
        delay = random.uniform(1, 5)
        logger.debug(f"Starting work, will take {delay:.2f} seconds...")
        await asyncio.sleep(delay)

        if self.next_tasks:
            if random.random() < 0.5:
                element = self.next_tasks.pop(0)
                await self.queue.put(element)
                logger.debug(f"Added {element} to the queue from next_tasks.")
            else:
                logger.debug("No element added to the queue this time.")
        else:
            logger.debug("No more elements in next_tasks to add to the queue.")

        logger.debug("Work finished.")

    async def worker(self, worker_id):
        logger.debug("Worker %s spawned", worker_id)

        while True:
            # obtain a task
            task = await self.queue.get()
            logger.debug("Task %s fetched by worker %s for processing",
                         task, worker_id)

            # simulate async work done
            logger.debug("Simulating work in worker %s", worker_id)
            await self.simulate_async_work()

            # mark task completed
            logger.debug(
                "Worker %s marking task %s as done in the task queue", worker_id, task)
            self.queue.task_done()

    async def run(self):
        logger.debug("Running the machine")

        # populate queue with init set of tasks
        logger.debug("Populating queue with initial tasks")
        for i in range(3):
            await self.queue.put(i)
            logger.debug("Task %s added to the task queue task", i)

        # init workers
        logger.debug("Initialising workers")
        workers = [asyncio.create_task(self.worker(f"worker_{i}"))
                   for i in range(self.max_workers)]

        # await until the task queue is empty
        logger.debug("Waiting for task queue to be empty")
        await self.queue.join()

        # cancel workers one by one
        logger.debug("Cancelling workers")
        for worker in workers:
            worker.cancel()

        # await clean cancellation
        logger.debug("Awaiting clean cancellation")


# NOTE :: Although things work as required, this is a very hacky way to organise a cooperative multitasking system
# NOTE :: Proceeding with this at the moment inorder to progress with other aspects of the project.
if __name__ == "__main__":
    machine = Machine()
    asyncio.run(machine.run())
