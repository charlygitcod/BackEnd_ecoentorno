from sqlalchemy import String, Integer, Column, Date, Time, DECIMAL, Enum, ForeignKey
from sqlalchemy.orm import relationship
from Conexion import base
import enum

class TipoRegistro(enum.Enum):
    patologico = "patologico"
    biosanitario = "biosanitario"

class RegistroPesos(base):
    __tablename__ = "registros_pesos"
    id_registro = Column(Integer, primary_key=True, autoincrement=True)
    empleado_documento = Column(Integer, ForeignKey('empleados.documento'), nullable=False)
    tipo = Column(Enum(TipoRegistro), nullable=False)
    peso = Column(DECIMAL(10, 2), nullable=False)
    turno = Column(String(20), nullable=False)
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)

    empleado = relationship("Usuario", back_populates="registros_pesos")

class EntregaEPP(base):
    __tablename__ = "entregas_epp"
    id_entrega = Column(Integer, primary_key=True, autoincrement=True)
    empleado_documento = Column(Integer, ForeignKey('empleados.documento'), nullable=False)
    nombre_ope = Column(String(255), nullable=False)
    nombre_epp = Column(String(255), nullable=False)
    cantidad = Column(Integer, nullable=False)
    fecha = Column(Date, nullable=False)
    empleado = relationship("Usuario", back_populates="entregas_epp")


class TipoUsuario(enum.Enum):
    operario = "operario"
    coordinador = "coordinador"
    administrador = "administrador"
    usuario_epp = "usuario_epp"

class Usuario(base):
    __tablename__ = "empleados"
    documento = Column(Integer, primary_key=True)
    nombre = Column(String(255), nullable=False)
    segundo_nombre = Column(String(255))
    apellido = Column(String(255), nullable=False)
    segundo_apellido = Column(String(255))
    correo = Column(String(255), nullable=True, unique=True)
    telefono = Column(String(20), nullable=True)
    rol = Column(Enum(TipoUsuario), nullable=False)
    edad = Column(Integer, nullable=True)
    descripcion = Column(String(255), nullable=True)
    fecha_registro = Column(Date, nullable=False)
    direccion = Column(String(255), nullable=True)
    
    credenciales = relationship("Credenciales", back_populates="usuario", uselist=False)
    entregas_epp = relationship("EntregaEPP", back_populates="empleado")
    registros_pesos = relationship("RegistroPesos", back_populates="empleado")

class Credenciales(base):
    __tablename__ = "credenciales"
    empleado_documento = Column(Integer, ForeignKey('empleados.documento'), primary_key=True)
    password = Column(String(255), nullable=False)

    usuario = relationship("Usuario", back_populates="credenciales")
