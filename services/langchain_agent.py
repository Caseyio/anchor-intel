import os
from langchain.chat_models import ChatOpenAI
from langchain.sql_database import SQLDatabase
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine

# Use your existing SQLAlchemy URI or pass via env
DATABASE_URL = os.getenv("DATABASE_URL")  # Example: postgresql://user:pass@host/db

engine = create_engine(DATABASE_URL)
db = SQLDatabase(engine)

llm = ChatOpenAI(
    temperature=0.3, model="gpt-4", openai_api_key=os.getenv("OPENAI_API_KEY")
)

toolkit = SQLDatabaseToolkit(db=db, llm=llm)

agent_executor = create_sql_agent(
    llm=llm, toolkit=toolkit, verbose=True, handle_parsing_errors=True
)


def run_sql_agent(prompt: str) -> str:
    return agent_executor.run(prompt)
