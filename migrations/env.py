from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from dotenv import load_dotenv
import os

from app.models.models import Base  # ensure this path is correct

# Load .env explicitly
load_dotenv()

# Alembic Config object
config = context.config

# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add model metadata for 'autogenerate' support
target_metadata = Base.metadata


# Run migrations in 'offline' mode
def run_migrations_offline() -> None:
    url = os.getenv("DATABASE_URL")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# Run migrations in 'online' mode
def run_migrations_online() -> None:
    connectable = engine_from_config(
        {"sqlalchemy.url": os.getenv("DATABASE_URL")},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


# Choose mode based on Alembic context
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
