# src/controllers/customer_controller.py
from src.database.engine import get_session
from src.database.models import Customer
from src.utils.id_generator import generate_customer_id


class CustomerController:
    def get_all_customers(self):
        session = get_session()
        try:
            return session.query(Customer).all()
        finally:
            session.close()

    def get_by_id(self, customer_id: str):
        session = get_session()
        try:
            return session.query(Customer).filter(Customer.id == customer_id).first()
        finally:
            session.close()

    def create_customer(self, company: str, distance_km: float) -> bool:
        session = get_session()
        try:
            cust_id = generate_customer_id()
            customer = Customer(id=cust_id, company=company, distance_km=distance_km)
            session.add(customer)
            session.commit()
            return True
        except Exception as e:
            print(f"Ошибка создания клиента: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def update_customer(self, customer_id: str, company: str, distance_km: float):
        """Обновление данных клиента"""
        with get_session() as db:
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            if customer:
                customer.company = company
                customer.distance_km = distance_km
                db.commit()
                return True
        return False

    def get_customer_by_id(self, customer_id: str):
        """Получить клиента по ID"""
        with get_session() as db:
            return db.query(Customer).filter(Customer.id == customer_id).first()

    def delete_customer(self, customer_id: str) -> bool:
        session = get_session()
        try:
            customer = session.query(Customer).filter(Customer.id == customer_id).first()
            if customer:
                session.delete(customer)
                session.commit()
                return True
            return False
        except Exception as e:
            print(f"Ошибка удаления клиента: {e}")
            session.rollback()
            return False
        finally:
            session.close()