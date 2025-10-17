from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from app.services.qa_agent import QaAgent, provide_qa_agent

router = APIRouter()


@router.post("/ask")
async def ask(file_id: str, question: str, sheet_name: Optional[str] = None, agent: QaAgent = Depends(provide_qa_agent)):
	try:
		answer = await agent.answer_question_from_table(file_id=file_id, question=question, sheet_name=sheet_name)
		return {"answer": answer}
	except FileNotFoundError:
		raise HTTPException(status_code=404, detail="File not found")
	except Exception as exc:
		raise HTTPException(status_code=400, detail=str(exc))




