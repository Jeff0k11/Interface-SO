import psutil
import tkinter as tk
from tkinter import ttk
import GPUtil

def listar_processos():
    """Obtém uma lista dos processos em execução com informações de uso de CPU, memória, disco e GPU."""
    processos = []
    for processo in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            info = processo.info
            # Adiciona uso de disco
            info['disk_percent'] = processo.io_counters().write_bytes if processo.io_counters() else 0
            processos.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # Obter o uso de GPU usando GPUtil
    gpus = GPUtil.getGPUs()
    for i, processo in enumerate(processos):
        if gpus:
            # Atribui o uso de GPU (simplesmente usa a primeira GPU encontrada como exemplo)
            processo['gpu_percent'] = gpus[0].load * 100
        else:
            processo['gpu_percent'] = 0.0  # Caso não haja GPU ou suporte da biblioteca

    return processos

def atualizar_tabela():
    """Atualiza a tabela com dados reais dos processos em execução, incluindo CPU, Memória, Disco e GPU."""
    for row in tabela.get_children():
        tabela.delete(row)

    processos = listar_processos()
    for processo in processos:
        tabela.insert(
            "", 
            "end", 
            values=(
                processo['pid'], 
                processo['name'], 
                f"{processo['cpu_percent']:.2f}%", 
                f"{processo['memory_percent']:.2f}%", 
                f"{processo['disk_percent'] / (1024 * 1024):.2f} MB",  # Exibindo em MB
                f"{processo['gpu_percent']:.2f}%"
            )
        )

    root.after(2000, atualizar_tabela)

# Configuração da interface gráfica
root = tk.Tk()
root.title("Gerenciador de Tarefas")
root.geometry("800x400")

# Estilos usando ttk.Style()
style = ttk.Style()
style.theme_use("clam")  # Use o tema 'clam' para mais opções de estilo
style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"), background="#4CAF50", foreground="white")
style.configure("Treeview", font=("Helvetica", 9), background="#f0f0f0", fieldbackground="#f0f0f0", foreground="#333")
style.map("Treeview", background=[("selected", "#4CAF50")], foreground=[("selected", "white")])

# Configuração da tabela
colunas = ("PID", "Nome", "CPU (%)", "Memória (%)", "Disco (MB)", "GPU (%)")
tabela = ttk.Treeview(root, columns=colunas, show="headings", height=15)
for col in colunas:
    tabela.heading(col, text=col)

# Configurações de largura das colunas para ajuste horizontal
tabela.column("PID", width=60)
tabela.column("Nome", width=250)
tabela.column("CPU (%)", width=100)
tabela.column("Memória (%)", width=100)
tabela.column("Disco (MB)", width=100)
tabela.column("GPU (%)", width=100)

# Barra de rolagem horizontal
scrollbar_x = ttk.Scrollbar(root, orient="horizontal", command=tabela.xview)
tabela.configure(xscroll=scrollbar_x.set)
scrollbar_x.pack(side="bottom", fill="x")

# Barra de rolagem vertical
scrollbar_y = ttk.Scrollbar(root, orient="vertical", command=tabela.yview)
tabela.configure(yscroll=scrollbar_y.set)
scrollbar_y.pack(side="right", fill="y")

# Empacota a tabela na janela principal
tabela.pack(fill=tk.BOTH, expand=True)

# Inicia a atualização da tabela
atualizar_tabela()

root.mainloop()
