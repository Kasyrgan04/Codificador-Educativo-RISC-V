import subprocess
import re
import tempfile
import os
import sys
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)


TESTS = [
    # R
    "add x31, x0, x1",
    "add x1, x31, x31",
    "add x16, x15, x8",

    "sub x31, x31, x0",
    "sub x0, x1, x31",
    "sub x18, x7, x5",

    "and x31, x31, x0",
    "and x2, x1, x30",
    "and x20, x15, x16",

    "or x31, x0, x31",
    "or x3, x25, x8",
    "or x14, x14, x14",

    # I
    "addi x31, x0, 2047",
    "addi x1, x31, -2048",
    "addi x10, x5, 0",

    "andi x31, x0, 2047",
    "andi x1, x31, -2048",
    "andi x20, x15, -1",

    "lw x31, 2047(x0)",
    "lw x1, -2048(x31)",
    "lw x15, 0(x10)",

    "lb x31, 2047(x0)",
    "lb x1, -2048(x31)",
    "lb x20, 15(x15)",

    # S
    "sw x31, 2047(x0)",
    "sw x0, -2048(x31)",
    "sw x15, 1023(x16)",

    "sb x31, 2047(x0)",
    "sb x0, -2048(x31)",
    "sb x20, -411(x23)",

    # B
    "beq x0, x31, +4094",
    "beq x31, x0, -4096",
    "beq x10, x10, +16",

    "bne x31, x0, +4094",
    "bne x0, x31, -4096",
    "bne x5, x6, -20",
]

def generate_asm(instruction):

    parts = instruction.replace(",", "").split()

    if parts[0] in ["beq", "bne"]:

        op = parts[0]
        rs1 = parts[1]
        rs2 = parts[2]
        offset = int(parts[3])

        # Branch positivo
        if offset > 0:

            asm = f"""
.text
.globl _start

_start:
    {op} {rs1}, {rs2}, target
    .space {offset - 4}

target:
    nop
"""

        # Branch negativo
        else:

            asm = f"""
.text
.globl _start

target:
    .space {abs(offset)}

_start:
    {op} {rs1}, {rs2}, target
"""

        return asm


    # Instrucciones que no son formato B
    return f"""
.text
.globl _start

_start:
    {instruction}
"""


def run_encoder(instruction):

    encoder_path = os.path.join(
        BASE_DIR,
        "encoder_skeleton.py"
    )

    result = subprocess.run(
        ["python3", encoder_path, instruction],
        capture_output=True,
        text=True
    )

    output = result.stdout + result.stderr

    match = re.search(r"HEX:\s*(0x[0-9a-fA-F]+)", output)

    if match:
        return match.group(1).lower()

    return "ERROR"


def run_toolchain(instruction):

    asm = generate_asm(instruction)

    with tempfile.TemporaryDirectory() as tmp:

        asm_file = os.path.join(tmp, "test.s")
        obj_file = os.path.join(tmp, "test.o")

        #print(asm)
        
        with open(asm_file, "w") as f:
            f.write(asm)

        subprocess.run(
        [
            "riscv64-unknown-elf-as",
            "-march=rv32i",
            "-mno-relax",
            asm_file,
            "-o",
            obj_file
        ],
        check=True,
        capture_output=True
        )

        result = subprocess.run(
            [
                "riscv64-unknown-elf-objdump",
                "-d",
                obj_file
            ],
            capture_output=True,
            text=True,
            check=True
        )

        output = result.stdout

        # Busca el hexadecimal de la instrucción

        match = re.search(
            r"^\s*[0-9a-f]+:\s+([0-9a-f]{8})",
            output,
            re.MULTILINE
        )

        if match:
            return "0x" + match.group(1).lower()


def main():

    correct = 0

    print()
    print(
        f"{'Instrucción':35} "
        f"{'Toolchain':14} "
        f"{'Encoder':14} "
        f"{'Estado'}"
    )

    print("-" * 80)

    for instruction in TESTS:

        toolchain = run_toolchain(instruction)
        encoder = run_encoder(instruction)

        if toolchain == encoder:
            status = "OK"
            correct += 1
        else:
            status = "FAIL"

        print(
            f"{instruction:35} "
            f"{toolchain:14} "
            f"{encoder:14} "
            f"{status}"
        )

    print("-" * 80)
    print(f"{correct}/{len(TESTS)} pruebas correctas")


if __name__ == "__main__":
    main()