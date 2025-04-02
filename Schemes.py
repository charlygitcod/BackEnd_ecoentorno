from pydantic import BaseModel
from datetime import date, time

# Esquema base para RegistroPesos
class RegistroPesosBase(BaseModel):
    empleado_documento: int
    tipo: str
    peso: float
    turno:str
    fecha: date
    hora: time

# Esquema base para EntregaEPP
class EntregaEPPBase(BaseModel):
    empleado_documento: int
    nombre_ope: str
    nombre_epp: str
    cantidad: int
    fecha: date

# Esquema base para Usuario
class UsuarioBase(BaseModel):
    documento: int
    nombre: str
    segundo_nombre: str
    apellido: str
    segundo_apellido: str
    correo: str
    telefono: str
    rol: str
    edad: int
    descripcion: str
    fecha_registro: date
    direccion: str

# Esquema base para Credenciales
class CredencialesBase(BaseModel):
    empleado_documento: int
    password: str

# Esquema para Login
class Login(BaseModel):
    nombre_usuario: int 
    password: str
