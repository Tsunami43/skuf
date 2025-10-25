"""
Microservice Example - Service Communication
Demonstrates microservice architecture with dependency injection.
"""
import asyncio
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from skuf.dependency import Dependency


# Data Models
@dataclass
class Order:
    id: str
    customer_id: str
    items: List[Dict[str, Any]]
    total: float
    status: str
    created_at: datetime


@dataclass
class Customer:
    id: str
    name: str
    email: str
    credit_limit: float


# Services
class OrderService:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self._orders = []
    
    async def create_order(self, customer_id: str, items: List[Dict[str, Any]]) -> Order:
        order_id = f"order-{len(self._orders) + 1}"
        total = sum(item.get('price', 0) * item.get('quantity', 1) for item in items)
        
        order = Order(
            id=order_id,
            customer_id=customer_id,
            items=items,
            total=total,
            status="pending",
            created_at=datetime.now()
        )
        
        self._orders.append(order)
        print(f"📦 Created order {order_id} for customer {customer_id}")
        return order
    
    async def get_order(self, order_id: str) -> Optional[Order]:
        return next((o for o in self._orders if o.id == order_id), None)


class CustomerService:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self._customers = [
            Customer("cust-1", "Alice Johnson", "alice@example.com", 1000.0),
            Customer("cust-2", "Bob Smith", "bob@example.com", 500.0),
        ]
    
    async def get_customer(self, customer_id: str) -> Optional[Customer]:
        return next((c for c in self._customers if c.id == customer_id), None)
    
    async def check_credit_limit(self, customer_id: str, amount: float) -> bool:
        customer = await self.get_customer(customer_id)
        if not customer:
            return False
        return amount <= customer.credit_limit


class PaymentService:
    def __init__(self, gateway_url: str):
        self.gateway_url = gateway_url
    
    async def process_payment(self, customer_id: str, amount: float) -> bool:
        print(f"💳 Processing payment for customer {customer_id}: ${amount}")
        await asyncio.sleep(0.5)  # Simulate payment processing
        
        # Simulate 95% success rate
        success = True  # In real app, this would call payment gateway
        if success:
            print(f"✅ Payment successful: ${amount}")
        else:
            print(f"❌ Payment failed: ${amount}")
        
        return success


class InventoryService:
    def __init__(self, warehouse_url: str):
        self.warehouse_url = warehouse_url
        self._inventory = {
            "laptop": 10,
            "mouse": 50,
            "keyboard": 25,
        }
    
    async def check_stock(self, item_name: str, quantity: int) -> bool:
        available = self._inventory.get(item_name, 0)
        print(f"📦 Checking stock for {item_name}: {available} available, {quantity} needed")
        return available >= quantity
    
    async def reserve_items(self, items: List[Dict[str, Any]]) -> bool:
        for item in items:
            name = item.get('name', '')
            quantity = item.get('quantity', 1)
            if not await self.check_stock(name, quantity):
                return False
        
        # Reserve items
        for item in items:
            name = item.get('name', '')
            quantity = item.get('quantity', 1)
            self._inventory[name] -= quantity
            print(f"🔒 Reserved {quantity} {name}")
        
        return True


class NotificationService:
    def __init__(self, sms_url: str, email_url: str):
        self.sms_url = sms_url
        self.email_url = email_url
    
    async def send_order_confirmation(self, customer_id: str, order_id: str):
        print(f"📧 Sending order confirmation to customer {customer_id} for order {order_id}")
        await asyncio.sleep(0.2)
    
    async def send_payment_notification(self, customer_id: str, amount: float):
        print(f"💰 Sending payment notification to customer {customer_id}: ${amount}")
        await asyncio.sleep(0.2)


class Logger:
    def __init__(self, service_name: str):
        self.service_name = service_name
    
    def info(self, message: str):
        print(f"[INFO] {self.service_name}: {message}")
    
    def error(self, message: str):
        print(f"[ERROR] {self.service_name}: {message}")


# Business Logic
class OrderOrchestrator:
    def __init__(self, order_service: OrderService, customer_service: CustomerService,
                 payment_service: PaymentService, inventory_service: InventoryService,
                 notification_service: NotificationService, logger: Logger):
        self.order_service = order_service
        self.customer_service = customer_service
        self.payment_service = payment_service
        self.inventory_service = inventory_service
        self.notification_service = notification_service
        self.logger = logger
    
    async def process_order(self, customer_id: str, items: List[Dict[str, Any]]) -> Optional[Order]:
        self.logger.info(f"Processing order for customer {customer_id}")
        
        # 1. Check customer exists
        customer = await self.customer_service.get_customer(customer_id)
        if not customer:
            self.logger.error(f"Customer {customer_id} not found")
            return None
        
        # 2. Check inventory
        if not await self.inventory_service.reserve_items(items):
            self.logger.error("Insufficient inventory")
            return None
        
        # 3. Create order
        order = await self.order_service.create_order(customer_id, items)
        
        # 4. Process payment
        if not await self.payment_service.process_payment(customer_id, order.total):
            self.logger.error(f"Payment failed for order {order.id}")
            return None
        
        # 5. Update order status
        order.status = "confirmed"
        
        # 6. Send notifications
        await self.notification_service.send_order_confirmation(customer_id, order.id)
        await self.notification_service.send_payment_notification(customer_id, order.total)
        
        self.logger.info(f"Order {order.id} processed successfully")
        return order


# Setup Dependencies
def setup_dependencies():
    Dependency.register(OrderService, instance=OrderService("postgresql://localhost/orders"))
    Dependency.register(CustomerService, instance=CustomerService("postgresql://localhost/customers"))
    Dependency.register(PaymentService, instance=PaymentService("https://payment-gateway.com"))
    Dependency.register(InventoryService, instance=InventoryService("https://warehouse.com"))
    Dependency.register(NotificationService, instance=NotificationService("https://sms.com", "https://email.com"))
    Dependency.register(Logger, instance=Logger("order-orchestrator"))


# Main Application
async def main():
    """Main microservice application"""
    print("🚀 Starting Microservice Example")
    
    # Setup dependencies
    setup_dependencies()
    
    # Get orchestrator
    @Dependency.inject
    def get_orchestrator(order_service: Dependency[OrderService], 
                        customer_service: Dependency[CustomerService],
                        payment_service: Dependency[PaymentService],
                        inventory_service: Dependency[InventoryService],
                        notification_service: Dependency[NotificationService],
                        logger: Dependency[Logger]):
        return OrderOrchestrator(order_service, customer_service, payment_service,
                               inventory_service, notification_service, logger)
    
    orchestrator = get_orchestrator()
    
    # Process sample orders
    sample_orders = [
        {
            "customer_id": "cust-1",
            "items": [{"name": "laptop", "price": 999.99, "quantity": 1}]
        },
        {
            "customer_id": "cust-2", 
            "items": [{"name": "mouse", "price": 29.99, "quantity": 2}]
        }
    ]
    
    for order_data in sample_orders:
        order = await orchestrator.process_order(
            order_data["customer_id"], 
            order_data["items"]
        )
        if order:
            print(f"✅ Order processed: {order.id} - ${order.total}")
        else:
            print("❌ Order failed")
    
    print("🎉 Microservice example completed!")


if __name__ == "__main__":
    asyncio.run(main())
