import sqlite3
import csv
import os
import pathlib

BASE_DIR = pathlib.Path(__file__).parent.resolve()
BACKUP_DIR = BASE_DIR / 'backups'
DATA_DIR = BASE_DIR / 'data'
EXPORTS_DIR = BASE_DIR / 'exports'

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / 'livraria.db'
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS livros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        autor TEXT NOT NULL,
        ano_publicacao INTEGER NOT NULL,
        preco REAL NOT NULL
    )
''')
conn.commit()

def adicionar_livro():
    """Adiciona um novo livro ao banco de dados."""
    titulo = input("Título: ")
    autor = input("Autor: ")
    while True:
        try:
            ano_publicacao = int(input("Ano de Publicação: "))
            if ano_publicacao > 0:
                break
            else:
                print("O ano de publicação deve ser um número positivo.")
        except ValueError:
            print("Ano de Publicação inválido. Digite um número inteiro.")
    while True:
        try:
            preco = float(input("Preço: "))
            if preco > 0:
                break
            else:
                print("O preço deve ser um número positivo.")
        except ValueError:
            print("Preço inválido. Digite um número.")

    cursor.execute('''
        INSERT INTO livros (titulo, autor, ano_publicacao, preco)
        VALUES (?, ?, ?, ?)
    ''', (titulo, autor, ano_publicacao, preco))
    conn.commit()
    print("Livro adicionado com sucesso!")
    fazer_backup()

def exibir_livros():
    """Exibe todos os livros cadastrados."""
    cursor.execute('SELECT * FROM livros')
    livros = cursor.fetchall()
    if livros:
        for livro in livros:
            print(f"ID: {livro[0]}, Título: {livro[1]}, Autor: {livro[2]}, Ano: {livro[3]}, Preço: R$ {livro[4]:.2f}")
    else:
        print("Nenhum livro cadastrado.")

def atualizar_preco():
    """Atualiza o preço de um livro."""
    id_livro = int(input("ID do livro a ser atualizado: "))
    novo_preco = float(input("Novo preço: "))
    cursor.execute('UPDATE livros SET preco = ? WHERE id = ?', (novo_preco, id_livro))
    conn.commit()
    if cursor.rowcount > 0:
        print("Preço atualizado com sucesso!")
        fazer_backup()
    else:
        print("Livro não encontrado.")

def remover_livro():
    """Remove um livro do banco de dados."""
    id_livro = int(input("ID do livro a ser removido: "))
    cursor.execute('DELETE FROM livros WHERE id = ?', (id_livro,))
    conn.commit()
    if cursor.rowcount > 0:
        print("Livro removido com sucesso!")
        fazer_backup()
    else:
        print("Livro não encontrado.")

def buscar_por_autor():
    """Busca livros por autor."""
    autor = input("Digite o nome do autor: ")
    cursor.execute('SELECT * FROM livros WHERE autor = ?', (autor,))
    livros = cursor.fetchall()
    if livros:
        for livro in livros:
            print(f"ID: {livro[0]}, Título: {livro[1]}, Autor: {livro[2]}, Ano: {livro[3]}, Preço: R$ {livro[4]:.2f}")
    else:
        print("Nenhum livro encontrado para o autor informado.")

def exportar_para_csv():
    """Exporta os dados do banco de dados para um arquivo CSV."""
    cursor.execute('SELECT * FROM livros')
    livros = cursor.fetchall()
    csv_path = EXPORTS_DIR / 'livros_exportados.csv'
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['id', 'titulo', 'autor', 'ano_publicacao', 'preco'])
        writer.writerows(livros)
    print(f"Dados exportados para {csv_path}")

def importar_de_csv():
    """Importa dados de um arquivo CSV para o banco de dados."""
    csv_path = input("Caminho para o arquivo CSV: ")
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Pula o cabeçalho
        for row in reader:
            cursor.execute('''
                INSERT INTO livros (id, titulo, autor, ano_publicacao, preco)
                VALUES (?, ?, ?, ?, ?)
            ''', row)
    conn.commit()
    print("Dados importados com sucesso!")
    fazer_backup()

def fazer_backup():
    """Faz um backup do banco de dados."""
    import shutil
    from datetime import datetime

    backup_filename = f"backup_livraria_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.db"
    backup_path = BACKUP_DIR / backup_filename
    shutil.copy2(DB_PATH, backup_path)
    print(f"Backup realizado em {backup_path}")
    limpar_backups_antigos()

def limpar_backups_antigos():
    """Mantém apenas os 5 backups mais recentes."""
    backups = sorted(BACKUP_DIR.glob('*.db'), key=os.path.getmtime, reverse=True)
    for backup in backups[5:]:
        backup.unlink()

while True:
    print("\nMenu:")
    print("1. Adicionar novo livro")
    print("2. Exibir todos os livros")
    print("3. Atualizar preço de um livro")
    print("4. Remover um livro")
    print("5. Buscar livros por autor")
    print("6. Exportar dados para CSV")
    print("7. Importar dados de CSV")
    print("8. Fazer backup do banco de dados")
    print("9. Sair")

    opcao = input("Escolha uma opção: ")

    if opcao == '1':
        adicionar_livro()
    elif opcao == '2':
        exibir_livros()
    elif opcao == '3':
        atualizar_preco()
    elif opcao == '4':
        remover_livro()
    elif opcao == '5':
        buscar_por_autor()
    elif opcao == '6':
        exportar_para_csv()
    elif opcao == '7':
        importar_de_csv()
    elif opcao == '8':
        fazer_backup()
    elif opcao == '9':
        break
    else:
        print("Opção inválida.")

conn.close()