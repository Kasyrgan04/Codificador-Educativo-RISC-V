#!/usr/bin/env python3
import sys
import textwrap

SOPORTADAS = ["add", "sub", "and", "or", "addi", "andi",
              "lw", "lb", "sw", "sb", "beq", "bne"]

INSTRUCTIONS = {
    # FORMATO R 
    "add": {
        "type" : "R",
        "opcode" : 0b0110011,
        "funct3" : 0b000,
        "funct7" : 0b0000000
    },

    "sub" : {
        "type" : "R",
        "opcode" : 0b0110011,
        "funct3" : 0b000,
        "funct7" : 0b0100000
    },

    "and" : {
        "type" : "R",
        "opcode" : 0b0110011,
        "funct3" : 0b111,
        "funct7" : 0b0000000
        },

    "or": {
        "type": "R",
        "opcode": 0b0110011,
        "funct3": 0b110,
        "funct7": 0b0000000
    },

    # FORMATO I ARITMETICO

    "addi" : {
        "type" : "I",
        "opcode" : 0b0010011,
        "funct3" : 0b000
    },

    "andi" : {
        "type" : "I",
        "opcode" : 0b0010011,
        "funct3" : 0b111
    },

    # FORMATO I CARGA

    "lw" : {
        "type" : "I",
        "opcode" : 0b0000011,
        "funct3" : 0b010
    },

    "lb" : {
        "type" : "I",
        "opcode" : 0b0000011,
        "funct3" : 0b000
        },

    # FORMATO S

    "sw" : {
        "type" : "S",
        "opcode" : 0b0100011,
        "funct3" : 0b010
    },

    "sb" : {
        "type" : "S",
        "opcode" : 0b0100011,
        "funct3" : 0b000
    },

    #Formato B
    "beq" : {
        "type" : "B",
        "opcode" : 0b1100011,
        "funct3" : 0b000
    },
    "bne" : {
        "type" : "B",
        "opcode" : 0b1100011,
        "funct3" : 0b001
    }
}

#Función auxiliar que retorna el mnemonico de una instrucción
def get_instruction_info(mnemonic):
    return INSTRUCTIONS[mnemonic]

#Separa la instrucción en su mnemónico y sus operandos
def parse_instruction(instruction: str):
    instruction = instruction.replace(",", "")
    tokens = instruction.split()
    mnemonic = tokens[0]
    operands = tokens[1:]

    return mnemonic, operands

#Toma operandos de memoria con offset y los parsea en offset y registro
#Ejemplo: "4(x5)" -> (4, 5)
def parse_memory_operand(operand):
    offset, reg = operand.split("(")
    reg = reg.replace(")", "")
    imm = int(offset)
    rs1 = register_number(reg)
    return imm, rs1

#Obtiene unicamente el número de registro eliminando la "x"
def register_number(reg):

    number = int(reg.replace("x", ""))

    if number<0 or number>31:
        raise ValueError("Número de registro fuera de rango")

    return number

#Función auxiliar que obtiene la representación en complemento a dos
#de un inmediato conservando únicamente la cantidad de bits indicada.
def immediate_bits(value, bits):
    value = int(value)
    return value & ((1 << bits) - 1)

#Función auxiliar que recupera el valor con signo de un inmediato
#codificado en complemento a dos con la cantidad de bits indicada.
def sign_extend(value, bits):
    if value & (1 << (bits - 1)):
        value -= (1 << bits)
    return value

#Función de encodificación de las instrucciones tipo R
#Retorna la palabra de 32 bits correspondiente a la instrucción dada
def encode_R(info, operands):
    rd = register_number(operands[0])
    rs1 = register_number(operands[1])
    rs2 = register_number(operands[2])

    word = (
        (info ["funct7"] << 25) |
        (rs2 << 20) |
        (rs1 << 15) |
        (info ["funct3"] << 12) |
        (rd << 7) |
        (info ["opcode"])
    )

    return word

#Función de decodificación de las instrucciones tipo R
#Retorna un diccionario con los campos de la instrucción 
#Utiliza desplazamientos y máscaras para extraer los campos de la palabra de 32 bits
def decode_R(word: int) -> dict:
    funct7 = (word >> 25) & 0x7F
    rs2 = (word >> 20) & 0x1F
    rs1 = (word >> 15) & 0x1F
    funct3 = (word >> 12) & 0x7
    rd = (word >> 7) & 0x1F
    opcode = word & 0x7F

    return {
        "funct7": funct7,
        "rs2": rs2,
        "rs1": rs1,
        "funct3": funct3,
        "rd": rd,
        "opcode": opcode
    }

