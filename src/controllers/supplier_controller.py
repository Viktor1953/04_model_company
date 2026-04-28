# src/controllers/supplier_controller.py
from src.database.engine import get_session
from src.database.models import Supplier
from src.utils.id_generator import generate_supplier_id


class SupplierController:
    def create_supplier(self, company_name: str, currency: str, distance_km: float, reliability_score: float = 0.85):
        """Создание нового поставщика"""
        supplier_id = generate_supplier_id()
        with get_session() as db:
            supplier = Supplier(
                id=supplier_id,
                company_name=company_name,
                currency=currency,
                distance_km=distance_km,
                reliability_score=reliability_score
            )
            db.add(supplier)
            db.commit()
            return supplier_id

    def get_all_suppliers(self):
        """Получить всех поставщиков"""
        with get_session() as db:
            return db.query(Supplier).all()

    def get_supplier_by_id(self, supplier_id: str):
        """Получить поставщика по ID для редактирования"""
        with get_session() as db:
            return db.query(Supplier).filter(Supplier.id == supplier_id).first()

    def update_supplier(self, supplier_id: str, company_name: str, currency: str, 
                       distance_km: float, reliability_score: float):
        """Обновление данных поставщика"""
        with get_session() as db:
            supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
            if supplier:
                supplier.company_name = company_name
                supplier.currency = currency
                supplier.distance_km = distance_km
                supplier.reliability_score = reliability_score
                db.commit()
                return True
        return False

    def delete_supplier(self, supplier_id: str):
        """Удаление поставщика"""
        with get_session() as db:
            supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
            if supplier:
                db.delete(supplier)
                db.commit()
                return True
        return False

    def clear_all_suppliers(self):
        """Очистка всех поставщиков"""
        with get_session() as db:
            db.query(Supplier).delete()
            db.commit()
            return True