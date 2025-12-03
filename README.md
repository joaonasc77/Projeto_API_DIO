🏋️‍♂️ API de Atletas – FastAPI

Este projeto implementa uma API para gerenciamento de atletas, com suporte a query parameters, paginação, tratamento de exceções e respostas customizadas utilizando FastAPI, SQLAlchemy e fastapi-pagination.

🔍 Query Parameters

- Filtro por nome

- Filtro por CPF

🎯 Respostas Customizadas

- Endpoint GET /atletas retorna:

- nome

- centro_treinamento

- categoria

❗ Tratamento de Exceções

Em caso de CPF duplicado na criação de atleta, a API retorna:
    - "detail": "Já existe um atleta cadastrado com o cpf: X"

- Exceção tratada: sqlalchemy.exc.IntegrityError

Status code: 303

📑 Paginação

- Implementada com fastapi-pagination, utilizando:

- limit

- offset
