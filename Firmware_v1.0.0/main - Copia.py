# pyinstaller --onefile main.py

import os
import sys
import time
import shutil
import ctypes
import filecmp
import configparser
import PIL.Image
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pystray import Icon, Menu, MenuItem


config = configparser.ConfigParser()

source_folder = None
backup_folder = None
backup = False

ctypes.windll.kernel32.SetConsoleTitleW(
    'Monitoramento Auto Backup - DALCOQUIO AUTOMACAO')

# Função para gravar dados em config.ini
def write_config(_source, _backup):
    # Adicionar seções e atributos
    config['FOLDER'] = {
        'source': _source,
        'backup': _backup,
    }
    # Gravar no arquivo
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

# Função para ler dados em config.ini
def read_config():
    # Ler dados do arquivo
    config.read('config.ini')
    # Acessar os valores
    global source_folder
    global backup_folder
    source_folder = config['FOLDER']['source']
    backup_folder = config['FOLDER']['backup']

def auto_backup():
    # Iniciar o monitoramento de auto-backup
    os.system('cls')
    read_config() # Busca endereço de origem e backup em config.ini
    event_handler = BackupHandler(source_folder, backup_folder)
    observer = Observer()
    observer.schedule(event_handler, source_folder, recursive=True)

    try:
        observer.start()
        print(f'Monitorando alterações em: {source_folder}')
        icon.run()
        while running:
            time.sleep(1)  # Mantém o programa rodando
        sys.exit() # Fecha o aplicativo de auto-backup
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

class BackupHandler(FileSystemEventHandler):
    def __init__(self, source_folder, backup_folder):
        self.source_folder = source_folder
        self.backup_folder = backup_folder
        if backup == True :
            self.sync_initial()  # Chama a função de sincronização inicial

    def on_modified(self, event):
        # Verifica se o evento é um arquivo (não uma pasta)
        if not event.is_directory:
            self.backup_file(event.src_path)

    def on_created(self, event):
        # Também faz backup se um novo arquivo for criado
        if not event.is_directory:
            self.backup_file(event.src_path)

    def on_deleted(self, event):
        # Se o arquivo ou pasta foi excluído, exclui do backup também
        if not event.is_directory:
            self.delete_backup_file(event.src_path)
        else:
            self.delete_backup_directory(event.src_path)

    def on_moved(self, event):
        # Se o arquivo ou pasta foi movido (renomeado)
        if not event.is_directory:
            self.rename_backup_file(event.src_path, event.dest_path)
        else:
            self.rename_backup_directory(event.src_path, event.dest_path)

    def backup_file(self, file_path):
        # Define o caminho do arquivo de backup
        relative_path = os.path.relpath(file_path, self.source_folder)
        backup_path = os.path.join(self.backup_folder, relative_path)

        # Cria diretórios se não existirem
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)

        # Copia o arquivo para a pasta de backup
        shutil.copy2(file_path, backup_path)
        print(f'Backup realizado: {file_path} -> {backup_path}')

    def delete_backup_file(self, file_path):
        # Define o caminho do arquivo no backup
        relative_path = os.path.relpath(file_path, self.source_folder)
        backup_path = os.path.join(self.backup_folder, relative_path)

        # Verifica se o arquivo existe no backup e o exclui
        if os.path.exists(backup_path):
            os.remove(backup_path)
            print(f'Arquivo excluído do backup: {backup_path}')
        else:
            print(f'Arquivo não encontrado no backup: {backup_path}')

    def delete_backup_directory(self, dir_path):
        # Define o caminho do diretório no backup
        relative_path = os.path.relpath(dir_path, self.source_folder)
        backup_path = os.path.join(self.backup_folder, relative_path)

        # Verifica se o diretório existe no backup e o exclui
        if os.path.exists(backup_path):
            shutil.rmtree(backup_path)
            print(f'Diretório excluído do backup: {backup_path}')
        else:
            print(f'Diretório não encontrado no backup: {backup_path}')

    def rename_backup_file(self, old_file_path, new_file_path):
        # Define os caminhos relativos
        old_relative_path = os.path.relpath(old_file_path, self.source_folder)
        new_relative_path = os.path.relpath(new_file_path, self.source_folder)

        # Define os caminhos completos no backup
        old_backup_path = os.path.join(self.backup_folder, old_relative_path)
        new_backup_path = os.path.join(self.backup_folder, new_relative_path)

        # Renomeia o arquivo no backup
        if os.path.exists(old_backup_path):
            os.rename(old_backup_path, new_backup_path)
            print(f'Arquivo renomeado no backup: {old_backup_path} -> {new_backup_path}')
        else:
            print(f'Arquivo não encontrado no backup para renomear: {old_backup_path}')

    def rename_backup_directory(self, old_dir_path, new_dir_path):
        # Define os caminhos relativos
        old_relative_path = os.path.relpath(old_dir_path, self.source_folder)
        new_relative_path = os.path.relpath(new_dir_path, self.source_folder)

        # Define os caminhos completos no backup
        old_backup_path = os.path.join(self.backup_folder, old_relative_path)
        new_backup_path = os.path.join(self.backup_folder, new_relative_path)

        # Renomeia o diretório no backup
        if os.path.exists(old_backup_path):
            os.rename(old_backup_path, new_backup_path)
            print(f'Diretório renomeado no backup: {old_backup_path} -> {new_backup_path}')
        else:
            print(f'Diretório não encontrado no backup para renomear: {old_backup_path}')
            
    def sync_initial(self):
        inicio = time.time()
        print("Iniciando backup total, isso poderá demorar um pouco, aguarde...")
        # Sincroniza a pasta de origem com o backup no início
        for root, dirs, files in os.walk(self.source_folder):
            for dir in dirs:
                source_dir = os.path.join(root, dir)
                backup_dir = os.path.join(self.backup_folder, os.path.relpath(source_dir, self.source_folder))
                if not os.path.exists(backup_dir):
                    shutil.copytree(source_dir, backup_dir, dirs_exist_ok=True)
                    print(f'Pasta sincronizada (inicial): {source_dir} -> {backup_dir}')

            for file in files:
                source_file = os.path.join(root, file)
                backup_file = os.path.join(self.backup_folder, os.path.relpath(source_file, self.source_folder))
                if not os.path.exists(backup_file):
                    shutil.copy2(source_file, backup_file)
                    print(f'Arquivo sincronizado (inicial): {source_file} -> {backup_file}')
        fim = time.time()
        tempo = fim -inicio
        print("Tempo de backup: ", tempo, " segundos")
        print("Backup total finalizado com sucesso, iniciando o monitoramento de backup.../n")        
        
