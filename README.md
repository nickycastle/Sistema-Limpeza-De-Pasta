🧹 Limpeza de Arquivos Antigos (Python)

Aplicação desktop em Python + Tkinter para organizar e limpar diretórios, movendo arquivos antigos para uma pasta central de forma segura e automatizada.

📋 Funcionalidades

Interface gráfica simples

Seleção de diretório

Definição de ano limite

Movimentação de arquivos antigos

Criação automática da pasta excluir

Registro de pastas vazias

Log detalhado da execução

Barra de progresso

Execução em thread (não trava a UI)

⚙️ Regras

Arquivos com data de modificação até 31/12 do ano informado são movidos

A pasta excluir é ignorada no processamento

Arquivos com nomes duplicados recebem sufixos automáticos

Pastas vazias antigas são removidas e registradas em .txt

🚀 Como Executar
python main.py


Selecione o diretório

Informe o ano limite

Clique em EXECUTAR LIMPEZA

🧩 Tecnologias

Python 3

Tkinter

Threading

Pathlib

(Bibliotecas nativas)

📊 Resultado

Ao final da execução:

Total de arquivos movidos

Total de pastas vazias registradas

Caminho da pasta excluir

📄 Licença

Projeto para fins educacionais e uso interno.
