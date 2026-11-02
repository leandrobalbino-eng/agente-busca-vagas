# 🤖 Agente de IA para Busca de Vagas

Um agente autônomo desenvolvido em Python que varre a internet em busca de vagas de tecnologia (Júnior/Estágio/Trainee), analisa a compatibilidade com o perfil do candidato e gera cartas de apresentação personalizadas.

## 🚀 Tecnologias Utilizadas
*   **Python 3.12**
*   **CrewAI**: Orquestração de agentes de IA (Pesquisador, Analista e Redator).
*   **DeepSeek API**: LLM utilizado para análise e geração de texto.
*   **CustomTkinter**: Interface gráfica moderna e em tela cheia.
*   **DuckDuckGo Search (ddgs)**: Motor de busca web.

## ⚙️ Como Executar o Projeto

1. Clone o repositório:
   ```bash
   git clone https://github.com/leandrobalbino-eng/agente-busca-vagas.git

GUIA DE INSTALAÇÃO E USO

 Guia de Instalação e Uso (Para quem baixar o projeto)
Olá! Se você baixou este projeto, siga os passos abaixo para fazer o Agente de Busca de Vagas funcionar. O agente precisa de uma chave de API da DeepSeek para que os modelos de Inteligência Artificial possam "pensar" e analisar as vagas.

Requisitos
Ter uma conta gratuita na DeepSeek.

Saldo disponível na conta (a API da DeepSeek é paga por uso, mas os custos para rodar este agente são muito baixos, geralmente frações de centavos por busca).

Opção A: Usando o Executável (.exe) - Mais Fácil
Se você baixou o arquivo interface.exe na aba Releases deste repositório, siga estes passos:

Crie uma pasta: Coloque o arquivo interface.exe dentro de uma pasta vazia no seu computador.

Obtenha sua chave:

Acesse platform.deepseek.com.

Vá em "API Keys" no menu lateral.

Clique em "Create new API key", copie a chave gerada (ela começa com sk-...) e guarde-a.

Crie o arquivo de configuração:

Dentro da mesma pasta onde está o interface.exe, crie um arquivo de texto chamado exatamente .env (com o ponto no início e sem .txt no final).

Abra esse arquivo no Bloco de Notas e cole a sua chave no seguinte formato:

env
DEEPSEEK_API_KEY=sk-sua-chave-copiada-aqui
Salve e feche o arquivo.

Execute: Dê um duplo clique no interface.exe. A janela do agente vai abrir e você já pode clicar em "Iniciar Busca".

Opção B: Usando o Código-Fonte (Python) - Para Desenvolvedores
Se você clonou o repositório e quer rodar o código em Python, siga estes passos:

Clone o repositório:

bash
git clone https://github.com/leandrobailbino-eng/agente-busca-vagas.git
cd agente-busca-vagas
Crie e ative um ambiente virtual:

bash
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
Instale as dependências:

bash
pip install -r requirements.txt
Configure a chave da API:

Renomeie o arquivo env.example (que está no repositório) para .env.

Abra o .env e substitua sua_chave_aqui pela sua chave real da DeepSeek.

Execute o agente:

bash
python job_hunter.py
(Ou, para abrir a interface gráfica, rode python interface.py).

⚠️ Aviso de Segurança Importante
NUNCA faça commit do seu arquivo .env em repositórios públicos. A sua chave de API é pessoal e intransferível. Se você acidentalmente expor a sua chave, vá imediatamente ao site da DeepSeek e delete-a, gerando uma nova em seguida. O arquivo .env já está listado no .gitignore deste projeto para evitar vazamentos.

