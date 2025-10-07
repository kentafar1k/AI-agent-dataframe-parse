from typing import Optional
import difflib

from app.services.table_reader import read_table_from_gdrive


def _best_match(query: str, choices: list[str]) -> Optional[str]:
	query_norm = query.strip().lower()
	choices_norm = [c.strip().lower() for c in choices]
	matches = difflib.get_close_matches(query_norm, choices_norm, n=1, cutoff=0.5)
	if matches:
		best = matches[0]
		# Map back to original casing
		for original in choices:
			if original.strip().lower() == best:
				return original
	return None


async def answer_question_from_table(file_id: str, question: str, sheet_name: Optional[str] = None) -> str:
	rows = await read_table_from_gdrive(file_id=file_id, sheet_name=sheet_name)
	# Heuristic: look for a tool name in parentheses: (A1), or direct name after 'в ячейке'
	# If question is like: "Объясни инструмент, название которого находится в (A1)"
	import re
	cell_match = re.search(r"\(([A-Za-z]+\d+)\)", question)
	if cell_match:
		cell_ref = cell_match.group(1)
		# We cannot read arbitrary cell here without file id; assume A-column has tool names
		# But better: try to match tool name directly from question too
	# Try fuzzy match of any tool name mentioned in question
	tool_names = [r['tool_name'] for r in rows]
	best = _best_match(question, tool_names)
	if best:
		url = next((r['url'] for r in rows if r['tool_name'] == best), None)
		if url:
			return f"Инструмент '{best}': см. раздел {url}. В таблице есть название и ссылка."
		return f"Инструмент '{best}' найден в таблице, но ссылка отсутствует."
	# Fallback: list tools
	preview = ', '.join(tool_names[:5])
	return (
		"Не удалось однозначно определить инструмент из вопроса. "
		"Уточните название. Примеры из таблицы: " + preview
	)
