import os
import shutil
import threading
from datetime import datetime
from pathlib import Path
from tkinter import *
from tkinter import ttk, filedialog, messagebox, scrolledtext

class LimpezaArquivosGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Limpeza de Arquivos Antigos")
        self.root.geometry("700x600")
        
        # Variáveis
        self.diretorio_var = StringVar()
        self.ano_var = StringVar(value="2022")
        self.executando = False
        
        self.setup_ui()
    
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(N, W, E, S))
        
        # Título
        ttk.Label(main_frame, text="LIMPEZA DE ARQUIVOS ANTIGOS", 
                 font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Seção de configuração
        config_frame = ttk.LabelFrame(main_frame, text="Configurações", padding="10")
        config_frame.grid(row=1, column=0, columnspan=3, sticky=(W, E), pady=(0, 10))
        
        # Diretório
        ttk.Label(config_frame, text="Diretório:").grid(row=0, column=0, sticky=W, pady=5)
        ttk.Entry(config_frame, textvariable=self.diretorio_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(config_frame, text="Procurar...", command=self.selecionar_diretorio).grid(row=0, column=2, padx=5, pady=5)
        
        # Ano limite
        ttk.Label(config_frame, text="Ano limite:").grid(row=1, column=0, sticky=W, pady=5)
        ano_spinbox = ttk.Spinbox(config_frame, from_=2000, to=2030, textvariable=self.ano_var, width=10)
        ano_spinbox.grid(row=1, column=1, sticky=W, padx=5, pady=5)
        ttk.Label(config_frame, text="(mover arquivos até 31/12 deste ano)").grid(row=1, column=1, sticky=E, padx=(100,0))
        
        # Área de log
        ttk.Label(main_frame, text="Log de Execução:").grid(row=2, column=0, sticky=W, pady=(10, 0))
        
        # ScrolledText para logs
        self.log_text = scrolledtext.ScrolledText(main_frame, width=80, height=20, state='disabled')
        self.log_text.grid(row=3, column=0, columnspan=3, pady=(5, 10))
        
        # Barra de progresso
        self.progress_var = DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=4, column=0, columnspan=3, sticky=(W, E), pady=(0, 10))
        
        # Botões
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=10)
        
        self.executar_btn = ttk.Button(button_frame, text="EXECUTAR LIMPEZA", 
                                      command=self.executar_limpeza, state='disabled')
        self.executar_btn.pack(side=LEFT, padx=5)
        
        ttk.Button(button_frame, text="LIMPAR LOG", command=self.limpar_log).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="SAIR", command=self.root.quit).pack(side=LEFT, padx=5)
        
        # Atualizar estado do botão
        self.diretorio_var.trace('w', self.validar_campos)
        self.ano_var.trace('w', self.validar_campos)
        
        # Configurar expansão
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
    
    def selecionar_diretorio(self):
        diretorio = filedialog.askdirectory(title="Selecione o diretório para limpeza")
        if diretorio:
            self.diretorio_var.set(diretorio)
            self.log(f"Diretório selecionado: {diretorio}")
    
    def validar_campos(self, *args):
        diretorio = self.diretorio_var.get()
        ano = self.ano_var.get()
        
        if diretorio and ano.isdigit() and 2000 <= int(ano) <= 2030:
            self.executar_btn.config(state='normal')
        else:
            self.executar_btn.config(state='disabled')
    
    def log(self, mensagem):
        self.log_text.config(state='normal')
        self.log_text.insert(END, f"{mensagem}\n")
        self.log_text.see(END)
        self.log_text.config(state='disabled')
        self.root.update_idletasks()
    
    def limpar_log(self):
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, END)
        self.log_text.config(state='disabled')
    
    def executar_limpeza(self):
        if self.executando:
            return
        
        diretorio = self.diretorio_var.get()
        ano_limite = int(self.ano_var.get())
        
        # Confirmar
        resposta = messagebox.askyesno(
            "Confirmar",
            f"Esta operação irá:\n\n"
            f"1. Percorrer TODAS as subpastas de:\n{diretorio}\n"
            f"2. Criar uma pasta 'excluir' no diretório principal\n"
            f"3. Mover TODOS os arquivos antigos (até 31/12/{ano_limite}) para esta pasta\n\n"
            f"Deseja continuar?"
        )
        
        if not resposta:
            return
        
        # Desabilitar botão durante execução
        self.executando = True
        self.executar_btn.config(state='disabled', text="EXECUTANDO...")
        self.progress_var.set(0)
        
        # Executar em thread separada para não travar a interface
        thread = threading.Thread(
            target=self.executar_limpeza_thread,
            args=(diretorio, ano_limite),
            daemon=True
        )
        thread.start()
    
    def executar_limpeza_thread(self, diretorio_base, ano_limite):
        try:
            self.log("=" * 60)
            self.log("INICIANDO LIMPEZA DE ARQUIVOS ANTIGOS")
            self.log("=" * 60)
            
            # Converte para Path object
            base_path = Path(diretorio_base)
            
            # Verifica se o diretório base existe
            if not base_path.exists():
                self.log(f"ERRO: Diretório não encontrado: {base_path}")
                messagebox.showerror("Erro", f"Diretório não encontrado:\n{base_path}")
                return
            
            # Cria a pasta 'excluir' no diretório principal
            excluir_dir = base_path / "excluir"
            excluir_dir.mkdir(exist_ok=True)
            
            # Data limite: 31 de dezembro do ano limite
            data_limite = datetime(ano_limite, 12, 31, 23, 59, 59)
            
            # Contadores
            total_arquivos_movidos = 0
            total_pastas_movidas = 0
            
            self.log(f"Diretório base: {base_path}")
            self.log(f"Data limite: até {data_limite.strftime('%d/%m/%Y')}")
            self.log(f"Pasta 'excluir' central: {excluir_dir}")
            self.log("=" * 60)
            
            # Coletar todos os arquivos primeiro para estimar progresso
            self.log("Coletando informações dos arquivos...")
            todos_arquivos = []
            for raiz, dirs, arquivos in os.walk(base_path):
                # Ignora a pasta 'excluir'
                if 'excluir' in raiz:
                    continue
                
                for arquivo in arquivos:
                    caminho_completo = Path(raiz) / arquivo
                    todos_arquivos.append(caminho_completo)
            
            total_arquivos = len(todos_arquivos)
            self.log(f"Total de arquivos a verificar: {total_arquivos}")
            
            # Processar arquivos
            for i, caminho_arquivo in enumerate(todos_arquivos):
                try:
                    # Atualizar progresso
                    if total_arquivos > 0:
                        progresso = (i + 1) / total_arquivos * 100
                        self.progress_var.set(progresso)
                    
                    # Obtém a data de modificação
                    mod_time = datetime.fromtimestamp(caminho_arquivo.stat().st_mtime)
                    
                    # Verifica se é antigo
                    if mod_time <= data_limite:
                        # Cria um nome único baseado no caminho relativo
                        caminho_relativo = caminho_arquivo.relative_to(base_path)
                        nome_unico = str(caminho_relativo).replace('\\', '_').replace('/', '_')
                        
                        # Se o nome for muito longo, truncamos
                        if len(nome_unico) > 200:
                            nome_base = caminho_arquivo.stem
                            extensao = caminho_arquivo.suffix
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            nome_unico = f"{nome_base}_{timestamp}{extensao}"
                        
                        destino = excluir_dir / nome_unico
                        
                        # Se já existir, adiciona um número
                        contador = 1
                        while destino.exists():
                            novo_nome = f"{caminho_arquivo.stem}_{contador}{caminho_arquivo.suffix}"
                            destino = excluir_dir / novo_nome
                            contador += 1
                        
                        # Move o arquivo
                        shutil.move(str(caminho_arquivo), str(destino))
                        total_arquivos_movidos += 1
                        
                        if total_arquivos_movidos % 100 == 0:
                            self.log(f"  Arquivos movidos: {total_arquivos_movidos}...")
                    
                except Exception as e:
                    self.log(f"  ✗ Erro ao processar {caminho_arquivo.name}: {e}")
            
            # Verificar pastas vazias
            self.log("\n" + "-" * 60)
            self.log("Verificando pastas vazias antigas...")
            self.log("-" * 60)
            
            todas_pastas = []
            for raiz, dirs, arquivos in os.walk(base_path):
                diretorio_atual = Path(raiz)
                
                # Ignora a pasta 'excluir' principal
                if diretorio_atual == excluir_dir or excluir_dir in diretorio_atual.parents:
                    continue
                
                # Verifica se o diretório está vazio
                if not any(diretorio_atual.iterdir()):
                    todas_pastas.append(diretorio_atual)
            
            # Processar pastas vazias
            for pasta in todas_pastas:
                try:
                    mod_time = datetime.fromtimestamp(pasta.stat().st_mtime)
                    
                    if mod_time <= data_limite:
                        # Cria registro da pasta vazia
                        caminho_relativo = pasta.relative_to(base_path)
                        nome_unico = str(caminho_relativo).replace('\\', '_').replace('/', '_')
                        
                        registro_pasta = excluir_dir / f"PASTA_VAZIA_{nome_unico}.txt"
                        
                        with open(registro_pasta, 'w', encoding='utf-8') as f:
                            f.write(f"Pasta original: {pasta}\n")
                            f.write(f"Data de modificação: {mod_time}\n")
                            f.write(f"Data da movimentação: {datetime.now()}\n")
                        
                        # Remove a pasta vazia
                        pasta.rmdir()
                        total_pastas_movidas += 1
                        
                except Exception as e:
                    self.log(f"  ✗ Erro ao processar pasta {pasta.name}: {e}")
            
            # Relatório final
            self.log("\n" + "=" * 60)
            self.log("RELATÓRIO FINAL")
            self.log("=" * 60)
            self.log(f"✓ Total de arquivos movidos: {total_arquivos_movidos}")
            self.log(f"✓ Total de pastas registradas como vazias: {total_pastas_movidas}")
            self.log(f"✓ Pasta de destino: {excluir_dir}")
            self.log("\n✅ Processo concluído com sucesso!")
            self.log("=" * 60)
            
            # Mostrar mensagem de conclusão
            self.root.after(0, lambda: messagebox.showinfo(
                "Concluído",
                f"Limpeza concluída!\n\n"
                f"Arquivos movidos: {total_arquivos_movidos}\n"
                f"Pastas vazias registradas: {total_pastas_movidas}\n"
                f"Pasta 'excluir': {excluir_dir}"
            ))
            
        except Exception as e:
            self.log(f"\n❌ ERRO: {e}")
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Ocorreu um erro:\n{str(e)}"))
        
        finally:
            # Reabilitar botão
            self.root.after(0, self.finalizar_execucao)
    
    def finalizar_execucao(self):
        self.executando = False
        self.executar_btn.config(state='normal', text="EXECUTAR LIMPEZA")
        self.progress_var.set(100)

def main():
    root = Tk()
    app = LimpezaArquivosGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()