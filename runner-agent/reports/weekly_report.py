"""Formateador del reporte semanal en texto legible."""
from datetime import date


def format_weekly_report(review_text: str, week_start: str = None) -> str:
    """Envuelve el output del orquestador en un reporte formateado."""
    if week_start is None:
        week_start = date.today().isoformat()

    header = f"""
{'='*60}
  REPORTE SEMANAL — Runner Agent
  Semana del {week_start}
{'='*60}
"""
    footer = f"""
{'='*60}
  Generado el {date.today().isoformat()} | Runner Agent v1.0
{'='*60}
"""
    return header + "\n" + review_text + "\n" + footer
