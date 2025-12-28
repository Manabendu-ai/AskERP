# execute_query
# Api - "ASKERP_AI"

from typing import Dict, Any, List, Union
from db_connector import ERPDatabase
from intent_classifier import classify_intent
from anomaly_detector import run_anomaly_checks

from openai import AzureOpenAI
from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam
)

import os


class AskERP_AI:
    def __init__(self):
        self.db = ERPDatabase()

        self.client = AzureOpenAI(
            api_key=os.getenv("ASKERP_AI"),
            api_version="2024-02-15-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )

        self.model = os.getenv("AZURE_OPENAI_DEPLOYMENT")

    # Process a natural-language ERP query
    def process_user_query(self, user_query: str) -> Dict[str, Any]:

        intent_result = classify_intent(user_query)
        intent = intent_result["intent"]

        if intent == "ANOMALY_CHECK":
            return self._handle_anomaly_request(intent_result)

        if intent in ("PAYMENT_QUERY", "INVENTORY_QUERY", "SUMMARY_REPORT"):
            return self._handle_sql_request(user_query, intent_result)

        return {
            "status": "error",
            "message": "Unable to determine user intent",
            "intent_analysis": intent_result
        }

    def _handle_sql_request(
            self,
            user_query: str,
            intent_result: Dict[str, Any]
    ) -> Dict[str, Any]:

        sql_query = self._generate_sql(user_query)

        try:
            data = self.db.execute_query(sql_query)
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "sql": sql_query,
                "intent_analysis": intent_result
            }

        return {
            "status": "success",
            "intent_analysis": intent_result,
            "sql": sql_query,
            "data": data
        }

    def _generate_sql(self, user_query: str) -> str:
        system_prompt = """
You are an ERP SQL assistant.

Rules:
- Generate ONLY SELECT queries
- Do NOT use INSERT, UPDATE, DELETE
- Use valid table and column names
- Do NOT hallucinate schema
- Output ONLY SQL, no explanation
"""

        messages: List[
            Union[
                ChatCompletionSystemMessageParam,
                ChatCompletionUserMessageParam
            ]
        ] = [
            ChatCompletionSystemMessageParam(
                role="system",
                content=system_prompt
            ),
            ChatCompletionUserMessageParam(
                role="user",
                content=user_query
            )
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1
        )

        sql = response.choices[0].message.content
        if not sql:
            raise ValueError("AI failed to generate SQL")

        return sql.strip()

    def _handle_anomaly_request(
            self,
            intent_result: Dict[str, Any]
    ) -> Dict[str, Any]:

        anomalies = run_anomaly_checks(self.db)

        return {
            "status": "success",
            "intent_analysis": intent_result,
            "anomalies": anomalies
        }
