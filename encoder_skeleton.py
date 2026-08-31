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

def sign_extend(value, bits):
    if value & (1 << (bits - 1)):
        value -= (1 << bits)
    return value

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
        """)

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
        """)

def decode_S(word: int) -> dict:

    imm_4_0 = (word >> 7) & 0x1F
    funct3 = (word >> 12) & 0x7
    rs1 = (word >> 15) & 0x1F
    rs2 = (word >> 20) & 0x1F
    imm_11_5 = (word >> 25) & 0x7F
    opcode = word & 0x7F

    imm = (imm_11_5 << 5) | imm_4_0
    imm = sign_extend(imm, 12)

    return {
        "imm": imm,
        "rs1": rs1,
        "rs2": rs2,
        "funct3": funct3,
        "opcode": opcode,
        "imm_11_5": imm_11_5,
        "imm_4_0": imm_4_0
    }

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
    """)


def decode_B(word: int) -> dict:
    imm_12 = (word >> 31) & 0x1
    imm_10_5 = (word >> 25) & 0x3F
    rs2 = (word >> 20) & 0x1F
    rs1 = (word >> 15) & 0x1F
    funct3 = (word >> 12) & 0x7
    imm_4_1 = (word >> 8) & 0xF
    imm_11 = (word >> 7) & 0x1
    opcode = word & 0x7F
    imm = (
    (imm_12 << 12) |
    (imm_11 << 11) |
    (imm_10_5 << 5) |
    (imm_4_1 << 1)
)
    imm = sign_extend(imm, 13)

    return {
        "imm_12": imm_12,
        "imm_10_5": imm_10_5,
        "rs2": rs2,
        "rs1": rs1,
        "funct3": funct3,
        "imm_4_1": imm_4_1,
        "imm_11": imm_11,
        "imm": imm,
        "opcode": opcode
    }

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
    """)



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
    
       
