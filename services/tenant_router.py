# services/tenant_router.py

from sqlalchemy import create_engine
from langchain.sql_database import SQLDatabase

# This could also be loaded from env, config, or your DB
TENANT_DATABASES = {
    "store1": "postgresql://user:pass@host/store1_db",
    "store2": "postgresql://user:pass@host/store2_db",
    "default": "postgresql://user:pass@host/default_db",
}


def get_sqlagent_for_store(store_id: str):
    db_uri = TENANT_DATABASES.get(store_id, TENANT_DATABASES["default"])
    engine = create_engine(db_uri)
    db = SQLDatabase(engine)

    from langchain.chat_models import ChatOpenAI
    from langchain.agents import create_sql_agent
    from langchain.agents.agent_toolkits import SQLDatabaseToolkit

    llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        handle_parsing_errors=True,
    )

    return agent_executor
