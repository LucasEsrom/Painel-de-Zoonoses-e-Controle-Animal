"""Exporta o banco local e envia somente o JSON ao repositório do painel."""

from pathlib import Path
import shutil
import subprocess
import sys


REPOSITORIO = "https://github.com/LucasEsrom/Painel-de-Zoonoses-e-Controle-Animal.git"


def executar(args, cwd):
    subprocess.run(args, cwd=cwd, check=True)


def git(repo, *args, capturar=False):
    command = ["git", "-c", f"safe.directory={repo.as_posix()}", "-C", str(repo), *args]
    return subprocess.run(command, check=True, capture_output=capturar, text=True,
                          encoding="utf-8" if capturar else None)


def main():
    base = Path(__file__).resolve().parent
    if not shutil.which("git"):
        raise RuntimeError("Git não encontrado. Instale o Git para Windows antes de atualizar o site.")
    if not (base / "banco_zoonoses.db").is_file():
        raise RuntimeError("Coloque a versão atualizada de banco_zoonoses.db na pasta do painel.")

    print("1/3 Gerando os dados a partir do banco local...", flush=True)
    executar([sys.executable, str(base / "exportar_dashboard.py")], base)

    repo = base / ".publicacao" / "Painel-de-Zoonoses-e-Controle-Animal"
    repo.parent.mkdir(exist_ok=True)
    if not repo.exists():
        executar(["git", "clone", REPOSITORIO, str(repo)], base)
    remote = git(repo, "remote", "get-url", "origin", capturar=True).stdout.strip()
    if remote.rstrip("/").removesuffix(".git") != REPOSITORIO.removesuffix(".git"):
        raise RuntimeError("A pasta de publicação aponta para outro repositório. Nenhum dado foi enviado.")
    if git(repo, "status", "--porcelain", capturar=True).stdout.strip():
        raise RuntimeError("Existem alterações pendentes na pasta .publicacao. Resolva-as antes de atualizar.")
    if git(repo, "branch", "--show-current", capturar=True).stdout.strip() != "main":
        raise RuntimeError("A pasta de publicação precisa estar na branch main.")

    print("2/3 Conferindo a versão no GitHub...", flush=True)
    git(repo, "pull", "--ff-only", "origin", "main")
    destino = repo / "dados" / "dashboard.json"
    destino.parent.mkdir(exist_ok=True)
    shutil.copyfile(base / "dados" / "dashboard.json", destino)
    git(repo, "add", "--", "dados/dashboard.json")
    git(repo, "-c", "user.name=LucasEsrom", "commit", "--only", "-m",
        "Atualiza dados tratados do painel", "--", "dados/dashboard.json")
    print("3/3 Enviando os dados ao GitHub...", flush=True)
    git(repo, "push", "origin", "main")
    print("\nDados enviados! O GitHub está preparando a publicação.")
    print("Acompanhe: https://github.com/LucasEsrom/Painel-de-Zoonoses-e-Controle-Animal/actions")
    print("O site mostrará os dados novos quando a execução terminar com sucesso.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"\nAtualização não concluída: {error}")
        print("Confira a conexão e o acesso à sua conta GitHub. O banco local foi preservado.")
        sys.exit(1)
