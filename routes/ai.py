# routes/ai.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os
import json
import logging
from openai import OpenAI

from app.db.database import get_db
from services.langchain_agent import run_sql_agent
from services.ai_functions import (
    get_top_margin_products,
    get_top_category,
)
from app.auth.dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


class AiPrompt(BaseModel):
    prompt: str
    mode: str = "auto"  # Options: "sql" | "function" | "auto"


function_definitions = [
    {
        "name": "get_top_margin_products",
        "description": "Get top-selling products by margin over a given time window",
        "parameters": {
            "type": "object",
            "properties": {"days": {"type": "integer", "default": 30}},
            "required": [],
        },
    },
    {
        "name": "get_top_category",
        "description": "Return the top-selling category by total margin or revenue over a period",
        "parameters": {
            "type": "object",
            "properties": {"days": {"type": "integer", "default": 30}},
            "required": [],
        },
    },
]


@router.post("/ask")
async def ask_ai(
    request: AiPrompt,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    try:
        logger.info(f"[AI] Request received: {request.dict()}")
        tenant_id = current_user.tenant_id

        if request.mode not in {"sql", "function", "auto"}:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid mode '{request.mode}'. Use 'sql', 'function', or 'auto'.",
            )

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant manager with the ability to answer "
                    "questions for retail sales and business intelligence."
                ),
            },
            {"role": "user", "content": request.prompt},
        ]

        if request.mode == "sql":
            logger.info("[AI] Running SQL agent mode.")
            result = run_sql_agent(request.prompt, tenant_id=str(tenant_id))
            return {"answer": result}

        if request.mode == "function":
            logger.info("[AI] Running function-calling mode.")
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                functions=function_definitions,
                function_call="auto",
                temperature=0.3,
                max_tokens=300,
            )

            fn_call = response.choices[0].message.function_call
            if fn_call:
                fn_name = fn_call.name
                logger.info(f"[AI] Function triggered: {fn_name}")
                try:
                    args = json.loads(fn_call.arguments)
                    logger.info(f"[AI] Arguments: {args}")

                    if fn_name == "get_top_margin_products":
                        result = get_top_margin_products(
                            tenant_id=str(tenant_id), **args, db=db
                        )
                        if isinstance(result, list):
                            answer = "Top margin products:\n" + "\n".join(
                                f"- {r['product']}: ${r['total_margin']} from {r['units_sold']} units"
                                for r in result
                            )
                            return {"answer": answer}
                        return {"answer": result}

                    elif fn_name == "get_top_category":
                        result = get_top_category(
                            tenant_id=str(tenant_id), **args, db=db
                        )
                        return {"answer": f"Top category: {result}"}

                    else:
                        return {"answer": f"Function '{fn_name}' not implemented."}

                except Exception as fn_error:
                    logger.exception("[AI] Function call failed")
                    return {"answer": f"Function call failed: {str(fn_error)}"}

            logger.warning("[AI] No function was triggered.")
            return {"answer": "No function was triggered. Try rephrasing the question."}

        logger.info("[AI] Running fallback chat mode.")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.3,
            max_tokens=300,
        )
        return {"answer": response.choices[0].message.content.strip()}

    except Exception as e:
        logger.exception("[AI] Fatal error")
        raise HTTPException(status_code=500, detail=f"AI assistant error: {str(e)}")
