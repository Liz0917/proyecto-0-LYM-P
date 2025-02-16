file = open(input("Ingrese ruta de acceso del archivo con el programa (formato .txt): "))

ReadFile = file.read()
Command= ["=","GOTO","MOVE","TURN","FACE","PUT","TOTHE","INDIR","OFTYPE","NOP", "JUMP", "PICK"]
Condition = ["FACING", "CAN", "NOT"]
Cycle=["WHILE", "REPEAT" , "FOR"]
RES =["=", "GOTO","MOVE","TURN","FACE","PUT","TOTHE","INDIR","OFTYPE","NOP", "JUMP","PICK","WHILE", "REPEAT",
      "FOR", "FACING", "CAN", "NOT","PROC","IF" , "THEN", "ELSE", "DO"]
Procesamiento = {"PROG": ReadFile, "i":0, "Funciona":True, "Command":Command, "Condition":Condition, "Cycle": Cycle,
                 "FD":["LEFT", "RIGHT", "AROUND"], "SD":["NORTH", "SOUTH", "EAST", "WEST"], "VAR":{},
                 "RES":RES,"PROC":{}}


def Adapt_Programa(Procesamiento):
    text= Procesamiento["PROG"]
    dictV={"|":0,"[":0, "]":0,";":0, ".":0,"=":0, ":":0, ":=":0}
 
    text = text.split("\n")
    
    PROGRAMA1 = []
    palabra = ""
    
    for line in text:
        for caracter in line:
          
            if caracter in "|[].;=:": 
                if palabra:
                    PROGRAMA1.append(palabra)
                    palabra = ""
                dictV[caracter] += 1
                PROGRAMA1.append(caracter.upper()) 
            elif caracter == " ":
                if palabra:
                    PROGRAMA1.append(palabra)
                    palabra = ""
            else:
                palabra += caracter
    if palabra:
        PROGRAMA1.append(palabra)
    Procesamiento["PROG"]=PROGRAMA1

    #verificar erroes de sintaxis en delimitadores de variables, parametros y bloques
    if (dictV["|"] %2 != 0 ) or (dictV["["]!=dictV["]"]):
        Procesamiento["Funciona"]= False
    return Procesamiento

# Verifica que las variables se definan correctamente
def Verificar_VAR(Procesamiento):
    Programa = Procesamiento["PROG"]
    pos = Procesamiento["i"]

    if Programa[pos] == "|":
        pos += 1
        variables = {}

        while pos < len(Programa) and Programa[pos] != "|":
            var_name = Programa[pos]

            if var_name.isidentifier() and var_name[0].islower():
                variables[var_name] = None  
                pos += 1
            else:
                Procesamiento["Funciona"] = False
                return Procesamiento  

        if pos >= len(Programa) or Programa[pos] != "|":
            Procesamiento["Funciona"] = False
            return Procesamiento

        pos += 1
        Procesamiento["VAR"] = variables  
        Procesamiento["i"] = pos  

    return Procesamiento


# Función para verificar que cada  proceso esté definido correctamente
def Verificar_Proceso(Procesamiento):
    Programa = Procesamiento["PROG"]
    pos = Procesamiento["i"]  
    contador = 0  
    nombre = ""

    if Programa[pos] == "PROC":
        pos += 1
    else:
        Procesamiento["Funciona"] = False
        return Procesamiento

    nombre = Programa[pos]

    if not (nombre[0].islower() and nombre.endswith(":") and nombre[:-1].isidentifier()) or nombre in Procesamiento["RES"]:
        Procesamiento["Funciona"] = False
        return Procesamiento

    pos += 1 

    while pos < len(Programa):
        parametro = Programa[pos]

        if parametro.isalnum():  
            contador += 1
            pos += 1

            if pos < len(Programa) and Programa[pos] == "and:":
                pos += 1  
            else:
                break 
            Procesamiento["Funciona"] = False
            return Procesamiento

 
    if pos < len(Programa) and Programa[pos] == "[":
        pos += 1  
    else:
        Procesamiento["Funciona"] = False
        return Procesamiento

  
    Procesamiento["PROC"][nombre] = contador  
    Procesamiento["i"] = pos  
    return Procesamiento

# Función para verificar llamada a procedimiento
def Verificar_Llamada_Proceso(Procesamiento):
    Programa = Procesamiento["PROG"]
    pos = Procesamiento["i"] 
    contador = 0  
    nombre = ""

    nombre = Programa[pos]
    if nombre not in Procesamiento["PROC"]:
        Procesamiento["Funciona"] = False
        return Procesamiento

    pos += 1 
    if pos < len(Programa) and Programa[pos].isalnum():  
        while pos < len(Programa):
            parametro = Programa[pos]

            if parametro.isalnum():  
                contador += 1
                pos += 1

                
                if pos < len(Programa) and Programa[pos] == "and:":
                    pos += 1  # Saltar "and:"
                else:
                    break 
            else:
                Procesamiento["Funciona"] = False
                return Procesamiento

   
    if pos < len(Programa) and Programa[pos] == ".":
        pos += 1 
    else:
        Procesamiento["Funciona"] = False
        return Procesamiento

    Procesamiento["i"] = pos
    return Procesamiento


