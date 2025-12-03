from uuid import uuid4
from datetime import datetime
from fastapi import APIRouter, Body, HTTPException, status
from pydantic import UUID4
from sqlalchemy.future import select

from workout_api.contrib.dependencies import DatabaseDependency

from workout_api.atleta.schemas import AtletaIn, AtletaOut, AtletaUpdate
from workout_api.atleta.models import AtletaModel
from workout_api.categorias.models import CategoriaModel
from workout_api.centro_treinamento.models import CentroTreinamentoModel

router = APIRouter()

#Create Atleta
@router.post(
    "/",
    summary="Registrar um novo atleta",
    status_code=status.HTTP_201_CREATED,
    response_model=AtletaOut,
)
async def create_atleta(
    session: DatabaseDependency,
    atleta_data: AtletaIn = Body(...)
):
    #Verificando categoria
    categoria_nome = atleta_data.categoria.nome
    query_categoria = select(CategoriaModel).filter(CategoriaModel.nome == categoria_nome)
    categoria = (await session.execute(query_categoria)).scalars().first()

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Categoria '{categoria_nome}' não encontrada."
        )

    #Verificando centro de treinamento
    ct_nome = atleta_data.centro_treinamento.nome
    query_ct = select(CentroTreinamentoModel).filter(CentroTreinamentoModel.nome == ct_nome)
    centro_treinamento = (await session.execute(query_ct)).scalars().first()

    if not centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Centro de treinamento '{ct_nome}' não encontrado."
        )

    #Inserindo atleta
    try:
        atleta_out = AtletaOut(
            id=uuid4(),
            created_at=datetime.utcnow(),
            **atleta_data.model_dump()
        )

        atleta_db = AtletaModel(
            **atleta_out.model_dump(exclude={"categoria", "centro_treinamento"})
        )
        atleta_db.categoria_id = categoria.pk_id
        atleta_db.centro_treinamento_id = centro_treinamento.pk_id

        session.add(atleta_db)
        await session.commit()

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao salvar atleta no banco de dados."
        )

    return atleta_out

#Listar Atletas
@router.get(
    "/",
    summary="Listar todos os atletas",
    status_code=status.HTTP_200_OK,
    response_model=list[AtletaOut],
)
async def listar_atletas(session: DatabaseDependency):
    resultado = await session.execute(select(AtletaModel))
    atletas = resultado.scalars().all()
    return [AtletaOut.model_validate(a) for a in atletas]


#Get Atleta by id
@router.get(
    "/{id}",
    summary="Buscar atleta pelo ID",
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def obter_atleta(id: UUID4, session: DatabaseDependency):
    consulta = select(AtletaModel).filter(AtletaModel.id == id)
    atleta = (await session.execute(consulta)).scalars().first()

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta com ID {id} não foi encontrado."
        )

    return atleta


#Update Atleta
@router.patch(
    "/{id}",
    summary="Atualizar atleta pelo ID",
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def atualizar_atleta(
    id: UUID4,
    session: DatabaseDependency,
    updates: AtletaUpdate = Body(...)
):
    consulta = select(AtletaModel).filter(AtletaModel.id == id)
    atleta = (await session.execute(consulta)).scalars().first()

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta com ID {id} não encontrado."
        )

    campos = updates.model_dump(exclude_unset=True)
    for campo, valor in campos.items():
        setattr(atleta, campo, valor)

    await session.commit()
    await session.refresh(atleta)

    return atleta

#Delete Atleta
@router.delete(
    "/{id}",
    summary="Remover atleta pelo ID",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remover_atleta(id: UUID4, session: DatabaseDependency):
    consulta = select(AtletaModel).filter(AtletaModel.id == id)
    atleta = (await session.execute(consulta)).scalars().first()

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta com ID {id} não encontrado."
        )

    await session.delete(atleta)
    await session.commit()
