"""Capa de persistencia.

- `db.py` y `runner_profile.py` (legacy): SQLite single-tenant que mantiene
  funcionando el sistema personal de José durante la migración.
- `models.py`, `database.py`, `repositories/`: nueva capa multitenant Postgres
  (Liebre SaaS). Cada función recibe `user_id` como primer argumento.
"""
