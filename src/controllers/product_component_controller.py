# src/controllers/product_component_controller.py
from src.database.engine import get_session
from src.database.models import ProductComponent
from src.utils.id_generator import generate_product_component_id


class ProductComponentController:
    def create_component(self, product_id: str, component_name: str, mcr_gu: float,
                        manufacturing_losses_pct: float, scrap_pct: float,
                        uom: str, notes: str = None):
        
        tmc_gu = mcr_gu * (1 + manufacturing_losses_pct/100 + scrap_pct/100)

        component_id = generate_product_component_id()

        with get_session() as db:
            component = ProductComponent(
                id=component_id,
                product_id=product_id,
                component_name=component_name,
                mcr_gu=mcr_gu,
                manufacturing_losses_pct=manufacturing_losses_pct,
                scrap_pct=scrap_pct,
                tmc_gu=round(tmc_gu, 4),
                uom=uom,
                notes=notes
            )
            db.add(component)
            db.commit()
            return component_id

    def get_all_components(self):
        with get_session() as db:
            return db.query(ProductComponent).all()

    def get_component_by_id(self, component_id: str):
        """Получить компонент по ID для редактирования"""
        with get_session() as db:
            return db.query(ProductComponent).filter(ProductComponent.id == component_id).first()

    def update_component(self, component_id: str, component_name: str, mcr_gu: float,
                        manufacturing_losses_pct: float, scrap_pct: float,
                        uom: str, notes: str = None):
        """Обновление существующего компонента"""
        tmc_gu = mcr_gu * (1 + manufacturing_losses_pct/100 + scrap_pct/100)

        with get_session() as db:
            component = db.query(ProductComponent).filter(ProductComponent.id == component_id).first()
            if component:
                component.component_name = component_name
                component.mcr_gu = mcr_gu
                component.manufacturing_losses_pct = manufacturing_losses_pct
                component.scrap_pct = scrap_pct
                component.tmc_gu = round(tmc_gu, 4)
                component.uom = uom
                component.notes = notes
                db.commit()
                return True
        return False

    def delete_component(self, component_id: str):
        with get_session() as db:
            comp = db.query(ProductComponent).filter(ProductComponent.id == component_id).first()
            if comp:
                db.delete(comp)
                db.commit()
                return True
        return False

    def clear_all_components(self):
        with get_session() as db:
            db.query(ProductComponent).delete()
            db.commit()
            return True