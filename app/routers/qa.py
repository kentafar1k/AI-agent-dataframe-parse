from fastapi import APIRouter, HTTPException
from typing import Optional

from app.services.qa_agent import answer_question_from_table

router = APIRouter()


@router.post("/ask")
async def ask(file_id: str, question: str, sheet_name: Optional[str] = None):
	try:
		answer = await answer_question_from_table(file_id=file_id, question=question, sheet_name=sheet_name)
		return {"answer": answer}
	except FileNotFoundError:
		raise HTTPException(status_code=404, detail="File not found")
	except Exception as exc:
		raise HTTPException(status_code=400, detail=str(exc))




