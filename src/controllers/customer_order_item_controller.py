# src/controllers/customer_order_item_controller.py
from src.database.engine import get_session
from src.database.models import CustomerOrderItem
from sqlalchemy.orm import joinedload


class CustomerOrderItemController:
    def get_items_by_order(self, order_id: str):
        session = get_session()
        try:
            items = session.query(CustomerOrderItem)\
                .options(joinedload(CustomerOrderItem.product))\
                .filter(CustomerOrderItem.order_id == order_id)\
                .all()
            return items
        finally:
            session.close()

    def add_item(self, order_id: str, product_id: str, qty: float) -> bool:
        session = get_session()
        try:
            item = CustomerOrderItem(order_id=order_id, product_id=product_id, qty=qty)
            session.add(item)
            session.commit()
            return True
        except Exception as e:
            print(f"Ошибка добавления позиции: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def update_item(self, item_id: int, qty: float) -> bool:
        session = get_session()
        try:
            item = session.query(CustomerOrderItem).filter(CustomerOrderItem.id == item_id).first()
            if item:
                item.qty = qty
                session.commit()
                return True
            return False
        except Exception as e:
            print(f"Ошибка обновления позиции: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def delete_item(self, item_id: int) -> bool:
        session = get_session()
        try:
            item = session.query(CustomerOrderItem).filter(CustomerOrderItem.id == item_id).first()
            if item:
                session.delete(item)
                session.commit()
                return True
            return False
        except Exception as e:
            print(f"Ошибка удаления позиции: {e}")
            session.rollback()
            return False
        finally:
            session.close()