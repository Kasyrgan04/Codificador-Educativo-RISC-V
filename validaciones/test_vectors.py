import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from encoder_skeleton import encode_instruction, explain_instruction


def load_vectors(filename):

    vectors = []

    with open(filename, "r") as file:

        for line in file:

            line = line.strip()

            # Ignorar líneas vacías y comentarios
            if not line or line.startswith("#"):
                continue

            instruction, expected = line.split(";")

            instruction = instruction.strip()
            expected = int(expected.strip(), 16)

            vectors.append((instruction, expected))

    return vectors


def run_tests():

    vectors = load_vectors("./vectores_ejemplo.txt")

    passed = 0

    print()
    print(
        f"{'Instrucción':35}"
        f"{'Vector':14}"
        f"{'Encoder':14}"
        f"{'Estado'}"
    )

    print("-" * 80)

    for instruction, expected in vectors:

        try:
            result = encode_instruction(instruction)

            if result == expected:
                status = "OK"
                passed += 1

            else:
                status = "FAIL"

            print(
                f"{instruction:35}"
                f"0x{expected:08x}   "
                f"0x{result:08x}   "
                f"{status}"
            )

        except Exception as e:

            print(
                f"{instruction:35}"
                f"{'ERROR':14}"
                f"{'ERROR':14}"
                f"FAIL"
            )

            print(f"      {e}")

    print("-" * 80)
    print(f"{passed}/{len(vectors)} pruebas correctas")


    """print("\nValidación de explicaciones:")
    print("-" * 80)

    explain_passed = 0

    for instruction, expected in vectors:

        word = encode_instruction(instruction)

        explanation = explain_instruction(instruction, word)

        if explanation:
            print(f"EXPLAIN OK {instruction}")
            explain_passed += 1

        else:
            print(f"EXPLAIN FAIL {instruction}")


    print()
    print(
        f"{explain_passed}/{len(vectors)} explicaciones correctas"
    )"""


if __name__ == "__main__":
    run_tests()