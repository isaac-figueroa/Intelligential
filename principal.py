import controlador as c
import pandas as pd

def preguntar(instrucciones, tipo=int, valores=[]):
    """Regresa la respuesta válida seleccionada por el usuario"""

    repetir = True
    respuesta = -1
    #mientras aún no se haya ingresado una respuesta válida
    while repetir:
        #lectura de la respuesta
        respuesta = input(instrucciones)\
                    if tipo==str\
                    else\
                    eval(input(instrucciones))

        #en caso de que la respuesta sea str, entonces se convierte a minúsculas
        if type(respuesta) is str:
            respuesta = respuesta.lower()

        #la respuesta es correcta si es del tipo esperado y la lista de valores está vacía o
        #la respuesta se encuentra en la lista de valores permitidos
        if type(respuesta) is tipo and (len(valores)==0 or respuesta in valores):
            repetir = False
        else:
            print("ERROR: ¡Inserta una opción válida!\n")
    print()

    return respuesta

def insertar(pago):
    """Permite insertar cada uno de los datos para un nuevo pago"""

    continuar = True
    while continuar:
        print("Ingresa los siguientes datos...")
        id_contrato = preguntar('id_contrato: ')
        id_cliente = preguntar('id_cliente: ')
        fecha = preguntar('fecha: ', tipo=str)
        monto = preguntar('monto: ', tipo=float)
        #activo = preguntar('monto: ', tipo=bool)

        pago.insertar(id_contrato, id_cliente, fecha, monto)
        #pago.insertar(id_contrato, id_cliente, fecha, monto, activo)

        #pregunta para saber si desea ingresar más pagos o no
        instrucciones = "¿Deseas ingresar más pagos (s/n)?:"
        valores = {"s","n"}
        respuesta = preguntar(instrucciones, valores=valores, tipo=str)
        if respuesta=="n":
            continuar = False

def mostrar(pago):
    """Permite mostrar los registros en la base de datos"""

    instrucciones = "Elige algunas de las siguientes opciones: \n1. Mostrar todos\n2. Mostrar pagos de contrato\n3. Mostrar todos los pagos del contrato\n"
    valores = {1,2,3}
    respuesta = preguntar(instrucciones, valores=valores)

    if respuesta==1:
        #obtiene todos los registros en la base de datos
        registros = pago.obtenerRegistros()
    else:
        #obtiene los registros asociados a un id_contrato; se mostrarán también los inactivos
        #en caso de haber escogido la tercera opción
        id_contrato = preguntar("Ingresa el id del contrato: ", tipo=str)
        registros = pago.obtenerRegistros(id_contrato, soloActivos=respuesta==2)
    
    if(len(registros)>0):
        df = pd.DataFrame(registros)
        df.columns = registros[0].keys()
        with pd.option_context('display.max_rows', None,
                       'display.max_columns', None,
                       'display.precision', 3,
                       ):
            print(df)
            print()
    else:
        print("¡NO SE ENCONTRARON REGISTROS!")

def main():
    """Esta es la función principal del programa"""

    instrucciones = "Elige algunas de las siguientes opciones: \n1. Cargar base de datos\n2. Crear base de datos\n"
    valores = {1,2}
    respuesta = preguntar(instrucciones, valores=valores)

    #selección de la base de datos
    instrucciones = "Ingresa el nombre de la base de datos a "+\
                    ("cargar" if respuesta==1 else "crear")+": "
    respuesta = preguntar(instrucciones, tipo=str)
    pago = c.Pago(dbURL="sqlite:///"+respuesta+".sqlite", crearTabla=respuesta==2)

    #mientras se quiera seguir interactuando con el programa
    continuar = True
    while continuar:
        instrucciones = "Elige algunas de las siguientes opciones: \n1. Insertar pago\n2. Mostrar registros\n"
        valores = {1,2}
        respuesta = preguntar(instrucciones, valores=valores)
    
        #elección entre insertar o visualizar pagos
        if respuesta==1:
            insertar(pago)
        else:
            mostrar(pago)

        #pregunta para saber si continuar con el programa o no
        instrucciones = "¿Deseas volver al menú (s/n)?:"
        valores = {"s","n"}
        respuesta = preguntar(instrucciones, valores=valores, tipo=str)
        if respuesta=="n":
            continuar = False

if __name__ == '__main__':
    main()