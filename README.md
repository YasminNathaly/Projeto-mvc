#Instale o requirements.txt

´´bash
pip install -r requirements.txt

#Iniciar o Alembic
python -m alembic init migrations

#Gerar a migration
```bash
python -m alembic revision --autogenerate -m "Criar tabela usuarios"

#aplicar a migration 
```bash
python -m alembic upgrade head
```

#Como rodar o código 
```bash
python -m uvicorn app.main:app --reload