import os

def is_ignored(path, ignore_list):
    """
    Verifica se o caminho deve ser ignorado com base em uma lista de termos.
    """
    for ignore in ignore_list:
        if ignore in path:
            return True
    return False

def generate_project_structure(output_file='estrutura_projeto.txt'):
    """
    Percorre o diretório atual e salva apenas a estrutura de pastas e arquivos
    em um arquivo de texto.
    """
    
    # Diretórios e arquivos a serem ignorados para evitar poluição da listagem
    ignore_list = [
        '__pycache__', '.git', 'venv', 'env', 
        'node_modules', '.idea', '.vscode', 
        'gerar_contexto.py', 'package-lock.json',
        'image_16f180.png' # Ignorando a imagem que você mandou
    ]

    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Escreve a estrutura de diretórios
        outfile.write("=== ESTRUTURA DE DIRETÓRIOS ===\n")
        for root, dirs, files in os.walk('.'):
            # Modifica a lista dirs in-place para pular diretórios ignorados no walk
            dirs[:] = [d for d in dirs if not is_ignored(d, ignore_list)]
            
            level = root.replace('.', '').count(os.sep)
            indent = ' ' * 4 * (level)
            outfile.write(f"{indent}{os.path.basename(root)}/\n")
            
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                if not is_ignored(f, ignore_list):
                    outfile.write(f"{subindent}{f}\n")

    print(f"Arquivo '{output_file}' gerado com sucesso contendo apenas a estrutura.")

if __name__ == "__main__":
    generate_project_structure()