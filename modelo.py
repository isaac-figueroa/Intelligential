import controlador as c
import sqlalchemy as db
from sqlalchemy.sql.elements import Null

class Consulta:
    """Esta clase contiene las características para realizar consultas a la base de datos"""

    def __init__(self, dbURL, limiteSelector = 0):
        """Constructor de la clase"""

        #atributos sobre la conección y consulta a la base de datos
        self.__engine = db.create_engine(dbURL)
        self.__connection = self.__engine.connect()
        self.__metadata = db.MetaData()
            
        #límite de registros a obtener con un selector:
        #si es cero, entonces se obtienen todos a la vez
        self.limiteSelector = limiteSelector

    def crearTabla(self):
        """Crea la tabla de Pago"""

        self.tabPago = db.Table('Pago', self.__metadata,
                  db.Column('id_pago', db.Integer(), primary_key=True, autoincrement=True),
                  db.Column('id_contrato', db.Integer()),
                  db.Column('id_cliente', db.Integer()),
                  db.Column('fecha', db.Date(), nullable=False),
                  db.Column('monto', db.Float(), nullable=False),
                  db.Column('activo', db.Boolean(), nullable=False),
                  db.Column('fecha_registro', db.Date(), nullable=False),
              )

        self.__metadata.create_all(self.__engine)
        
    def cargarTabla(self):
        """Carga la tabla de Pago"""

        self.tabPago = db.Table('Pago', self.__metadata, autoload=True, autoload_with=self.__engine)

    def insertar(self, pago):
        """Inserta en la tabla el nuevo pago, dependiendo de si es uno atrasado o no"""
        
        #condición para la selección de los registros o para su eliminación
        condicion = (self.tabPago.columns.id_contrato==pago['id_contrato']) & \
                    (self.tabPago.columns.fecha>pago['fecha'])

        #selección de los registros que cumplen la condición
        pagosPosteriores = self.__seleccionar(self.tabPago, condicion)

        #si hubo registros tras la consulta, entonces procede el proceso de inserción completo
        if len(pagosPosteriores)>0:
            #actualización de los pagos posteriores
            self.__actualizar(self.tabPago, condicion)
            #inserción del pago atrasado
            self.__insertar(self.tabPago, pago)
            #modificación de los registros correspondientes a los pagos posteriores
            pagosPosteriores = c.Procesamiento.modificarPagos(pagosPosteriores)
            #inserción de los nuevos registros para los pagos posteriores
            self.__insertar(self.tabPago, pagosPosteriores)
        else:
            #si no hubo registros, solo se inserta el nuevo pago
            self.__insertar(self.tabPago, [pago])

    def obtenerRegistros(self, id_contrato=Null, soloActivos=True):
        """Regresa todos los registros o solo los que corresponden a los identificadores"""

        #condición para la selección de los registros
        if id_contrato!=Null:
            #si se requiere seleccionar los registros de un solo contrato
            #adicionalmente, si también solo los activos de dicho contrato o todos
            condicion = (self.tabPago.columns.id_contrato==id_contrato) &\
                        (self.tabPago.columns.activo==True)\
                        if soloActivos\
                        else\
                        self.tabPago.columns.id_contrato==id_contrato
        else:
            #si se requiere seleccionar todos los registros
            condicion = Null

        return self.__seleccionar(self.tabPago, condicion)

    def __seleccionar(self, tabla, condicion=Null):
        """Regresa los registros de la base de datos (que cumplen la condicion proporcionada)"""

        consulta =  db.select([tabla]) \
                    if condicion==Null \
                    else \
                    db.select([tabla]).where(condicion)

        ResultProxy = self.__connection.execute(consulta)
        registros = self.__obtenerRegistros(ResultProxy)
        ResultProxy.close()

        return registros

    def __obtenerRegistros(self, ResultProxy):
        """
        Retorna los registros con el ResultProxy proporcionado. Los registros se obtienen de 
        una sola vez o por lotes, como se haya indicado con el atributo limiteSelector
        """
        
        #Obtención de los registros en una sola intención
        if self.limiteSelector == 0:
            return ResultProxy.fetchall()

        #Obtención de los registros por lotes
        bandera = True
        registros = []
        while bandera:
            registrosParciales = ResultProxy.fetchmany(self.limiteSelector)
            if(registrosParciales == []):
                bandera = False

            registros.extend(registrosParciales)

        return registros

    def __eliminar(self, tabla, condicion):
        """Elimina los registros de la base de datos que cumplen la condición proporcionada"""

        consulta = db.delete(tabla).where(condicion)
        ResultProxy = self.__connection.execute(consulta)
        ResultProxy.close()

    def __actualizar(self, tabla, condicion):
        """Actualiza los registros de la base de datos que cumplen la condición proporcionada"""

        consulta = db.update(tabla).values(activo=False).where(condicion)
        ResultProxy = self.__connection.execute(consulta)
        ResultProxy.close()

    def __insertar(self, tabla, registros):
        """Inserta los registros proporcionados en la tabla señalada"""

        consulta = db.insert(tabla)
        ResultProxy = self.__connection.execute(consulta,registros)
        ResultProxy.close()