#Explica la instrucción tipo R decodificada, 
#Muestra el significado de los campos, su posición en la palabra, el valor decimal y binario de cada campo y el resultado de la operación
def explain_R(word):

    fields = decode_R(word)

    return textwrap.dedent(f"""
    Formato: R

    Bits:
        {word:032b}

    Campos:
        funct7  [31:25]: {fields['funct7']:07b} ({fields['funct7']})
        rs2     [24:20]: x{fields['rs2']} ({fields['rs2']})
        rs1     [19:15]: x{fields['rs1']} ({fields['rs1']})
        funct3  [14:12]: {fields['funct3']:03b} ({fields['funct3']})
        rd      [11:7] : x{fields['rd']} ({fields['rd']})
        opcode  [6:0]  : {fields['opcode']:07b} ({fields['opcode']})

        {describe_R(fields)}
        """)

#Describe la instrucción tipo R decodificada
#Distingue en tre las distintas operaciones para cambiar el resultado final que muestra la operación realizada
def describe_R(fields):

    if fields["funct3"] == 0 and fields["funct7"] == 0:
        operation = "ADD"
        operation_text = (
            f"x{fields['rd']} = x{fields['rs1']} + x{fields['rs2']}"
        )

    elif fields["funct3"] == 0 and fields["funct7"] == 32:
        operation = "SUB"
        operation_text = (
            f"x{fields['rd']} = x{fields['rs1']} - x{fields['rs2']}"
        )

    elif fields["funct3"] == 7:
        operation = "AND"
        operation_text = (
            f"x{fields['rd']} = x{fields['rs1']} & x{fields['rs2']}"
        )

    elif fields["funct3"] == 6:
        operation = "OR"
        operation_text = (
            f"x{fields['rd']} = x{fields['rs1']} | x{fields['rs2']}"
        )

    else:
        operation = "desconocida"
        operation_text = ""

    return textwrap.dedent(f"""
    Descripción:

    Operación: {operation}

    funct7:
      Identifica la variante de la operación R. Valor: {fields['funct7']:07b} ({fields['funct7']}).

    rs2:
      Segundo registro fuente.Contiene el segundo operando: x{fields['rs2']}.

    rs1:
      Primer registro fuente. Contiene el primer operando: x{fields['rs1']}.

    funct3:
      Junto con opcode identifica la operación dentro del formato R. 
      Valor: {fields['funct3']:03b} ({fields['funct3']}).

    rd:
      Registro de destino. El resultado de la operación se almacena en: x{fields['rd']}.

    opcode:
      Identifica la instrucción como formato R. Valor: {fields['opcode']:07b} ({fields['opcode']}).

    Resultado:
      {operation_text}

    
    """)

#Encodifica la instrucción tipo I
#Como existen de carga y aritméticas, se hace una distinción en el opcode para determinar de cual tipo es
def encode_I(info, operands):
    rd = register_number(operands[0])

    #Para instrucciones de carga
    if info["opcode"] == 0b0000011:
        imm, rs1 = parse_memory_operand(operands[1])
    else:
        rs1 = register_number(operands[1])
        imm = operands[2]

    imm = immediate_bits(imm, 12)

    word = (
        (imm << 20) |
        (rs1 << 15) |
        (info["funct3"] << 12) |
        (rd << 7) |
        (info["opcode"])
    )

    return word

#Decodifica la instrucción tipo I
#Retorna un diccionario con los campos de la instrucción
def decode_I(word: int) -> dict:
    imm_bits = (word >> 20) & 0xFFF
    imm = sign_extend(imm_bits, 12)
    rs1 = (word >> 15) & 0x1F
    funct3 = (word >> 12) & 0x7
    rd = (word >> 7) & 0x1F 
    opcode = word & 0x7F

    return {
        "imm": imm,
        "imm_bits": imm_bits,
        "rs1": rs1,
        "funct3": funct3,
        "rd": rd,
        "opcode": opcode
    }

