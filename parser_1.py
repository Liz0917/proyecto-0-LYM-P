file = open(input("Ingrese ruta de acceso del archivo con el programa (formato .txt): "))

ReadFile = file.read()
Command= ["=","GOTO","MOVE","TURN","FACE","PUT","TOTHE","INDIR","OFTYPE","NOP", "JUMP", "PICK"]
Condition = ["FACING", "CAN", "NOT"]
Cycle=["WHILE", "REPEAT" , "FOR"]
RES =["=", "GOTO","MOVE","TURN","FACE","PUT","TOTHE","INDIR","OFTYPE","NOP", "JUMP","PICK","WHILE", "REPEAT",
      "FOR", "FACING", "CAN", "NOT","PROC","IF" , "THEN", "ELSE", "DO", "baloons", "chips"]
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
def VerificarVAR(Procesamiento):
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
def VerificarProceso(Procesamiento):
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
def VerificarLlamadaProceso(Procesamiento):
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


def verificarCiclo(Procesamiento):
    Programa = Procesamiento["PROG"]
    pos = Procesamiento["i"]
    Reservadas = Procesamiento["RES"]
    
    # Verificar ciclo WHILE
    if Programa[pos] == "while:":
        pos += 1
        Procesamiento["i"] = pos
        Procesamiento = verificarCondicion(Procesamiento)
        Programa = Procesamiento["PROG"]
        pos = Procesamiento["i"]
        
        if Procesamiento["Funciona"]:  
            if Programa[pos] == "do:":
                pos += 1
                Procesamiento["i"] = pos

                Procesamiento = verificarBloque(Procesamiento)
                pos = Procesamiento["i"]
                Programa = Procesamiento["PROG"]
                
            else:
                Procesamiento["Funciona"] = False  
        else:
            Procesamiento["Funciona"] = False 

   # Verificar ciclo REPEAT
    elif Programa[pos] == "for:":
        pos += 1
        
        if Programa[pos].isdigit():  
            
            pos += 1
            if Programa[pos] == "repeat:":
                pos += 1
                if Programa[pos] == "[":  
                    Procesamiento["i"] = pos
                    
                    Procesamiento = verificarBloque(Procesamiento)
                    
                    pos = Procesamiento["i"]
                    
                else:
                    Procesamiento["Funciona"] = False  
            else:
                Procesamiento["Funciona"] = False  
        else:
            Procesamiento["Funciona"] = False  
    
    return Procesamiento 


def verificarComando(Procesamiento):
    Programa = Procesamiento["PROG"]
    Reservadas = Procesamiento["RES"]
    FD = Procesamiento["FD"]
    SD = Procesamiento["SD"]
    OC = ["DROP", "GET", "GRAB", "LETGO"]
    pos = Procesamiento["i"]
    
    def matchea(expected, pos):
        if Programa[pos] == expected:
            return True, pos + 1
        Procesamiento["Funciona"] = False
        return False, pos
    
    def identificadorValido(pos):
        return Programa[pos].isalnum() and Programa[pos] not in Reservadas
    
    if Programa[pos] in ["WALK", "LEAP"]:
        pos += 1
        success, pos = matchea("(", pos)
        if success and identificadorValido(pos):
            pos += 1
            if Programa[pos] == ")":
                pos += 1
            else:
                success, pos = matchea(",", pos)
                if success and (Programa[pos] in FD or Programa[pos] in SD):
                    pos += 1
                    matchea(")", pos)
        Procesamiento["i"] = pos
    
    elif Programa[pos] in OC:
        pos += 1
        success, pos = matchea("(", pos)
        if success and identificadorValido(pos):
            pos += 1
            matchea(")", pos)
        Procesamiento["i"] = pos
    
    elif Programa[pos] == "TURN":
        pos += 1
        success, pos = matchea("(", pos)
        if success and Programa[pos] in FD:
            pos += 1
            matchea(")", pos)
        Procesamiento["i"] = pos
    
    elif Programa[pos] == "TURNTO":
        pos += 1
        success, pos = matchea("(", pos)
        if success and Programa[pos] in SD:
            pos += 1
            matchea(")", pos)
        Procesamiento["i"] = pos
    
    elif Programa[pos] == "NOP":
        pos += 1
        success, pos = matchea("(", pos)
        if success:
            matchea(")", pos)
        Procesamiento["i"] = pos
    
    elif Programa[pos] == "JUMP":
        pos += 1
        success, pos = matchea("(", pos)
        if success and identificadorValido(pos):
            pos += 1
            success, pos = matchea(",", pos)
            if success and identificadorValido(pos):
                pos += 1
                matchea(")", pos)
        Procesamiento["i"] = pos
    
    elif Programa[pos] in Procesamiento["PROC"].keys():
        Parametros = Procesamiento["PROC"][Programa[pos]]
        pos += 1
        success, pos = matchea("(", pos)
        if success:
            conteo, coma = 0, False
            while Programa[pos] != ")":
                if identificadorValido(pos):
                    conteo += 1
                    coma = False
                elif Programa[pos] == "," and not coma:
                    coma = True
                else:
                    Procesamiento["Funciona"] = False
                    break
                pos += 1
            pos += 1  
            if Parametros != conteo:
                Procesamiento["Funciona"] = False
        Procesamiento["i"] = pos
    
    return Procesamiento
    
   
