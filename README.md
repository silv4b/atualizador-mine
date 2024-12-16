# Script de Sincronização com GitHub

Este script em Python facilita o processo de sincronização de arquivos com o GitHub, permitindo que você baixe (pull) ou envie (push) alterações para um repositório. Ele é configurado por meio de um arquivo `config.txt` e pode ser utilizado tanto com repositórios públicos quanto privados.

## Requisitos

- **Python 3.6+**
- **Git instalado**
- **Repositório no GitHub**

Certifique-se de que o `git` está instalado e configurado no sistema operacional. Você pode verificar isso executando o comando:

```bash
git --version
```

## Instalação

1. Clone o repositório deste script ou copie o código para sua máquina.
2. No mesmo diretório do script, crie um arquivo chamado `config.txt`.

## Configuração

O arquivo `config.txt` deve conter as seguintes informações:

```txt
REPO_URL=https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
USERNAME=seu_usuario
```

- `REPO_URL`: URL do repositório GitHub.
- `USERNAME`: (Opcional para repositórios públicos) Seu nome de usuário no GitHub.

## Como Usar

1. Execute o script:

   ```bash
   python script.py
   ```

2. Escolha a operação desejada:
   - **1**: Baixar arquivos do repositório (pull).
   - **2**: Enviar arquivos para o repositório (push).
   - **3**. Abrir pasta do save

### Exemplo de Uso

#### 1. Baixar Arquivos (Pull)

Se você deseja apenas baixar os arquivos de um repositório público:

- Configure apenas o `REPO_URL` no `config.txt`.
- Execute o script e escolha a opção `1`.

#### 2. Enviar Arquivos (Push)

Se você deseja enviar arquivos para um repositório privado:

- Configure o `REPO_URL` e `USERNAME` no `config.txt`.
- Certifique-se de que as alterações estão salvas no diretório local.
- Execute o script e escolha a opção `2`.

## Estrutura do Script

O script realiza as seguintes operações:

1. **Clonar o Repositório**:
   - Se o diretório não estiver configurado como um repositório Git, ele será clonado automaticamente.

2. **Atualizar (Pull)**:
   - Sincroniza as alterações do repositório remoto para o local.

3. **Enviar (Push)**:
   - Adiciona, faz commit e envia as alterações locais para o repositório remoto.

## Erros Comuns

1. **"Arquivo de configuração 'config.txt' não encontrado"**:
   - Certifique-se de que o arquivo `config.txt` está no mesmo diretório do script.

2. **"Configuração incompleta"**:
   - Verifique se todos os campos necessários estão preenchidos no `config.txt`.

3. **Erro ao executar comandos Git**:
   - Certifique-se de que o `git` está instalado e que você tem permissão para acessar o repositório.

## Melhorias Futuras

[Em construção]
