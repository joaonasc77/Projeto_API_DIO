from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, status
from pydantic import UUID4
from sqlalchemy.future import select

#Dependência de sessão do banco (injeção automática pelo FastAPI)
from workout_api.contrib.dependencies import DatabaseDependency

#Schemas usados para entrada e saída dos dados
from workout_api.centro_treinamento.schemas import (
    CentroTreinamentoIn, 
    CentroTreinamentoOut
)

#Modelo ORM da tabela
from workout_api.centro_treinamento.models import CentroTreinamentoModel


#Cria um roteador específico para o módulo
router = APIRouter()


@router.post(
    "/",
    summary="Cadastrar um centro de treinamento",
    status_code=status.HTTP_201_CREATED,
    response_model=CentroTreinamentoOut,
)
async def create_centro_treinamento(
    db: DatabaseDependency,
    payload: CentroTreinamentoIn = Body(...)
) -> CentroTreinamentoOut:
    """
    Cria um novo centro de treinamento no banco de dados.
    """

    #Gera um objeto de saída com UUID e dados enviados pelo usuário
    novo_registro = CentroTreinamentoOut(
        id=uuid4(),
        **payload.model_dump()
    )

    try:
        #Cria uma instância do modelo ORM com os dados recebidos
        db_obj = CentroTreinamentoModel(**novo_registro.model_dump())

        #Adiciona à sessão do banco
        db.add(db_obj)

        #Confirma a transação
        await db.commit()

    except Exception:
        #Qualquer erro ao inserir dispara um HTTP 500
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao salvar o centro de treinamento no banco de dados."
        )

    # Retorna o objeto criado
    return novo_registro



@router.get(
    "/",
    summary="Listar centros de treinamento",
    response_model=list[CentroTreinamentoOut],
    status_code=status.HTTP_200_OK
)
async def listar_centros(db: DatabaseDependency) -> list[CentroTreinamentoOut]:
    """
    Retorna todos os centros de treinamento cadastrados.
    """

    # Executa SELECT * FROM centro_treinamento
    resultado = await db.execute(select(CentroTreinamentoModel))

    # Extrai os registros em forma de lista
    registros = resultado.scalars().all()

    return registros



@router.get(
    "/{id}",
    summary="Obter centro de treinamento por ID",
    response_model=CentroTreinamentoOut,
    status_code=status.HTTP_200_OK
)
async def obter_centro(id: UUID4, db: DatabaseDependency) -> CentroTreinamentoOut:
    """
    Retorna um único centro de treinamento com base no ID fornecido.
    """

    #Faz uma query filtrando pelo ID
    consulta = await db.execute(
        select(CentroTreinamentoModel).filter_by(id=id)
    )

    #Pega o primeiro resultado encontrado
    centro = consulta.scalars().first()

    #Se não existir, retorna erro 404
    if centro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nenhum centro de treinamento encontrado com id: {id}."
        )

    #Caso exista, retorna o registro encontrado
    return centro
