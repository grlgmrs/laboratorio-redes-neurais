"""
Executa todos os notebooks dos módulos, salva os outputs dentro de cada um
(in-place) e reporta sucesso ou erro por módulo.

Uso:
    python execute_all.py            # executa todos
    python execute_all.py 01 03 11   # executa só os módulos indicados
"""

import sys
import time
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

MODULOS_DIR = Path(__file__).parent / "modulos"
TIMEOUT = 300  # segundos por célula

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"


def executar(path: Path) -> tuple[bool, str, float]:
    """Executa o notebook em path e salva os outputs. Retorna (ok, mensagem, segundos)."""
    nb = nbformat.read(path, as_version=4)
    client = NotebookClient(
        nb,
        timeout=TIMEOUT,
        kernel_name="python3",
        resources={"metadata": {"path": str(path.parent)}},
    )
    t0 = time.time()
    try:
        client.execute()
        nbformat.write(nb, path)
        return True, "OK", time.time() - t0
    except CellExecutionError as e:
        nbformat.write(nb, path)  # salva mesmo com erro, para ver onde parou
        # pegar só a última linha do traceback
        msg = str(e).strip().splitlines()[-1][:120]
        return False, msg, time.time() - t0
    except Exception as e:
        return False, str(e)[:120], time.time() - t0


def main():
    filtro = set(sys.argv[1:])  # ex: {"01", "03"}

    notebooks = sorted(MODULOS_DIR.glob("*/notebook.ipynb"))
    if filtro:
        notebooks = [p for p in notebooks if p.parent.name[:2] in filtro]

    if not notebooks:
        print(f"{YELLOW}Nenhum módulo encontrado com o filtro: {filtro}{RESET}")
        sys.exit(1)

    total = len(notebooks)
    sucessos = 0
    print(f"\n{BOLD}Executando {total} módulo(s)...{RESET}\n")
    print(f"{'Módulo':<35} {'Status':<10} {'Tempo':>8}")
    print("─" * 60)

    for path in notebooks:
        nome = path.parent.name
        print(f"  {nome:<33} ", end="", flush=True)
        ok, msg, t = executar(path)
        if ok:
            sucessos += 1
            print(f"{GREEN}{'✓ OK':<10}{RESET} {t:>6.1f}s")
        else:
            print(f"{RED}{'✗ ERRO':<10}{RESET} {t:>6.1f}s")
            print(f"    {RED}{msg}{RESET}")

    print("─" * 60)
    cor = GREEN if sucessos == total else RED
    print(f"\n{cor}{BOLD}{sucessos}/{total} módulos executados com sucesso.{RESET}\n")
    sys.exit(0 if sucessos == total else 1)


if __name__ == "__main__":
    main()
