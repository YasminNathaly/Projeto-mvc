#Rotas para o painel administrativo
from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session 

from app.database import get_db
from app.models.usuario import Usuario
from app.auth import get_admin, hash_senha

router = APIRouter(prefix="/usuarios", tags=["Usuários"])

templates = Jinja2Templates(directory="app/templates")


#Exibir os usuarios do sistema
@router.get("/", response_class=HTMLResponse)
def listar_usuarios(
    request: Request, 
    db: Session = Depends(get_db), 
    admin: dict = Depends(get_admin)):  #Bloqueia quem não é admin
    #Buscar todos os usuarios no banco
    usuarios = db.query(Usuario).order_by(Usuario.nome).all() 
    return templates.TemplateResponse(
        request,
        "usuarios/index.html",
        {"request": request, "usuarios": usuarios, "admin": admin, "usuario": admin}
    )


@router.get("/novo", response_class=HTMLResponse)
def novo_usuario(
    request: Request,
    admin: dict = Depends(get_admin)
):
    return templates.TemplateResponse(
        request,
        "usuarios/novo.html",
        {"request": request, "usuario": admin}
    )


@router.post("/novo")
def criar_usuario(
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    role: str = Form("operador"),
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin)
):
    usuario_existente = db.query(Usuario).filter_by(email=email).first()
    if usuario_existente:
        return templates.TemplateResponse(
            request,
            "usuarios/novo.html",
            {
                "request": request,
                "erro": "Este e-mail já está cadastrado.",
                "nome": nome,
                "email": email,
                "role": role,
                "usuario": admin,
            }
        )

    novo_usuario = Usuario(
        nome=nome,
        email=email,
        senha_hash=hash_senha("123456"),
        role=role,
        ativo=True,
    )
    db.add(novo_usuario)
    db.commit()

    return RedirectResponse(url="/usuarios?criado=ok", status_code=status.HTTP_302_FOUND)


@router.get("/{usuario_id}/editar", response_class=HTMLResponse)
def editar_usuario(
    request: Request,
    usuario_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin)
):
    usuario = db.query(Usuario).filter_by(id=usuario_id).first()
    if usuario is None:
        return RedirectResponse(url="/usuarios", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        request,
        "usuarios/editar.html",
        {"request": request, "editing_usuario": usuario, "usuario": admin}
    )


@router.post("/{usuario_id}/editar")
def atualizar_usuario(
    request: Request,
    usuario_id: int,
    nome: str = Form(...),
    email: str = Form(...),
    role: str = Form(...),
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin)
):
    usuario = db.query(Usuario).filter_by(id=usuario_id).first()
    if usuario is None:
        return RedirectResponse(url="/usuarios", status_code=status.HTTP_302_FOUND)

    usuario_existente = db.query(Usuario).filter(Usuario.email == email, Usuario.id != usuario_id).first()
    if usuario_existente:
        return templates.TemplateResponse(
            request,
            "usuarios/editar.html",
            {
                "request": request,
                "editing_usuario": usuario,
                "usuario": admin,
                "erro": "Este e-mail já está cadastrado por outro usuário.",
            }
        )

    usuario.nome = nome
    usuario.email = email
    usuario.role = role
    db.commit()

    return RedirectResponse(url="/usuarios?editado=ok", status_code=status.HTTP_302_FOUND)


@router.post("/{usuario_id}/toggle-ativo")
def alternar_status_usuario(
    request: Request,
    usuario_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin)
):
    if admin.get("id") == usuario_id:
        return RedirectResponse(url="/usuarios?erro=autoproprio", status_code=status.HTTP_302_FOUND)

    usuario = db.query(Usuario).filter_by(id=usuario_id).first()
    if usuario is None:
        return RedirectResponse(url="/usuarios", status_code=status.HTTP_302_FOUND)

    usuario.ativo = not usuario.ativo
    db.commit()
    # Redirect with status info for UI feedback
    status_qs = "ativado" if usuario.ativo else "desativado"
    return RedirectResponse(url=f"/usuarios?status={status_qs}", status_code=status.HTTP_302_FOUND)


@router.post("/{usuario_id}/desativar")
def desativar_usuario(
    request: Request,
    usuario_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin)
):
    if admin.get("id") == usuario_id:
        return RedirectResponse(url="/usuarios?erro=autoproprio", status_code=status.HTTP_302_FOUND)

    usuario = db.query(Usuario).filter_by(id=usuario_id).first()
    if usuario is None:
        return RedirectResponse(url="/usuarios", status_code=status.HTTP_302_FOUND)

    usuario.ativo = False
    db.commit()

    return RedirectResponse(url="/usuarios?status=desativado", status_code=status.HTTP_302_FOUND)


@router.post("/{usuario_id}/ativar")
def ativar_usuario(
    request: Request,
    usuario_id: int,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_admin)
):
    usuario = db.query(Usuario).filter_by(id=usuario_id).first()
    if usuario is None:
        return RedirectResponse(url="/usuarios", status_code=status.HTTP_302_FOUND)

    usuario.ativo = True
    db.commit()

    return RedirectResponse(url="/usuarios?status=ativado", status_code=status.HTTP_302_FOUND)
