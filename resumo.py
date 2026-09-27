import os

def is_ignored(path, ignore_list):
    """
    Verifica se o caminho deve ser ignorado com base em uma lista de termos.
    """
    for ignore in ignore_list:
        if ignore in path:
            return True
    return False

def generate_project_context(output_file='projeto_contexto.txt'):
    """
    Percorre o diretório atual e consolida o conteúdo de arquivos de código
    e configuração em um único arquivo de texto para análise.
    """
    
    # Extensões de arquivos relevantes para o contexto do projeto
    relevant_extensions = (
        '.css', '.js', '.html', '.py', '.env', '.gitgnore', '.yml', 'Dockerfile', '.html', '.txt'
    )
    
    # Diretórios e arquivos a serem ignorados para evitar poluição do contexto
    ignore_list = [
        '__pycache__', '.git', 'venv', 'env', 
        'node_modules', '.idea', '.vscode', 
        'gerar_contexto.py', 'package-lock.json',
        'image_16f180.png' # Ignorando a imagem que você mandou
    ]

    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Escreve a estrutura de diretórios primeiro
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
        
        outfile.write("\n\n=== CONTEÚDO DOS ARQUIVOS ===\n\n")

        # Escreve o conteúdo dos arquivos
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if not is_ignored(d, ignore_list)]
            
            for file in files:
                if file.endswith(relevant_extensions) and not is_ignored(file, ignore_list):
                    file_path = os.path.join(root, file)
                    outfile.write(f"--- INÍCIO DO ARQUIVO: {file_path} ---\n")
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            outfile.write(infile.read())
                    except Exception as e:
                        outfile.write(f"[Erro ao ler arquivo: {e}]\n")
                        
                    outfile.write(f"\n--- FIM DO ARQUIVO: {file_path} ---\n\n")

    print(f"Arquivo '{output_file}' gerado com sucesso. Pode enviar para análise.")

if __name__ == "__main__":
    generate_project_context()