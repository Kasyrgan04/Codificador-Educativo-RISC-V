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

    vectors = load_vectors("vectores_ejemplo.txt")

    passed = 0

    for instruction, expected in vectors:

        try:
            result = encode_instruction(instruction)

            if result == expected:
                print(f"OK   {instruction}")
                passed += 1

            else:
                print(f"FAIL {instruction}")
                print(f"     esperado: 0x{expected:08x}")
                print(f"     obtenido: 0x{result:08x}")

        except Exception as e:
            print(f"ERROR {instruction}")
            print(f"      {e}")

    print()
    print(f"{passed}/{len(vectors)} pruebas correctas")

    for instruction, expected in vectors:

        word = encode_instruction(instruction)

        explanation = explain_instruction(instruction, word)

        if explanation:
            print(f"EXPLAIN OK {instruction}")


if __name__ == "__main__":
    run_tests()