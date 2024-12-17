import os
import subprocess
import sys
import shutil
import stat
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


def get_repo_folder_name(repo_url: str):
    """Extrai o nome da pasta do repositório a partir do URL."""
    parsed_url = urlparse(repo_url)
    repo_name = os.path.basename(parsed_url.path).replace(".git", "")
    return repo_name


def git_clone(repo_url: str, repo_dir: str):
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


def git_command(repo_dir: str, command_list: list[str]):
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


def has_changes(repo_dir: str):
    """Verifica se há alterações não commitadas no repositório."""
    os.chdir(repo_dir)
    result = subprocess.run(["git", "status", "--porcelain"], stdout=subprocess.PIPE)
    os.chdir("..")
    return bool(result.stdout.strip())  # Se a saída não for vazia, há alterações


def git_pull(repo_url: str, repo_dir: str):
    """Realiza o git pull dentro da pasta do repositório, ou clona o repositório se a pasta não existir."""
    if not os.path.exists(repo_dir):
        print(f"❌ O diretório do repositório '{repo_dir}' não existe.")
        print(f"📥 Clonando o repositório '{repo_url}'...")
        git_clone(repo_url, repo_dir)  # Clona o repositório se a pasta não existir
        return  # Após clonar, não é necessário continuar com o git_pull

    git_command(repo_dir, ["git", "pull"])


def git_push(repo_dir: str):
    """Realiza o git push dentro da pasta do repositório, avisando o usuário em caso de falha e verificando se há alterações no remoto antes de enviar."""
    if has_changes(repo_dir):
        os.chdir(repo_dir)

        # Primeiro, fazemos o git fetch para verificar se há alterações no repositório remoto
        try:
            subprocess.run(["git", "fetch"], check=True)
            print("🔄 Atualizações do repositório remoto baixadas com sucesso.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao executar git fetch. Detalhes: {e}")
            os.chdir("..")
            sys.exit(1)

        # Comparamos se há alterações no repositório remoto em relação ao local
        result = subprocess.run(
            ["git", "log", "HEAD..origin/main", "--oneline"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if result.stdout:
            print("🔄 O repositório remoto tem alterações mais recentes.")
            print(
                "\n🛑 Por favor, faça um git pull para atualizar seu repositório local antes de enviar as alterações."
            )
            os.chdir("..")
            return  # Cancela a operação de git push

        try:
            print("📤 Executando git push...")
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(
                ["git", "commit", "-m", f"Atualização: {get_datetime()}"], check=True
            )
            subprocess.run(["git", "push"], check=True)
            print("✅ Push concluído com sucesso.")
        except subprocess.CalledProcessError as e:
            # Detectar erro específico
            if "Authentication failed" in str(e):
                print(
                    "❌ Erro de autenticação. Verifique suas credenciais e permissões."
                )
            elif "Could not resolve host" in str(e):
                print("❌ Erro de conexão. Verifique sua conexão de rede.")
            elif "fatal: unable to access" in str(e):
                print(
                    "❌ O repositório remoto não está acessível. Verifique a URL do repositório."
                )
            else:
                print(f"❌ Erro ao executar git push. Detalhes: {e}")
            os.chdir("..")
            sys.exit(1)
        os.chdir("..")
    else:
        print("⚠️ Não há alterações para enviar. O repositório já está atualizado.")


def force_remove(file_path: str):
    """Força a remoção de um arquivo, alterando suas permissões, se necessário."""
    if os.path.exists(file_path):
        # Altera as permissões do arquivo para torná-lo removível
        os.chmod(file_path, stat.S_IWRITE)
        try:
            os.remove(file_path)
            print(f"✅ Arquivo removido: {file_path}")
        except OSError as e:
            print(f"❌ Erro ao remover o arquivo {file_path}: {e}")


def remove_repo_folder(repo_dir: str):
    """Remove a pasta do repositório, mesmo que não esteja vazia."""
    if os.path.exists(repo_dir):
        print(f"🗑️ Removendo a pasta do repositório '{repo_dir}'...")
        try:
            # Tentando remover arquivos primeiro
            for root, dirs, files in os.walk(repo_dir, topdown=False):
                for name in files:
                    force_remove(os.path.join(root, name))
                for name in dirs:
                    try:
                        os.rmdir(os.path.join(root, name))
                    except OSError as e:
                        print(
                            f"❌ Erro ao remover o diretório {os.path.join(root, name)}: {e}"
                        )

            # Agora tenta remover a pasta principal
            shutil.rmtree(repo_dir)  # Remove a pasta e todo o seu conteúdo
            print(f"✅ Pasta '{repo_dir}' removida com sucesso.")
        except OSError as e:
            print(f"❌ Erro ao remover a pasta: {e}")
            sys.exit(1)
    else:
        print("⚠️ Pasta do repositório não encontrada.")


def open_save_folder(repo_dir: str = "", repo_folder: bool = False):
    if repo_folder:
        caminho = os.path.dirname(os.path.abspath(__file__))
        subprocess.run(f"cd /d {caminho}/{repo_dir} && explorer .", shell=True)
    else:
        caminho = f"C:/Users/{get_user()}/AppData/Roaming/.minecraft/saves"
        subprocess.run(f"cd /d {caminho} && explorer .", shell=True)


def get_datetime():
    data_atual = datetime.now()
    data_em_texto = data_atual.strftime("%d/%m/%Y - %H:%M")
    return data_em_texto


def get_user():
    usuario = getuser()
    return usuario


def main():
    # Carrega as configurações do arquivo
    config = load_config()
    repo_url = str(config.get("REPO_URL"))

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
        print("3. Abrir pasta do save (PC)")
        print("4. Abrir pasta do save (Repositório)")
        print("5. Remover pasta do save")
        print("0. Sair")

        choice = input("Digite o número da sua escolha: ").strip()

        if choice == "1":
            git_pull(repo_url, repo_dir)
        elif choice == "2":
            git_push(repo_dir)
        elif choice == "3":
            print("Abrir pasta do save (PC)")
            open_save_folder()
        elif choice == "4":
            print("Abrir pasta do save (Repositório)")
            open_save_folder(repo_dir, True)
        elif choice == "5":
            print("Remover repositório")
            remove_repo_folder(repo_dir)
        elif choice == "0":
            print("👋 Saindo. Até a próxima!")
            break
        else:
            print("❌ Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()
