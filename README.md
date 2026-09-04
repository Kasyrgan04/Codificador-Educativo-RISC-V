# Codificador Educativo RISC-V

## Preparación del entorno

El codificador requiere

- Python 3.12
- Sistema operativo con soporte para ejecución de scripts Bash 
   - En Windows es posible ejecutar desde WSL o con una terminal de Git Bash
   - En Linux basta con ejecutar los comandos desde la terminal

No se requiere instalar bibliotecas adicionales para ejecutar la herramienta

Antes de ejecutar la herramienta, otorgue permisos de ejecución a **run.sh**:

```bash
chmod +x run.sh

```
## Instalación del toolchain

Para realizar la validación contra el ensamblador y desensamblador oficial
GNU RISC-V se requiere instalar el toolchain
`riscv64-unknown-elf`.

### Instalación en Ubuntu

Actualizar la lista de paquetes:

```bash
sudo apt update
```
Instalar el toolchain:

```bash
sudo apt install binutils-riscv64-unknown-elf
```
Este proporciona las herramientas necesarias:
- `riscv64-unknown-elf-as` : ensamblador GNU RISC-V
- `riscv64-unknown-elf-objdump`: herramienta para desemsamblar y obtener el hexadecimal de las instrucciones.

Comprobar que el ensamblador se instaló correctamente:
```bash
riscv64-unknown-elf-as --version
```
La salida esperada es
```bash
GNU assembler (2.42-1ubuntu1+6) 2.42
```

También comprobar que el desensamblador se instaló correctamente:
```bash
riscv64-unknown-elf-objdump --version
```
La salida esperada es
```bash
GNU objdump (2.42-1ubuntu1+6) 2.42
```

Con esto es posible ejecutar el script de validación con el siguiente comando:
```bash
python3 validaciones/validate_toolchain.py
```

### Consideraciones

Durante la validación de instrucciones de salto condicional (formato B) se
utilizan etiquetas dentro del archivo ensamblador generado, debido a que GNU
assembler calcula los desplazamientos relativos de branch a partir de la
posición de la etiqueta destino.
