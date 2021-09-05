import modelo as m
from datetime import datetime, date
import numpy as np

class Pago:
    """
    Esta clase contiene las características para recibir y enviar los datos a la vista y 
    al modelo
    """

    def __init__(self, dbURL="sqlite:///test.sqlite", crearTabla=False, limiteSelector=0, dateFormat='%d-%m-%Y'):
        """Constructor de la clase"""

        #creación del objeto de la clase Consulta
        self.__consulta = m.Consulta(dbURL, limiteSelector)

        #creación u obtención de la tabla 'Pago'
        self.__consulta.crearTabla() if crearTabla else self.__consulta.cargarTabla()

        #formato de las fechas
        self.dateFormat = dateFormat

    def insertar(self, id_contrato, id_cliente, fecha, monto, activo=True):
        """Inserta en la tabla los datos especificados"""

        pago = {
            'id_contrato': id_contrato,
            'id_cliente': id_cliente,
            'fecha': datetime.strptime(fecha, self.dateFormat).date(),
            'monto': monto,
            'activo': activo,
            'fecha_registro': date.today()
        }

        self.__consulta.insertar(pago)

    def obtenerRegistros(self, id_contrato=-1, soloActivos=True):
        """Regresa todos los registros o solo los que corresponden al identificador"""

        return self.__consulta.obtenerRegistros() \
               if id_contrato==-1 \
               else\
               self.__consulta.obtenerRegistros(id_contrato, soloActivos) 

class Procesamiento:
    """Esta clase contiene los métodos para procesar los datos de manera específica"""
    @staticmethod
    def modificarPagos(posteriores):
        """
        Regresa los pagos proporcionados convirtiéndolos en diccionarios y actualizando su 
        estado a inactivo y eliminando su id_pago
        """

        #conversión a numpy array
        posteriores = np.array(posteriores, dtype = 'object')
        #eliminación del id_pago
        posteriores = np.delete(posteriores, 0, 1)
        #conversión de numpy array a lista
        posteriores = posteriores.tolist()

        #conversión de cada registro a diccionario con las llaves de cada columna
        actualizados = []
        for registro in posteriores:
            actualizados.append({
                'id_contrato': registro[0],
                'id_cliente': registro[1],
                'fecha': registro[2],
                'monto': registro[3],
                'activo': registro[4],
                'fecha_registro': registro[5],
            })

        #retorno de la lista con los registros actualizados
        return actualizados