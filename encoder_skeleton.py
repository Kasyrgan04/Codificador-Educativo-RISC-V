#!/usr/bin/env python3
"""
Esqueleto del Codificador Educativo de Instrucciones RISC-V.
CE4301 Arquitectura de Computadores I — Proyecto Individual — 2026-II

Este esqueleto ya implementa el contrato de línea de comandos y de salida
requerido por la especificación. Usted debe completar las dos funciones
marcadas con TODO; puede modificar el resto del archivo si lo necesita,
siempre que se preserve el contrato de invocación y la línea "HEX: 0x...".

No es obligatorio usar este esqueleto ni Python: puede implementar su
propia herramienta desde cero, en el lenguaje que prefiera, siempre que
respete el mismo contrato (ver especificación, sección "Modo de operación").
"""
import sys

SOPORTADAS = ["add", "sub", "and", "or", "addi", "andi",
              "lw", "lb", "sw", "sb", "beq", "bne"]

INSTRUCTIONS = {
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

def register_number(reg):

    number = int(reg.replace("x", ""))

    if number<0 or number>31:
        raise ValueError("Número de registro fuera de rango")

    return number

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

    raise NotImplementedError("encode_instruction: pendiente de implementar")


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
       