# Funções referente ao icone stray
def open_backup(icon):
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd:
        ctypes.windll.user32.ShowWindow(hwnd, 1) # 0 = mostra console

def close_backup(icon):
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd:
        ctypes.windll.user32.ShowWindow(hwnd, 0) # 0 = oculta console

def exit_backup(icon):
    icon.stop()
    global running
    running = False # Para encerrar o loop principal
    print("Finalizando monitoramento de backup...")
    time.sleep(2)

# Busca a imagem e cria o icone
image = PIL.Image.open("bug_red.ico")
icon = Icon("Auto Backup", image, menu=Menu(MenuItem("Close Backup", close_backup),
MenuItem("Open Backup", open_backup), MenuItem("Exit Backup", exit_backup)))

def main():
    global running  # Define a variável global para controlar o loop principal
    running = True
    while running:
        # Menu de opções
        read_config()
        global source_folder
        global backup_folder
        print(f"Endereço de origem: {source_folder}")
        print(f"Endereço de backup: {backup_folder}")
        print("\nMenu:")
        print("1. Alterar endereço de origem")
        print("2. Alterar endereço de backup")
        print("3. Iniciar monitoramento de backup")
        print("4. Iniciar backup total + monitoramento de backup")
        opcao = input("\nDigite uma opção: ")

        # Tratamento da opção selecionada
        if opcao == '1' :
            source_folder = input("Digite o endereço de origem: ")
            write_config(source_folder, backup_folder)
        if opcao == '2' :
            backup_folder = input("Digite o endereço de backup: ")
            write_config(source_folder, backup_folder)
        if opcao == '3' :
            global backup
            backup = False
            auto_backup()
        if opcao == '4' :
            backup = True
            auto_backup()
        else:
            os.system('cls')
            print("Opção digitada inválida !!!\n")

if __name__ == "__main__":
    main()
    
