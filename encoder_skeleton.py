#!/usr/bin/env python3
import sys

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

    "or" : {
        "type" : "R",
        "opcode" : 0b0110011,
        "funct3" : 0b110,
        "funct7" : 0b0100000
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

def get_instruction_info(mnemonic):
    return INSTRUCTIONS[mnemonic]

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

def immediate_bits(value, bits):
    value = int(value)
    return value & ((1 << bits) - 1)

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

def encode_instruction(instruction: str) -> int:
    
    """
    Recibe una instrucción como texto, p. ej. "add x5, x6, x7", y debe
    retornar su codificación de 32 bits como entero (0 <= valor < 2**32).

    Debe soportar únicamente las instrucciones en SOPORTADAS. Los valores
    de opcode/funct3/funct7 de cada una NO se proveen aquí: deben
    investigarse en el manual oficial de la ISA RISC-V (ver referencia en
    la especificación) y documentarse en el README.
    """
    # TODO: implementar. Sugerencia: parsear el mnemónico y los operandos,
    # despachar según el formato (R/I/S/B), y ensamblar los campos con
    # operaciones de bits.
    mnemonic, operands = parse_instruction(instruction)
    info = get_instruction_info(mnemonic)
    print(mnemonic)
    print(info)

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
    """
    Debe retornar un texto (para imprimirse en pantalla) que muestre, de
    forma visual, los 32 bits de 'word' divididos en los campos del
    formato correspondiente (R, I, S o B) — indicando el rango de bits y
    el valor de cada campo — junto con una breve explicación de cada uno.
    El formato visual (colores, tabla, arte ASCII, etc.) queda a su
    criterio, siempre que sea claro.
    """
    # TODO: implementar.
    raise NotImplementedError("explain_instruction: pendiente de implementar")


def main():
    if len(sys.argv) != 2:
        print(f'Uso: {sys.argv[0]} "<instruccion>"', file=sys.stderr)
        print(f'Ejemplo: {sys.argv[0]} "add x5, x6, x7"', file=sys.stderr)
        sys.exit(2)

    instruction = sys.argv[1]
    word = encode_instruction(instruction) & 0xFFFFFFFF

    #print(explain_instruction(instruction, word))
    print(hex(word))

    # No modificar el formato de la siguiente línea: la especificación la
    # requiere, literal, para permitir la validación automática.
    print(f"HEX: 0x{word:08x}")


if __name__ == "__main__":
    main()
    
       
