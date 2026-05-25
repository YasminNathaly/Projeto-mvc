import email

from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.auth import hash_senha, verificar_senha, criar_token

router = APIRouter(prefix="/auth", tags=["Autenticação"])

templates = Jinja2Templates(directory="app/templates")

# Rota de cadastro
@router.get("/cadastro")
def tela_cadastro(request: Request):
    return templates.TemplateResponse(
        request,
        "auth/cadastro.html",
        {"request": request}
    )

#Exibir a tela de login
@router.get("/login")
def tela_login(request: Request):
    return templates.TemplateResponse(
        request,
        "auth/login.html",
        {"request": request}
    )

#Criar o usuário no banco - cadastrar usuario

@router.post("/cadastro")
def cadastrar_user(
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):
    
    # Verificar se o email está cadastrado
    user_existente = db.query(Usuario).filter(email=email).first()

    if user_existente:
        #Retorna o formulário com mensagem de erro
        return templates.TemplateResponse(
            request,
            "auth/cadastro.html",
            {"request": request, "erro": "Email já cadastrado"}
        )
    
    #Criar o novo usuário com senha hash
    novo_usuario = Usuario(
        nome=nome,
        email=email,
        senha_hash=hash_senha(senha), #Nunca salva a senha pura no db
)
    
    db.add(novo_usuario)
    db.commit()


#Redirecionar para login após cadastro 
    return RedirectResponse(url="/auth/login?cadastro=ok", status_code=302)

# Rota de login
@router.post("/login")
def fazer_login(
    request: Request,
    email: str = Form(...),
    senha: str = Form(...),
    db: Session = Depends(get_db)
):

    # Buscar o usuario no banco pelo email
    usuario = db.query(Usuario).filter_by(email=email).first()

    # Verificar a senha com bcrypt
    senha_correta = ( usuario is not None and verificar_senha(senha, usuario.senha_hash))

    if not senha_correta:
        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {"request": request, "erro": "E-mail ou senha incorretos."}
        )
    if not usuario.ativo:
        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {"request": request, "erro": "Usuário inativo."}
        )

    # Gera o token JWT

    token_data = criar_token(token_data)


    # Salvar o token em cookie Httponly
    # Redirecionar para a página principal
    response = RedirectResponse(url="/", status_code=302)

    response.set_cookie(
    key="access_token",
        value=token_data,
        httponly=True,
        max_age=3600, # Expira em 1 hora (Em segundos)
        samesite="lax"
)

    return response