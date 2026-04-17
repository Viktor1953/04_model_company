# src/controllers/customer_order_controller.py
from datetime import date
from src.database.engine import get_session
from src.database.models import CustomerOrder, CustomerOrderItem, Product
from src.utils.id_generator import generate_order_id


class CustomerOrderController:
    def get_all_orders(self):
        session = get_session()
        try:
            return session.query(CustomerOrder).all()
        finally:
            session.close()

    def get_order_by_id(self, order_id: str):
        session = get_session()
        try:
            return session.query(CustomerOrder).filter(CustomerOrder.id == order_id).first()
        finally:
            session.close()

    def create_order(self, customer_id: str, currency: str = "USD", 
                    discount_percent: float = 0.0, status: str = "Quotation",
                    advance_percent: float = 0.0, advance_deadline_days: int = 14,
                    final_payment_days: int = 30, risk_late_payment_days: int = 7,
                    order_date: date = None) -> str:   # возвращаем order_id
        
        if order_date is None:
            order_date = date.today()

        session = get_session()
        try:
            order_id = generate_order_id()
            
            order = CustomerOrder(
                id=order_id,
                order_date=order_date,
                customer_id=customer_id,
                currency=currency,
                discount_percent=discount_percent,
                status=status,
                advance_percent=advance_percent,
                advance_deadline_days=advance_deadline_days,
                final_payment_days=final_payment_days,
                risk_late_payment_days=risk_late_payment_days
            )
            
            session.add(order)
            session.commit()
            return order_id
        except Exception as e:
            print(f"Ошибка создания заказа: {e}")
            session.rollback()
            return None
        finally:
            session.close()

    # ... остальные методы остаются без изменений (update, delete)
    def update_order(self, order_id: str, **kwargs) -> bool:
        session = get_session()
        try:
            order = session.query(CustomerOrder).filter(CustomerOrder.id == order_id).first()
            if not order:
                return False

            for key, value in kwargs.items():
                if hasattr(order, key):
                    setattr(order, key, value)

            session.commit()
            return True
        except Exception as e:
            print(f"Ошибка обновления заказа: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def delete_order(self, order_id: str) -> bool:
        session = get_session()
        try:
            order = session.query(CustomerOrder).filter(CustomerOrder.id == order_id).first()
            if order:
                session.delete(order)
                session.commit()
                return True
            return False
        except Exception as e:
            print(f"Ошибка удаления заказа: {e}")
            session.rollback()
            return False
        finally:
            session.close()