#Explica la instrucción tipo I decodificada
#Muestra el significado de los campos, su posición en la palabra, el valor decimal y binario de cada campo y el resultado de la operación
def explain_I(word):

    fields = decode_I(word)

    return textwrap.dedent(f"""
        Formato: I

        Bits:
        {word:032b}

        Campos:

        imm     [31:20]: {fields['imm_bits']:012b} ({fields['imm']})
        rs1     [19:15]: x{fields['rs1']} ({fields['rs1']})
        funct3  [14:12]: {fields['funct3']:03b} ({fields['funct3']})
        rd      [11:7] : x{fields['rd']} ({fields['rd']})
        opcode  [6:0]  : {fields['opcode']:07b} ({fields['opcode']})

        {describe_I(fields)}
        """)

#Describe la instrucción
#Distingue entre las distintas operaciones para cambiar el resultado final que muestra la operación realizada
def describe_I(fields):
    if fields["funct3"] == 0 and fields["opcode"]==3:
        operation = "LB"
        operation_text = (
            f"x{fields['rd']} = Mem[x{fields['rs1']} + ({fields['imm']})] (carga de byte)"
        )
    elif fields["funct3"] == 2 and fields["opcode"]==3:
        operation = "LW"
        operation_text = (
            f"x{fields['rd']} = Mem[x{fields['rs1']} + ({fields['imm']})] (carga de palabra)"
        )
    elif fields["funct3"] == 0 and fields["opcode"]==19:
        operation = "ADDI"
        operation_text = (
            f"x{fields['rd']} = x{fields['rs1']} + ({fields['imm']})"
        )
    elif fields["funct3"] == 7 and fields["opcode"]==19:
        operation = "ANDI"
        operation_text = (
            f"x{fields['rd']} = x{fields['rs1']} & ({fields['imm']})"
        )
    else:
        operation = "desconocida"
        operation_text = ""

    return textwrap.dedent(f"""
    Descripción:

    Operación: {operation}


    imm:
      Inmediato de 12 bits con signo.
      Contiene el valor inmediato: {fields['imm_bits']:012b} ({fields['imm']}).
      Se utiliza como operando inmediato o desplazamiento según la instrucción. 
      

    rs1:
      Registro fuente. Contiene el operando: x{fields['rs1']}.

    funct3:
      Junto con opcode identifica la operación dentro del formato I. 
      Valor: {fields['funct3']:03b} ({fields['funct3']}).

    rd:
      Registro destino. El resultado de la operación se almacena en: x{fields['rd']}.

    opcode:
      Identifica la instrucción como formato I. Valor: {fields['opcode']:07b} ({fields['opcode']}).  
    
    Resultado:
      {operation_text}

    
    """)

#Encodifica la instrucción tipo S
#Retorna la palabra de 32 bits correspondiente a la instrucción dada
def encode_S(info, operands):
    rs2 = register_number(operands[0])
    imm, rs1 = parse_memory_operand(operands[1])

    imm = immediate_bits(imm, 12)

    imm_11_5 = (imm>>5) & 0x7F
    imm_4_0 = imm & 0x1F

    word = (
        (imm_11_5 << 25) |
        (rs2 << 20) |
        (rs1 << 15) |
        (info["funct3"] << 12) |
        (imm_4_0 << 7) |
        (info["opcode"])
    )
    return word

#decodifica la isntrucción
#retorna un diccionario con los campos de la instrucción utilizando máscaras de bits y desplazamientos para extraer los campos de la palabra de 32 bits
def decode_S(word: int) -> dict:

    imm_4_0 = (word >> 7) & 0x1F
    funct3 = (word >> 12) & 0x7
    rs1 = (word >> 15) & 0x1F
    rs2 = (word >> 20) & 0x1F
    imm_11_5 = (word >> 25) & 0x7F
    opcode = word & 0x7F

    #imm_bits es el valor sin complemento a 2 del inmediato, construido por la concatenatión de imm_11_5 y imm_4_0
    #imm es el valor con signo del immediato reconstruido a partir de imm_bits
    imm_bits = (imm_11_5 << 5) | imm_4_0
    imm = sign_extend(imm_bits, 12)

    #Se retorna tanto imm_bits como imm para poder hacer las representaciones en binario y decimal del inmediato
    return {
        "imm": imm,
        "imm_bits": imm_bits,
        "rs1": rs1,
        "rs2": rs2,
        "funct3": funct3,
        "opcode": opcode,
        "imm_11_5": imm_11_5,
        "imm_4_0": imm_4_0
    }

