"""Abstract Base Repository Paradigm.

Provides an enterprise-grade, fully typed generic repository implementation 
leveraging SQLAlchemy 2.x Asynchronous APIs. Encapsulates query compilation,
transaction boundaries, isolation protections, and unified error handling.
"""

import logging
from collections.abc import Sequence
from typing import Any, Generic, TypeVar, Any as GenericRow
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, text, exc
from sqlalchemy.engine import Result

from database.base import Base

logger = logging.getLogger("investment_platform.repositories.base")

# Generic Type Bound matching our declarative base schema layer
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic CRUD and Advanced Query Abstraction Layer for PostgreSQL.

    Encapsulates all standard interaction vectors for any model entity while
    maintaining strict computational type safety.
    """

    def __init__(self, model: type[ModelType], session: AsyncSession) -> None:
        """Initializes the generic repository wrapper.

        Args:
            model: The explicit target SQLAlchemy model class type.
            session: The active asynchronous transactional database context.
        """
        self.model = model
        self.session = session

    async def create(self, data: dict[str, Any], auto_commit: bool = False) -> ModelType:
        """Instantiates and persists a singular record entity within the transaction.

        Args:
            data: Explicit keyword mapping payload corresponding to model columns.
            auto_commit: Forces an immediate transaction flush checkpoint block if True.
        """
        try:
            instance = self.model(**data)
            self.session.add(instance)
            if auto_commit:
                await self.commit()
                await self.refresh(instance)
            else:
                await self.flush()
            return instance
        except exc.SQLAlchemyError as error:
            logger.error(f"Persistence creation execution trace error on {self.model.__name__}: {error}")
            await self.rollback()
            raise error

    async def bulk_create(self, data_list: list[dict[str, Any]], auto_commit: bool = False) -> list[ModelType]:
        """Executes optimized vectorized insertion sequences for massive record sets.

        Args:
            data_list: Collection arrays containing raw mapping payloads.
            auto_commit: Forces transaction completion block on immediate termination if True.
        """
        try:
            instances = [self.model(**data) for data in data_list]
            self.session.add_all(instances)
            if auto_commit:
                await self.commit()
            else:
                await self.flush()
            return instances
        except exc.SQLAlchemyError as error:
            logger.error(f"Bulk persistence failure sequence on {self.model.__name__}: {error}")
            await self.rollback()
            raise error

    async def get_by_id(self, record_id: int | str) -> ModelType | None:
        """Fetches a singular record instance matching an explicit primary key target index."""
        try:
            return await self.session.get(self.model, record_id)
        except exc.SQLAlchemyError as error:
            logger.error(f"Lookup validation failure on {self.model.__name__} for ID {record_id}: {error}")
            raise error

    async def get_one(self, **filters: Any) -> ModelType | None:
        """Evaluates strict equals predicates returning an isolated model record or None."""
        try:
            statement = select(self.model).filter_by(**filters).limit(1)
            result: Result = await self.session.execute(statement)
            return result.scalar_or_none()
        except exc.SQLAlchemyError as error:
            logger.error(f"Query sequence restriction exception on {self.model.__name__}: {error}")
            raise error

    async def get_all(self) -> Sequence[ModelType]:
        """Extracts all active rows matching the table entity description safely."""
        try:
            statement = select(self.model)
            result: Result = await self.session.execute(statement)
            return result.scalars().all()
        except exc.SQLAlchemyError as error:
            logger.error(f"Universal selection trace failure on {self.model.__name__}: {error}")
            raise error

    async def find(self, clause: Any) -> Sequence[ModelType]:
        """Accepts explicit complex binary expression statements to query targets.

        Args:
            clause: An explicit SQLAlchemy expression clause object (e.g., User.balance > 100).
        """
        try:
            statement = select(self.model).where(clause)
            result: Result = await self.session.execute(statement)
            return result.scalars().all()
        except exc.SQLAlchemyError as error:
            logger.error(f"Clause execution expression failure on {self.model.__name__}: {error}")
            raise error

    async def filter(self, **filters: Any) -> Sequence[ModelType]:
        """Applies basic parameter matching expressions via keyword mappings."""
        try:
            statement = select(self.model).filter_by(**filters)
            result: Result = await self.session.execute(statement)
            return result.scalars().all()
        except exc.SQLAlchemyError as error:
            logger.error(f"Filter matching extraction failure on {self.model.__name__}: {error}")
            raise error

    async def update(self, instance: ModelType, data: dict[str, Any], auto_commit: bool = False) -> ModelType:
        """Mutates an active tracked entity instance safely using mapped state properties."""
        try:
            for key, value in data.items():
                setattr(instance, key, value)
            if auto_commit:
                await self.commit()
                await self.refresh(instance)
            else:
                await self.flush()
            return instance
        except exc.SQLAlchemyError as error:
            logger.error(f"State mutation execution error on instance {self.model.__name__}: {error}")
            await self.rollback()
            raise error

    async def update_by_id(self, record_id: int | str, data: dict[str, Any], auto_commit: bool = False) -> bool:
        """Executes a decoupled, high-performance execution statement update directly matching criteria."""
        try:
            statement = (
                update(self.model)
                .where(self.model.id == record_id)
                .values(**data)
                .execution_options(synchronize_session="fetch")
            )
            result = await self.session.execute(statement)
            if auto_commit:
                await self.commit()
            else:
                await self.flush()
            return (result.rowcount or 0) > 0
        except exc.SQLAlchemyError as error:
            logger.error(f"Direct update command trace error on {self.model.__name__} for ID {record_id}: {error}")
            await self.rollback()
            raise error

    async def delete(self, instance: ModelType, auto_commit: bool = False) -> bool:
        """Removes a tracked record instance from the active persistence framework target."""
        try:
            await self.session.delete(instance)
            if auto_commit:
                await self.commit()
            else:
                await self.flush()
            return True
        except exc.SQLAlchemyError as error:
            logger.error(f"Physical execution erasure error on {self.model.__name__}: {error}")
            await self.rollback()
            raise error

    async def delete_by_id(self, record_id: int | str, auto_commit: bool = False) -> bool:
        """Executes a structural database delete statement directly targeting a primary index key."""
        try:
            statement = delete(self.model).where(self.model.id == record_id)
            result = await self.session.execute(statement)
            if auto_commit:
                await self.commit()
            else:
                await self.flush()
            return (result.rowcount or 0) > 0
        except exc.SQLAlchemyError as error:
            logger.error(f"Structural delete expression failure on {self.model.__name__} for ID {record_id}: {error}")
            await self.rollback()
            raise error

    async def exists(self, **filters: Any) -> bool:
        """Checks for the physical presence of rows matching constraints via scalar queries."""
        try:
            statement = select(select(self.model).filter_by(**filters).exists())
            result = await self.session.execute(statement)
            return bool(result.scalar())
        except exc.SQLAlchemyError as error:
            logger.error(f"Existential evaluation trace exception on {self.model.__name__}: {error}")
            raise error

    async def count(self, **filters: Any) -> int:
        """Computes total analytical record match sizes using safe database aggregations."""
        try:
            statement = select(func.count()).select_from(self.model).filter_by(**filters)
            result = await self.session.execute(statement)
            return int(result.scalar() or 0)
        except exc.SQLAlchemyError as error:
            logger.error(f"Aggregation count execution exception on {self.model.__name__}: {error}")
            raise error

    async def paginate(
        self, limit_val: int, offset_val: int, order_by_clause: Any = None, **filters: Any
    ) -> tuple[Sequence[ModelType], int]:
        """Executes decoupled paging retrieval patterns returning slice collections alongside total counts."""
        try:
            total = await self.count(**filters)
            statement = select(self.model).filter_by(**filters).offset(offset_val).limit(limit_val)
            if order_by_clause is not None:
                statement = statement.order_by(order_by_clause)
            
            result: Result = await self.session.execute(statement)
            return result.scalars().all(), total
        except exc.SQLAlchemyError as error:
            logger.error(f"Workload pagination extraction error on {self.model.__name__}: {error}")
            raise error

    async def order_by(self, clause: Any) -> Sequence[ModelType]:
        """Retrieves records prioritized by targeted multi-key alignment patterns."""
        try:
            statement = select(self.model).order_by(clause)
            result: Result = await self.session.execute(statement)
            return result.scalars().all()
        except exc.SQLAlchemyError as error:
            logger.error(f"Ordering processing trace exception on {self.model.__name__}: {error}")
            raise error

    async def limit(self, count_val: int) -> Sequence[ModelType]:
        """Extracts an absolute truncated row window from upper index boundaries."""
        try:
            statement = select(self.model).limit(count_val)
            result: Result = await self.session.execute(statement)
            return result.scalars().all()
        except exc.SQLAlchemyError as error:
            logger.error(f"Upper-bound truncation extraction exception on {self.model.__name__}: {error}")
            raise error

    async def offset(self, skip_val: int) -> Sequence[ModelType]:
        """Extracts rows bypassing lower index boundaries sequentially."""
        try:
            statement = select(self.model).offset(skip_val)
            result: Result = await self.session.execute(statement)
            return result.scalars().all()
        except exc.SQLAlchemyError as error:
            logger.error(f"Lower-bound skip alignment failure on {self.model.__name__}: {error}")
            raise error

    async def execute_raw_sql(self, sql_string: str, parameters: dict[str, Any] | None = None) -> Sequence[GenericRow]:
        """Provides emergency escape paths to process optimized parameter-bound relational structures directly."""
        try:
            statement = text(sql_string)
            result = await self.session.execute(statement, parameters or {})
            if result.returns_rows:
                return result.all()
            return []
        except exc.SQLAlchemyError as error:
            logger.error(f"Raw backend SQL programmatic execution failure context: {error}")
            raise error

    async def refresh(self, instance: ModelType) -> None:
        """Forces the validation state engine to update an explicit item mapping from disk data."""
        await self.session.refresh(instance)

    async def flush(self) -> None:
        """Synchronizes tracked transaction state operations directly to the driver socket layers."""
        await self.session.flush()

    async def commit(self) -> None:
        """Closes the operational unit of work boundary, persisting statements securely."""
        await self.session.commit()

    async def rollback(self) -> None:
        """Performs immediate error recovery, flushing active operational frames out of memory safely."""
        await self.session.rollback()
