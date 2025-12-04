from typing import Type, TypeVar, List, Optional, Generic
from sqlmodel import Session, SQLModel, select

T = TypeVar("T", bound=SQLModel)

class BaseRepository(Generic[T]):
    def __init__(self, session: Session, model: Type[T]):
        self.session = session
        self.model = model

    def get_all(self) -> List[T]:
        # Busca solo los activos (Herencia pura)
        statement = select(self.model).where(getattr(self.model, "activo") == True)
        return self.session.exec(statement).all()

    def get_by_id(self, id: int) -> Optional[T]:
        return self.session.get(self.model, id)

    def create(self, item: T) -> T:
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def soft_delete(self, id: int) -> bool:
        item = self.get_by_id(id)
        if item:
            item.activo = False # type: ignore
            self.session.add(item)
            self.session.commit()
            return True
        return False