def verificarBloque(Procesamiento):
    Programa = Procesamiento["PROG"]
    pos = Procesamiento["i"]
    ejecuta = True
    coma = False
    
    while ejecuta:
        if Programa[pos] in Procesamiento["Command"] or Programa[pos] in Procesamiento["PROC"]:
            Procesamiento["i"] = pos
            Procesamiento = verificarComando(Procesamiento)
            pos = Procesamiento["i"]
            coma = False      
        elif Programa[pos] == ";":
            pos += 1
            coma = True
            if Programa[pos] == "{":
                pos += 1
                Procesamiento["i"] = pos
                Procesamiento = verificarBloque(Procesamiento)
                pos = Procesamiento["i"]
                coma = False
            if Programa[pos] in Procesamiento["Command"] or Programa[pos] in Procesamiento["PROC"]:
                Procesamiento["i"] = pos
                Procesamiento = verificarComando(Procesamiento)
                pos = Procesamiento["i"]  
            if Programa[pos - 1] == ";" and Programa[pos] == "}":
                Procesamiento["Funciona"] = False
                Procesamiento["i"] = pos
                ejecuta = False     
        elif Programa[pos] == "}":
            ejecuta = False
            pos += 1
            Procesamiento["i"] = pos
        elif Programa[pos] == "{":
            pos += 1
            Procesamiento["i"] = pos
            Procesamiento = verificarBloque(Procesamiento)
            pos = Procesamiento["i"]
            coma = False
        elif Programa[pos] == "WHILE" or Programa[pos] == "REPEAT":
            Procesamiento["i"] = pos
            Procesamiento = verificarCiclo(Procesamiento)
            pos = Procesamiento["i"]
            coma = False
        elif Programa[pos] == "IF":
            pos += 1
            Procesamiento["i"] = pos
            Procesamiento = verificarCondicion(Procesamiento)
            pos = Procesamiento["i"]
            coma = False
        else:
            Procesamiento["Funciona"] = False
            Procesamiento["i"] = pos
            ejecuta = False 
    
    return Procesamiento



def verificarCondicion(Procesamiento): 
    Programa = Procesamiento["PROG"]
    pos = Procesamiento["i"]
    
    if Programa[pos] in Procesamiento["Condition"]:
        pos += 1
        if Programa[pos] == "(":
            pos += 1
            Procesamiento["i"] = pos
            Procesamiento = verificarComando(Procesamiento)
            pos = Procesamiento["i"]  
            if Programa[pos] == ")":
                pos += 1
                if Programa[pos] == "{":
                    pos += 1
                    Procesamiento["i"] = pos
                    Procesamiento = verificarBloque(Procesamiento)
                    pos = Procesamiento["i"] 
                    if Programa[pos] == "ELSE":
                        pos += 1
                        if Programa[pos] == "{":
                            pos += 1
                            Procesamiento["i"] = pos
                            Procesamiento = verificarBloque(Procesamiento)
                            pos = Procesamiento["i"] 
                        else:
                            Procesamiento["Funciona"] = False
                    else:
                        Procesamiento["Funciona"] = False
                else:
                    Procesamiento["Funciona"] = False
            else:
                Procesamiento["Funciona"] = False 
        else:
            Procesamiento["Funciona"] = False
    
    return Procesamiento 


def Inicio(Procesamiento):
    Procesamiento = Adapt_Programa(Procesamiento)
    Programa = Procesamiento["PROG"]
    while Procesamiento["Funciona"] and Procesamiento["i"]<len(Programa):
        pos=Procesamiento["i"]
        if Programa[pos] =="DEFPROC":
            Procesamiento = VerificarProceso(Procesamiento)
        elif Programa[pos] =="DEFVAR":
            Procesamiento["i"] +=1
            Procesamiento = VerificarVAR(Procesamiento)
        elif Programa[pos] =="{":
            Procesamiento["i"] +=1
            Procesamiento = verificarBloque(Procesamiento)
        else: 
            Procesamiento["Funciona"]=False
    if Procesamiento["Funciona"]:
        print("El programa es CORRECTO")
    else:
        print("El programa es ERRONEO")      
Inicio(Procesamiento)