#Explica la instrucción
#Muestra el significado de los campos, su posición en la palabra, el valor decimal y binario de cada campo y el resultado de la operación
def explain_S(word):

    fields = decode_S(word)

    return textwrap.dedent(f"""
    Formato: S

    Bits:
    {word:032b}

    Campos:

    imm[11:5] [31:25]: {fields['imm_11_5']:07b} ({fields['imm_11_5']})
    rs2       [24:20]: x{fields['rs2']} ({fields['rs2']})
    rs1       [19:15]: x{fields['rs1']} ({fields['rs1']})
    funct3    [14:12]: {fields['funct3']:03b} ({fields['funct3']})
    imm[4:0]  [11:7] : {fields['imm_4_0']:05b} ({fields['imm_4_0']})
    opcode    [6:0] : {fields['opcode']:07b} ({fields['opcode']})

    Inmediato reconstruido:
    {fields['imm']}
    {describe_S(fields)}
    """)

#Describe la instrucción
#Distingue entre las distintas operaciones para cambiar el resultado final que muestra la operación realizada
def describe_S(fields):
    if fields["funct3"] == 0 and fields["opcode"]==35:
        operation = "SB"
        operation_text = (
            f"Mem[x{fields['rs1']} + ({fields['imm']})] = "
            f"x{fields['rs2']} (almacenamiento de byte)"
        )
    elif fields["funct3"] == 2 and fields["opcode"]==35:
        operation = "SW"
        operation_text = (
            f"Mem[x{fields['rs1']} + ({fields['imm']})] = "
            f"x{fields['rs2']} (almacenamiento de palabra)"
        )
    else:
        operation = "desconocida"
        operation_text = ""

    return textwrap.dedent(f"""
    Descripción:

    Operación: {operation}

    imm:
      Inmediato de 12 bits con signo.
      Contiene el valor inmediato: {fields['imm_bits']:012b} ({fields['imm']}).
      Se suma al registro base rs1 para obtener la dirección efectiva de memoria.
      
    rs1:
      Registro base de la dirección de memoria: x{fields['rs1']}.
      La dirección efectiva se calcula como x{fields['rs1']} + inmediato.

    rs2:
      Registro que contiene el dato a almacenar en memoria: x{fields['rs2']}.

    funct3:
      Junto con opcode identifica la operación dentro del formato S. 
      Valor: {fields['funct3']:03b} ({fields['funct3']}).

    opcode:
      Identifica la instrucción como formato S. Valor: {fields['opcode']:07b} ({fields['opcode']}).  
    
    Resultado:
      {operation_text}

    
    """)

#Encodifica la instrucción tipo B
#Retorna la palabra de 32 bits correspondiente a la instrucción dada
def encode_B(info, operands):
    rs1 = register_number(operands[0])
    rs2 = register_number(operands[1])
    imm = int(operands[2])

    imm = immediate_bits(imm, 13)

    imm_12 = (imm >> 12) & 0x1
    imm_10_5 = (imm >> 5) & 0x3F
    imm_4_1 = (imm >> 1) & 0xF
    imm_11 = (imm >> 11) & 0x1

    word = (
        (imm_12 << 31) |
        (imm_10_5 << 25) |
        (rs2 << 20) |
        (rs1 << 15) |
        (info["funct3"] << 12) |
        (imm_4_1 << 8) |
        (imm_11 << 7) |
        (info["opcode"])
    )
    return word

#Decodifica la instrucción tipo B
#Retorna un diccionario con los campos de la instrucción utilizando máscaras de bits y desplaz
def decode_B(word: int) -> dict:
    imm_12 = (word >> 31) & 0x1
    imm_10_5 = (word >> 25) & 0x3F
    rs2 = (word >> 20) & 0x1F
    rs1 = (word >> 15) & 0x1F
    funct3 = (word >> 12) & 0x7
    imm_4_1 = (word >> 8) & 0xF
    imm_11 = (word >> 7) & 0x1
    opcode = word & 0x7F
    imm_bits = (
    (imm_12 << 12) |
    (imm_11 << 11) |
    (imm_10_5 << 5) |
    (imm_4_1 << 1)
)
    imm = sign_extend(imm_bits, 13)

    #El comportamiento de imm_bits y imm es similar al de las instrucciones tipo S, se retorna ambos para poder hacer las representaciones en binario y decimal del inmediato
    return {
        "imm_12": imm_12,
        "imm_10_5": imm_10_5,
        "rs2": rs2,
        "rs1": rs1,
        "funct3": funct3,
        "imm_4_1": imm_4_1,
        "imm_11": imm_11,
        "imm": imm,
        "imm_bits": imm_bits,
        "opcode": opcode
    }

