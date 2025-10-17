from typing import Optional, List
import difflib
import re

from app.services.table_reader import TableReader, provide_table_reader


def _best_match(query: str, choices: List[str]) -> Optional[str]:
	query_norm = query.strip().lower()
	choices_norm = [c.strip().lower() for c in choices]
	matches = difflib.get_close_matches(query_norm, choices_norm, n=1, cutoff=0.5)
	if matches:
		best = matches[0]
		for original in choices:
			if original.strip().lower() == best:
				return original
	return None


class QaAgent:
	def __init__(self, table_reader: TableReader):
		self._table_reader = table_reader

	async def answer_question_from_table(self, file_id: str, question: str, sheet_name: Optional[str] = None) -> str:
		rows = await self._table_reader.read_table(file_id=file_id, sheet_name=sheet_name)
		cell_match = re.search(r"\(([A-Za-z]+\d+)\)", question)
		if cell_match:
			cell_ref = cell_match.group(1)
			# Placeholder: could use read_cell in the future
		tool_names = [r['tool_name'] for r in rows]
		best = _best_match(question, tool_names)
		if best:
			url = next((r['url'] for r in rows if r['tool_name'] == best), None)
			if url:
				return f"Инструмент '{best}': см. раздел {url}. В таблице есть название и ссылка."
			return f"Инструмент '{best}' найден в таблице, но ссылка отсутствует."
		preview = ', '.join(tool_names[:5])
		return (
			"Не удалось однозначно определить инструмент из вопроса. "
			"Уточните название. Примеры из таблицы: " + preview
		)


_qa_agent_singleton: Optional[QaAgent] = None


def provide_qa_agent() -> QaAgent:
	global _qa_agent_singleton
	if _qa_agent_singleton is None:
		_qa_agent_singleton = QaAgent(provide_table_reader())
	return _qa_agent_singleton




