"""Atualiza os dados e abre o dashboard local, sem comandos manuais."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import sys
import webbrowser


def main():
    pasta = Path(__file__).resolve().parent
    subprocess.run([sys.executable, str(pasta / "exportar_dashboard.py")], check=True, cwd=pasta)
    handler = partial(SimpleHTTPRequestHandler, directory=str(pasta))
    try:
        servidor = ThreadingHTTPServer(("127.0.0.1", 8000), handler)
    except OSError:
        # Se já houver outro serviço, escolhe uma porta livre para esta pasta.
        servidor = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    with servidor:
        url = f"http://127.0.0.1:{servidor.server_port}/dashboard_atualizado.html"
        print(f"\nDashboard: {url}", flush=True)
        print("Mantenha esta janela aberta enquanto usa o painel.", flush=True)
        print("Para encerrar, feche esta janela ou pressione Ctrl+C.\n", flush=True)
        if not webbrowser.open(url):
            print("Abra o endereço acima no navegador.", flush=True)
        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    try:
        main()
    except (OSError, subprocess.CalledProcessError) as erro:
        print(f"\nNão foi possível abrir o dashboard: {erro}")
        sys.exit(1)
