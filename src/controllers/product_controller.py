# src/controllers/product_controller.py
from src.database.engine import get_session
from src.database.models import Product
from src.utils.id_generator import generate_product_id


class ProductController:
    def get_all_products(self):
        session = get_session()
        try:
            return session.query(Product).all()
        finally:
            session.close()

    def get_by_id(self, product_id: str):
        session = get_session()
        try:
            return session.query(Product).filter(Product.id == product_id).first()
        finally:
            session.close()

    def create_product(self, name: str, uom: str, unit_price: float, currency: str) -> bool:
        session = get_session()
        try:
            prod_id = generate_product_id()
            product = Product(
                id=prod_id,
                name=name,
                uom=uom,
                unit_price=unit_price,
                currency=currency
            )
            session.add(product)
            session.commit()
            return True
        except Exception as e:
            print(f"Ошибка создания изделия: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def get_product_by_id(self, product_id: str):
        """Получить изделие по ID для редактирования"""
        with get_session() as db:
            return db.query(Product).filter(Product.id == product_id).first()

    def update_product(self, product_id: str, name: str, uom: str, unit_price: float, currency: str):
        """Обновление данных изделия"""
        with get_session() as db:
            product = db.query(Product).filter(Product.id == product_id).first()
            if product:
                product.name = name
                product.uom = uom
                product.unit_price = unit_price
                product.currency = currency
                db.commit()
                return True
        return False

    def delete_product(self, product_id: str) -> bool:
        session = get_session()
        try:
            product = session.query(Product).filter(Product.id == product_id).first()
            if product:
                session.delete(product)
                session.commit()
                return True
            return False
        except Exception as e:
            print(f"Ошибка удаления изделия: {e}")
            session.rollback()
            return False
        finally:
            session.close()