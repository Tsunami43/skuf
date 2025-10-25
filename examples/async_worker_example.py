"""
Async Worker Example - Background Task Processing
Demonstrates async task processing with dependency injection.
"""
import asyncio
import random
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from skuf.dependency import Dependency


# Data Models
@dataclass
class Task:
    id: str
    name: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    result: Any = None


# Services
class TaskQueue:
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._queue = []
        self._completed = []
    
    async def add_task(self, task: Task):
        if len(self._queue) >= self.max_size:
            raise Exception("Queue is full")
        self._queue.append(task)
        print(f"📥 Added task {task.id} to queue")
    
    async def get_next_task(self) -> Optional[Task]:
        if not self._queue:
            return None
        return self._queue.pop(0)
    
    async def mark_completed(self, task: Task, result: Any):
        task.status = "completed"
        task.completed_at = datetime.now()
        task.result = result
        self._completed.append(task)
        print(f"✅ Task {task.id} completed")


class DatabaseService:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self._tasks = []
    
    async def save_task(self, task: Task):
        self._tasks.append(task)
        print(f"💾 Saved task {task.id} to database")
    
    async def get_task_history(self) -> List[Task]:
        return self._tasks


class EmailService:
    def __init__(self, smtp_host: str):
        self.smtp_host = smtp_host
    
    async def send_notification(self, to: str, subject: str, body: str):
        print(f"📧 Sending email to {to} via {self.smtp_host}")
        print(f"   Subject: {subject}")
        print(f"   Body: {body}")
        await asyncio.sleep(0.1)  # Simulate email sending


class Logger:
    def __init__(self, name: str):
        self.name = name
    
    def info(self, message: str):
        print(f"[INFO] {self.name}: {message}")
    
    def error(self, message: str):
        print(f"[ERROR] {self.name}: {message}")


# Business Logic
class TaskProcessor:
    def __init__(self, queue: TaskQueue, db: DatabaseService, email: EmailService, logger: Logger):
        self.queue = queue
        self.db = db
        self.email = email
        self.logger = logger
    
    async def process_task(self, task: Task):
        self.logger.info(f"Processing task {task.id}: {task.name}")
        
        # Simulate work
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        # Simulate success/failure
        if random.random() > 0.1:  # 90% success rate
            result = f"Task {task.id} completed successfully"
            await self.queue.mark_completed(task, result)
            await self.db.save_task(task)
            await self.email.send_notification(
                to="admin@example.com",
                subject="Task Completed",
                body=f"Task {task.id} has been completed successfully."
            )
        else:
            self.logger.error(f"Task {task.id} failed")
            task.status = "failed"
            await self.db.save_task(task)


class WorkerService:
    def __init__(self, processor: TaskProcessor, logger: Logger):
        self.processor = processor
        self.logger = logger
        self.is_running = False
    
    async def start_worker(self):
        self.is_running = True
        self.logger.info("🚀 Worker started")
        
        while self.is_running:
            task = await self.processor.queue.get_next_task()
            if task:
                await self.processor.process_task(task)
            else:
                await asyncio.sleep(1)  # Wait for new tasks
    
    def stop_worker(self):
        self.is_running = False
        self.logger.info("🛑 Worker stopped")


# Setup Dependencies
def setup_dependencies():
    Dependency.register(TaskQueue, instance=TaskQueue(max_size=100))
    Dependency.register(DatabaseService, instance=DatabaseService("postgresql://localhost/worker"))
    Dependency.register(EmailService, instance=EmailService("smtp.gmail.com"))
    Dependency.register(Logger, instance=Logger("worker"))


# Main Application
async def main():
    """Main application with async worker"""
    print("🚀 Starting Async Worker Example")
    
    # Setup dependencies
    setup_dependencies()
    
    # Get services
    @Dependency.inject
    def get_processor(queue: Dependency[TaskQueue], db: Dependency[DatabaseService], 
                     email: Dependency[EmailService], logger: Dependency[Logger]):
        return TaskProcessor(queue, db, email, logger)
    
    @Dependency.inject
    def get_worker(processor: Dependency[TaskProcessor], logger: Dependency[Logger]):
        return WorkerService(processor, logger)
    
    processor = get_processor()
    worker = get_worker()
    
    # Add some sample tasks
    tasks = [
        Task("task-1", "Process payment", "pending", datetime.now()),
        Task("task-2", "Send email", "pending", datetime.now()),
        Task("task-3", "Generate report", "pending", datetime.now()),
    ]
    
    for task in tasks:
        await processor.queue.add_task(task)
    
    # Start worker in background
    worker_task = asyncio.create_task(worker.start_worker())
    
    # Let it run for a bit
    await asyncio.sleep(5)
    
    # Stop worker
    worker.stop_worker()
    await worker_task
    
    print("🎉 Worker example completed!")


if __name__ == "__main__":
    asyncio.run(main())