#Explica la instrucción tipo B decodificada
#Muestra el significado de los campos, su posición en la palabra, el valor decimal y
def explain_B(word):

    fields = decode_B(word)

    return textwrap.dedent(f"""
    Formato: B

    Bits:
    {word:032b}

    Campos:

    imm[12]    [31]   : {fields['imm_12']:01b} ({fields['imm_12']})
    imm[10:5]  [30:25]: {fields['imm_10_5']:06b} ({fields['imm_10_5']})
    rs2        [24:20]: x{fields['rs2']} ({fields['rs2']})
    rs1        [19:15]: x{fields['rs1']} ({fields['rs1']})
    funct3     [14:12]: {fields['funct3']:03b} ({fields['funct3']})
    imm[4:1]   [11:8] : {fields['imm_4_1']:04b} ({fields['imm_4_1']})
    imm[11]    [7]    : {fields['imm_11']:01b} ({fields['imm_11']})
    opcode     [6:0]  : {fields['opcode']:07b} ({fields['opcode']})

    Inmediato reconstruido:
    {fields['imm']}
    {describe_B(fields)}
    """)

#Describe la instrucción tipo B decodificada
#Distingue entre las distintas operaciones para cambiar el resultado final que muestra la operación realizada
def describe_B(fields):
    if fields["funct3"] == 0 and fields["opcode"]==99:
        operation = "BEQ"
        operation_text = (
            f"Si (x{fields['rs1']} == x{fields['rs2']}):\n"
            f"          PC = PC + ({fields['imm']})\n\n"
            f"      Si no:\n"
            f"          PC = PC + 4"
        )
    elif fields["funct3"] == 1 and fields["opcode"]==99:
        operation = "BNE"
        operation_text = (
                    f"Si (x{fields['rs1']} != x{fields['rs2']}):\n"
                    f"          PC = PC + ({fields['imm']})"
                    f"      Si no:\n"
                    f"          PC = PC + 4"
                )
    else:
        operation = "desconocida"
        operation_text = ""

    return textwrap.dedent(f"""
    Descripción:

    Operación: {operation}

    imm:
      Inmediato de 13 bits con signo. Se utiliza como desplazamiento relativo al PC. Contiene el valor inmediato: {fields['imm_bits']:013b} ({fields['imm']}).
      
    rs1:
      Primer registro fuente. Contiene el primer valor a comparar: x{fields['rs1']}.

    rs2:
      Segundo registro fuente. Contiene el segundo valor a comparar: x{fields['rs2']}.

    funct3:
      Junto con opcode identifica la operación dentro del formato B. Valor: {fields['funct3']:03b} ({fields['funct3']}).

    opcode:
      Identifica la instrucción como formato B. Valor: {fields['opcode']:07b} ({fields['opcode']}).

    Resultado:
      {operation_text}""")


def encode_instruction(instruction: str) -> int:

    mnemonic, operands = parse_instruction(instruction)
    info = get_instruction_info(mnemonic)

    if info["type"] == "R":
        return encode_R(info, operands)
    elif info["type"] == "I":
        return encode_I(info, operands)
    elif info["type"] == "S":
        return encode_S(info, operands)
    elif info["type"] == "B":
        return encode_B(info, operands)
    else:
        raise NotImplementedError("instrucción no soportada")

def explain_instruction(instruction: str, word: int) -> str:
    mnemonic, operands = parse_instruction(instruction)
    info = get_instruction_info(mnemonic)

    if info["type"] == "R":
        return explain_R(word)
    elif info["type"] == "I":
        return explain_I(word)
    elif info["type"] == "S":
        return explain_S(word)
    elif info["type"] == "B":
        return explain_B(word)
    else:
        raise NotImplementedError("Instrucción no soportada")

def main():
    if len(sys.argv) != 2:
        print(f'Uso: {sys.argv[0]} "<instruccion>"', file=sys.stderr)
        print(f'Ejemplo: {sys.argv[0]} "add x5, x6, x7"', file=sys.stderr)
        sys.exit(2)

    instruction = sys.argv[1]
    word = encode_instruction(instruction) & 0xFFFFFFFF
    print(explain_instruction(instruction, word))

    # No modificar el formato de la siguiente línea: la especificación la
    # requiere, literal, para permitir la validación automática.
    print(f"HEX: 0x{word:08x}")


if __name__ == "__main__":
    main()
    
       
