from typing import Optional
import bcrypt
from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from Conexion import create, get_db
from Modelo import *
from Schemes import *
from fastapi.middleware.cors import CORSMiddleware
import jwt
from datetime import datetime, timedelta
import logging

# Configurar logging para ver qué rol se está pasando
logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://backendecoentorno-production.up.railway.app","frontendecoentorno-production.up.railway.app"], # añadir más orígenes si es necesario
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos HTTP (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)

# base.metadata.create_all(bind=create)

# ----------------------------- Registro Pesos -----------------------------

@app.post("/insertarpesos", response_model=RegistroPesosBase)
async def crear_registro(registro: RegistroPesosBase, db: Session = Depends(get_db)):
    # Asumimos que 'turno' es enviado desde el frontend en el objeto 'registro'
    nuevo_registro = RegistroPesos(**registro.dict())
    
    db.add(nuevo_registro)
    db.commit()
    db.refresh(nuevo_registro)
    return nuevo_registro


@app.get("/consultarpesos", response_model=list[RegistroPesosBase])
async def obtener_registros(db: Session = Depends(get_db)):
    registros = db.query(RegistroPesos).all()
    return registros

@app.get("/consultarpesos/{empleado_documento}", response_model=RegistroPesosBase)
async def obtener_registro_por_documento(empleado_documento: int, db: Session = Depends(get_db)):
    registro = db.query(RegistroPesos).filter(RegistroPesos.empleado_documento == empleado_documento).first()
    if registro is None:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return registro

# ----------------------------- Entrega EPP -----------------------------

@app.post("/insertarepp", response_model=EntregaEPPBase)
async def crear_entrega(entrega: EntregaEPPBase, db: Session = Depends(get_db)):
    nueva_entrega = EntregaEPP(**entrega.dict())
    db.add(nueva_entrega)
    db.commit()
    db.refresh(nueva_entrega)
    return nueva_entrega

@app.get("/consultarepp", response_model=list[EntregaEPPBase])
async def obtener_entregas(db: Session = Depends(get_db)):
    entregas = db.query(EntregaEPP).all()
    return entregas

@app.get("/consultarepp/{empleado_documento}", response_model=EntregaEPPBase)
async def obtener_entrega_por_documento(empleado_documento: int, db: Session = Depends(get_db)):
    entrega = db.query(EntregaEPP).filter(EntregaEPP.empleado_documento == empleado_documento).first()
    if entrega is None:
        raise HTTPException(status_code=404, detail="Entrega no encontrada")
    return entrega

# ----------------------------- Usuarios -----------------------------

@app.post("/insertarusuario", response_model=UsuarioBase)
async def crear_usuario(usuario: UsuarioBase, db: Session = Depends(get_db)):
    nuevo_usuario = Usuario(**usuario.dict())
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

@app.get("/consultarusuarios", response_model=list[UsuarioBase])
async def obtener_usuarios(
    query: Optional[str] = None, # Parámetro de búsqueda con longitud mínima
    db: Session = Depends(get_db)
):
    # Realizar la consulta con filtro de búsqueda
    if query:  # Si hay un parámetro de búsqueda
        usuarios = db.query(Usuario).filter(
            (Usuario.documento.like(f"%{query}%")) |
            (Usuario.nombre.like(f"%{query}%")) |
            (Usuario.apellido.like(f"%{query}%"))
        ).all()
    else:
        usuarios = db.query(Usuario).all()  # Si no hay filtro, devuelve todos los usuarios

    return usuarios


@app.put("/modificarusuario/{documento}", response_model=UsuarioBase)
async def modificar_usuario(documento: int, usuario: UsuarioBase, db: Session = Depends(get_db)):
    usuario_existente = db.query(Usuario).filter(Usuario.documento == documento).first()
    if not usuario_existente:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Actualizar los campos del usuario
    for key, value in usuario.dict().items():
        setattr(usuario_existente, key, value)

    db.commit()
    db.refresh(usuario_existente)
    return usuario_existente

