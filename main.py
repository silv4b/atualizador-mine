import os
import subprocess
import sys
from datetime import datetime
from urllib.parse import urlparse
from getpass import getuser

CONFIG_FILE = "config.txt"


def load_config():
    """Carrega as configurações do arquivo config.txt."""
    if not os.path.exists(CONFIG_FILE):
        print(f"❌ Arquivo de configuração '{CONFIG_FILE}' não encontrado.")
        sys.exit(1)

    config = {}
    with open(CONFIG_FILE, "r") as file:
        for line in file:
            line = line.strip()
            if line and "=" in line:
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()
    return config


def get_repo_folder_name(repo_url):
    """Extrai o nome da pasta do repositório a partir do URL."""
    parsed_url = urlparse(repo_url)
    repo_name = os.path.basename(parsed_url.path).replace(".git", "")
    return repo_name


def git_clone(repo_url, repo_dir):
    """Clona o repositório dentro da pasta especificada."""
    if not os.path.exists(repo_dir):
        print("📥 Clonando o repositório...")
        try:
            subprocess.run(["git", "clone", repo_url], check=True)
            print("✅ Repositório clonado com sucesso.")
        except subprocess.CalledProcessError:
            print("❌ Erro ao clonar o repositório.")
            sys.exit(1)
    else:
        print(f"✅ O repositório já está clonado na pasta '{repo_dir}'.")


def git_command(repo_dir, command_list):
    """Executa um comando git genérico."""
    os.chdir(repo_dir)
    try:
        subprocess.run(command_list, check=True)
        print(f"✅ {command_list[0]} concluído com sucesso.")
    except subprocess.CalledProcessError:
        print(f"❌ Erro ao executar {command_list[0]}.")
        os.chdir("..")
        sys.exit(1)
    os.chdir("..")


def has_changes(repo_dir):
    """Verifica se há alterações não commitadas no repositório."""
    os.chdir(repo_dir)
    result = subprocess.run(["git", "status", "--porcelain"], stdout=subprocess.PIPE)
    os.chdir("..")
    return bool(result.stdout.strip())  # Se a saída não for vazia, há alterações


def git_pull(repo_dir):
    """Realiza o git pull dentro da pasta do repositório."""
    git_command(repo_dir, ["git", "pull"])


def git_push(repo_dir):
    """Realiza o git push dentro da pasta do repositório."""
    if has_changes(repo_dir):
        os.chdir(repo_dir)
        try:
            print("📤 Executando git push...")
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(
                ["git", "commit", "-m", f"Atualização: {get_datetime()}"], check=True
            )
            subprocess.run(["git", "push"], check=True)
            print("✅ Push concluído com sucesso.")
        except subprocess.CalledProcessError:
            print("❌ Erro ao executar git push.")
            os.chdir("..")
            sys.exit(1)
        os.chdir("..")
    else:
        print("⚠️ Não há alterações para enviar. O repositório já está atualizado.")


def get_datetime():
    data_atual = datetime.now()
    data_em_texto = data_atual.strftime("%d/%m/%Y - %H:%M")
    return data_em_texto


def get_user():
    usuario = getuser()
    return usuario


def open_save_folder():
    caminho = f"C:/Users/{get_user()}/AppData/Roaming/.minecraft/saves"
    subprocess.run(f"cd /d {caminho} && explorer .", shell=True)


def main():
    # Carrega as configurações do arquivo
    config = load_config()
    repo_url = config.get("REPO_URL")

    if not repo_url:
        print("❌ Configurações inválidas no arquivo config.txt. Verifique REPO_URL.")
        sys.exit(1)

    # Obtém o nome da pasta do repositório
    repo_dir = get_repo_folder_name(repo_url)

    # Clona o repositório, se necessário
    git_clone(repo_url, repo_dir)

    while True:
        # Menu de opções para o usuário
        print(f"\nBem-vindo, {get_user().capitalize()}.")
        print("\nEscolha uma opção:")
        print("1. Baixar as alterações mais recentes (git pull)")
        print("2. Enviar suas alterações (git push)")
        print("3. Abrir pasta do save")
        print("0. Sair")

        choice = input("Digite o número da sua escolha: ").strip()

        if choice == "1":
            git_pull(repo_dir)
        elif choice == "2":
            git_push(repo_dir)
        elif choice == "3":
            print("Abrir pasta do save")
            open_save_folder()
        elif choice == "0":
            print("👋 Saindo. Até a próxima!")
            break
        else:
            print("❌ Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()
