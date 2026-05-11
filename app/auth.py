#1. Hash e verificacao de senhas com bcrypt
#2. Geracao do token JWT
#3. Leitura e validação do token vindo do cookie

from datetime import datetime, timedelta, timezone
from fastapi import Request, requests, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

#Carregar as variaveis de ambiente
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACESS_TOKEN_EXPIRACAO_MINUTES = int(os.getenv("ACESS_TOKEN_EXPIRE_MINUTES"))
                                    



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#Função da senha 
def hash_senha(senha: str):
    return pwd_context.hash(senha)

def verificar_senha(senha: str, senha_hash: str):
    return pwd_context.verify(senha, senha_hash)

# Funções do token
def criar_token(data: dict):
    
    paylod = data.copy()
    
    #Define quando o token expira
    expira = datetime.now(timezone.utc) + timedelta(minutes=ACESS_TOKEN_EXPIRACAO_MINUTES)
    paylod.update({"exp": expira})
    
    # criar o token
    token = jwt.encode(paylod, SECRET_KEY, algorithm=ALGORITHM)
    return token
def decodificar_token(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
    # dependenciais do fastapi para lidar com erros de autenticação

def get_usuario_logado(request: Request):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação não encontrado")
    try:
        payload = decodificar_token(token)
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de autenticação inválido"
                )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação inválido"
        )
    
def get_usuario_opcional(request: Request):
    try:
        return get_usuario_logado(request)
    except HTTPException:
        return None