@app.delete("/eliminarusuario/{documento}")
async def eliminar_usuario(documento: int, db: Session = Depends(get_db)):
    usuario_existente = db.query(Usuario).filter(Usuario.documento == documento).first()
    if not usuario_existente:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    db.delete(usuario_existente)
    db.commit()
    return {"message": "Usuario eliminado"}




# ----------------------------- Credenciales -----------------------------

@app.post("/insertarcredencial", response_model=CredencialesBase)
async def crear_credencial(credencial: CredencialesBase, db: Session = Depends(get_db)):
    # Encriptar la contraseña
    hashed_password = bcrypt.hashpw(credencial.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    nueva_credencial = Credenciales(
        empleado_documento=credencial.empleado_documento,
        password=hashed_password
    )
    
    db.add(nueva_credencial)
    db.commit()
    db.refresh(nueva_credencial)
    return nueva_credencial

@app.get("/consultarcredenciales", response_model=list[CredencialesBase])
async def obtener_credenciales(db: Session = Depends(get_db)):
    credenciales = db.query(Credenciales).all()
    return credenciales

@app.put("/modificarcredencial/{empleado_documento}", response_model=CredencialesBase)
async def modificar_credencial(empleado_documento: int, credencial: CredencialesBase, db: Session = Depends(get_db)):
    credencial_existente = db.query(Credenciales).filter(Credenciales.empleado_documento == empleado_documento).first()
    if not credencial_existente:
        raise HTTPException(status_code=404, detail="Credencial no encontrada")

    # Verificar si se está actualizando la contraseña
    if credencial.password:
        # Encriptar la nueva contraseña
        hashed_password = bcrypt.hashpw(credencial.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        credencial_existente.password = hashed_password
    else:
        # Mantener la contraseña actual si no se proporciona una nueva
        credencial_existente.password = credencial_existente.password

    # Actualizar otros campos de las credenciales
    for key, value in credencial.dict().items():
        if key != 'password':  # No actualizar la contraseña si no se proporciona una nueva
            setattr(credencial_existente, key, value)
    
    db.commit()
    db.refresh(credencial_existente)
    return credencial_existente

@app.delete("/eliminarcredencial/{empleado_documento}")
async def eliminar_credencial(empleado_documento: int, db: Session = Depends(get_db)):
    credencial_existente = db.query(Credenciales).filter(Credenciales.empleado_documento == empleado_documento).first()
    if not credencial_existente:
        raise HTTPException(status_code=404, detail="Credencial no encontrada")

    db.delete(credencial_existente)
    db.commit()
    return {"message": "Credencial eliminada exitosamente"}

# ----------------------------- Login -----------------------------

# Secret key y algoritmo para JWT
SECRET_KEY = "progkeysecret01"
ALGORITHM = "HS256"

# Función para crear un token JWT
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ----------------------------- Login -----------------------------

@app.post("/login")
async def login(request: Login, db: Session = Depends(get_db)):
    # Buscar las credenciales del usuario usando el documento
    credencial = db.query(Credenciales).filter(Credenciales.empleado_documento == request.nombre_usuario).first()
    
    # Verificar si el usuario existe y la contraseña es correcta
    if not credencial or not bcrypt.checkpw(request.password.encode('utf-8'), credencial.password.encode('utf-8')):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos")
    
    # Obtener el usuario asociado al documento de la credencial
    usuario = db.query(Usuario).filter(Usuario.documento == credencial.empleado_documento).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    
    # Obtener el rol del usuario y convertirlo a string
    rol_usuario = usuario.rol.value
    logging.info(f"El rol del usuario es: {rol_usuario}")  # Imprime el rol para depuración
    
    # Verificar si el rol es válido (ajusta los valores de roles permitidos según tu aplicación)
    if rol_usuario not in ["administrador", "coordinador", "operario", "usuario_epp"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rol no válido")
    
    # Generar el token JWT
    access_token = create_access_token(data={"sub": usuario.documento, "rol": rol_usuario})
    
    # Retornar el token JWT
    return {
        "message": "Inicio de sesión exitoso",
        "access_token": access_token,
        "token_type": "bearer",
        "rol": rol_usuario
    }
