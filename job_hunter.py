#!/usr/bin/env python3
"""
============================================================
AGENTE DE IA AUTÔNOMO - BUSCA E CANDIDATURA A VAGAS
============================================================
Candidato: Leandro Balbino Santos de Moraes
Perfil: Estudante finalista de Ciência da Computação
Foco: Vagas Júnior / Estágio / Trainee em Tech (SP ou Remoto)

Uso:
    1. pip install -r requirements.txt (ou instalar manualmente)
    2. Criar arquivo .env com DEEPSEEK_API_KEY=sk-...
    3. python job_hunter.py

Autor: Gerado como MVP executável
============================================================
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import Type

# ============================================================
# VERIFICAÇÃO DE DEPENDÊNCIAS (falha cedo com mensagem clara)
# ============================================================
try:
    from dotenv import load_dotenv
    from pydantic import BaseModel, Field
    from ddgs import DDGS
    from crewai import Agent, Task, Crew, Process, LLM
    from crewai.tools import BaseTool
except ImportError as e:
    print(f"❌ Dependência faltando: {e}")
    print("\n📦 Instale com:")
    print("   pip install crewai crewai-tools duckduckgo-search python-dotenv pydantic")
    sys.exit(1)


# ============================================================
# 1. CONFIGURAÇÃO
# ============================================================
load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL = "deepseek-flash"

CANDIDATE_PROFILE = {
    "nome": "Leandro Balbino Santos de Moraes",
    "formacao": "Estudante finalista de Bacharelado em Ciência da Computação",
    "nivel": "Entry-Level / Júnior / Estágio Avançado / Trainee",
    "tecnologias": ["Python", "HTML/CSS/JS", "APIs REST", "SQL básico"],
    "interesses": ["Desenvolvimento Web", "Funcionalidades de IA", "Arquitetura de Sistemas/Nuvem"],
    "localizacao": "São Paulo (capital) ou Remoto",
    "modalidade": "Presencial, Híbrido ou Remoto",
}

PROMPT_PESQUISADOR = """
Você é um recrutador técnico especializado em vagas de tecnologia para iniciantes.

Sua tarefa: usar a ferramenta JobSearchTool para encontrar vagas RECENTES
que correspondam ao perfil do candidato.

## Queries obrigatórias (execute TODAS, uma por vez, nesta ordem):
1. "site:gupy.io estágio desenvolvimento são paulo"
2. "site:gupy.io vaga júnior desenvolvedor são paulo"
3. "site:gupy.io trainee tecnologia são paulo"
4. "site:gupy.io desenvolvedor júnior remoto"
5. "site:sidi.gupy.io estágio são paulo"
6. "site:b4a.gupy.io estágio são paulo"
7. "site:devvagas.com.br júnior são paulo"
8. "vaga júnior python são paulo capital"

## Limite de buscas:
- Execute NO MÁXIMO as 8 queries acima. NÃO invente queries extras.
- Se uma query retornar erro ou vazio, siga para a próxima.

## 🚨 REGRA DE LOCALIZAÇÃO — A MAIS IMPORTANTE 🚨

**ACEITE APENAS:**
- ✅ São Paulo (CAPITAL) — presencial, híbrido ou remoto
- ✅ 100% Remoto (qualquer lugar do Brasil, desde que seja remoto)

**DESCARTE IMEDIATAMENTE (SEM EXCEÇÃO):**
- ❌ Campinas/SP (NUNCA aceite Campinas)
- ❌ Rio de Janeiro, Belo Horizonte, Curitiba, Porto Alegre
- ❌ São Paulo (interior) — Barueri, Osasco, Guarulhos, ABC Paulista
- ❌ Qualquer outra cidade que NÃO seja a capital São Paulo

**Como verificar antes de aceitar:**
1. Leia o snippet da vaga com atenção.
2. Se aparecer "Campinas", "Campinas/SP", "regime presencial em Campinas",
   ou qualquer menção a outra cidade → **DESCARTE a vaga**.
3. Se aparecer "São Paulo", "São Paulo/SP", "capital", "remoto", "home office",
   "100% remoto" → **ACEITE a vaga**.
4. Se a localização NÃO estiver clara no snippet → **DESCARTE** (não assuma).
5. Exceção: se a vaga for explicitamente "100% remoto" ou "home office",
   ACEITE mesmo que a empresa esteja sediada em Campinas.

## Regras de filtragem:
- DESCARTE páginas institucionais, tutoriais, documentação e agregadores
  (python.org, w3schools, microsoft.com, querobolsa, etc.).
- DESCARTE páginas-índice de agregadores (Glassdoor, Indeed, LinkedIn
  quando o link for uma listagem genérica, não um anúncio específico).
- ACEITE apenas ANÚNCIOS DE VAGA individuais, com título do cargo,
  empresa e link direto para a vaga.

## Regras de nível:
- ACEITE apenas vagas de nível: Júnior, Estágio ou Trainee.
- DESCARTE vagas Sênior, Especialista, Lead, Coordenador ou que peçam
  "5+ anos de experiência".

## Formato de saída:
Retorne uma lista JSON com as vagas válidas, cada uma contendo:
- titulo: título da vaga
- empresa: nome da empresa (se visível)
- link: URL direta para a vaga
- snippet: trecho da descrição
- localizacao: "São Paulo (capital)" ou "Remoto"
- nivel: "Júnior" | "Estágio" | "Trainee"
- fonte: "Gupy" | "DevVagas" | "Outro"

## Validação final (OBRIGATÓRIA):
Antes de retornar a lista, revise CADA vaga e confirme:
- [ ] A localização é São Paulo (capital) ou 100% Remota?
- [ ] A vaga NÃO menciona Campinas, Rio, BH, Curitiba, Porto Alegre
      ou outra cidade que não seja São Paulo capital?
- [ ] O nível é Júnior, Estágio ou Trainee?
- [ ] O link é um anúncio individual (não uma listagem)?

Se QUALQUER resposta for "não", REMOVA a vaga da lista final.

Se após as 8 buscas não houver nenhuma vaga válida, retorne lista vazia
e explique o motivo (ex: "Todas as vagas encontradas eram de Campinas/SP"
ou "Todas as buscas retornaram vazio").
"""

PROMPT_ANALISTA = """
Você é um analista de compatibilidade de vagas.

Receba a descrição de uma vaga e o perfil do candidato. Calcule uma pontuação de 0 a 100:

1. Nível de experiência (peso 30%):
   - 100 se "Júnior/Estágio/Trainee"
   - 50 se não especificar
   - 0 se "Sênior/Especialista"

2. Tecnologias (peso 30%):
   - Python: +30 | Web (HTML/CSS/JS): +20 | IA/ML: +20 | Cloud: +20

3. Localização/Modalidade (peso 20%):
   - SP capital ou Remoto: 100 | Híbrido em SP: 80 | Presencial fora de SP: 20

4. Área de interesse (peso 20%):
   - Desenvolvimento: 100 | Dados/IA: 90 | Infraestrutura: 70

Saída esperada (JSON):
{"compatibilidade": 85, "justificativa": "...", "aprovada": true}

Aprove apenas vagas com compatibilidade >= 70.
"""

PROMPT_REDATOR = """
Você é um redator profissional de cartas de apresentação.

Gere uma Cover Letter personalizada em português (máx. 200 palavras) que:
1. Mencione o nome da empresa e o título da vaga.
2. Destaque 2-3 tecnologias do perfil relevantes.
3. Expresse entusiasmo genuíno pela oportunidade.
4. Tenha tom profissional mas acessível.
"""


# ============================================================
# 2. FERRAMENTAS CUSTOMIZADAS
# ============================================================
class JobSearchInput(BaseModel):
    """Input para a ferramenta de busca de vagas."""
    query: str = Field(..., description="Termo de busca para encontrar vagas")


# Domínios que NÃO são anúncios de vaga (tutoriais, documentação, agregadores)
DOMINIOS_IRRELEVANTES = [
    "python.org", "w3schools.com", "microsoft.com", "programiz.com",
    "online-python.com", "onlinegdb.com", "onecompiler.com", "wikipedia.org",
    "querobolsa.com.br", "orientacarreira.com.br", "reclameaqui.com.br",
]


class JobSearchTool(BaseTool):
    name: str = "JobSearchTool"
    description: str = (
        "Busca vagas de emprego no DuckDuckGo. Retorna lista com título, link e snippet. "
        "Use queries curtas como 'estágio desenvolvimento são paulo' ou "
        "'site:gupy.io estágio desenvolvimento'."
    )
    args_schema: Type[BaseModel] = JobSearchInput
    max_results: int = 8

    def _run(self, query: str) -> str:
        try:
            import time
            time.sleep(2)  # evita rate limit do DuckDuckGo

            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=self.max_results, region="br-pt"))

            if not results:
                return json.dumps({"status": "vazio", "resultados": []}, ensure_ascii=False)

            # Filtra domínios irrelevantes
            formatted = []
            for r in results:
                link = r.get("href", "")
                if any(dom in link for dom in DOMINIOS_IRRELEVANTES):
                    continue  # descarta tutorial/documentação/agregador
                formatted.append({
                    "titulo": r.get("title", ""),
                    "link": link,
                    "snippet": r.get("body", ""),
                })

            if not formatted:
                return json.dumps(
                    {"status": "vazio_filtrado", "query": query, "resultados": []},
                    ensure_ascii=False,
                )

            return json.dumps(
                {"status": "ok", "query": query, "resultados": formatted},
                ensure_ascii=False,
                indent=2,
            )
        except Exception as e:
            return json.dumps({"status": "erro", "mensagem": str(e)}, ensure_ascii=False)


# ============================================================
# 3. AGENTES
# ============================================================
def criar_llm():
    return LLM(
        model=f"openai/{DEEPSEEK_MODEL}",
        base_url=DEEPSEEK_BASE_URL,
        api_key=DEEPSEEK_API_KEY,
        temperature=0.3,
    )


def criar_agentes(llm):
    search_tool = JobSearchTool()

    pesquisador = Agent(
        role="Pesquisador de Vagas de Tecnologia",
        goal="Encontrar vagas recentes e relevantes para devs iniciantes em SP ou remotas.",
        backstory=PROMPT_PESQUISADOR,
        tools=[search_tool],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=5,
    )

    analista = Agent(
        role="Analista de Compatibilidade de Vagas",
        goal="Filtrar vagas por relevância e calcular score de 0 a 100.",
        backstory=PROMPT_ANALISTA,
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )

    redator = Agent(
        role="Redator de Cartas de Apresentação",
        goal="Gerar cover letters concisas e personalizadas.",
        backstory=PROMPT_REDATOR,
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=2,
    )

    return pesquisador, analista, redator


# ============================================================
# 4. RELATÓRIO
# ============================================================
def gerar_relatorio(resultado_final):
    import re
    os.makedirs("output/cover_letters", exist_ok=True)

    # Tenta extrair a lista JSON de vagas aprovadas do output do agente
    vagas = []
    try:
        texto = str(resultado_final)
        # Procura o primeiro array JSON que contenha "titulo" e "link"
        match = re.search(r'\[\s*\{.*?"link".*?\}\s*\]', texto, re.DOTALL)
        if match:
            vagas = json.loads(match.group())
    except Exception:
        pass

    linhas = []
    linhas.append("# 📋 Relatório de Busca de Vagas\n")
    linhas.append(f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  ")
    linhas.append(f"**Candidato:** {CANDIDATE_PROFILE['nome']}  ")
    linhas.append(f"**Nível:** {CANDIDATE_PROFILE['nivel']}  ")
    linhas.append(f"**Localização:** {CANDIDATE_PROFILE['localizacao']}\n")
    linhas.append("---\n")
    linhas.append(f"## ✅ Vagas Aprovadas ({len(vagas)})\n")

    if vagas:
        for i, v in enumerate(vagas, 1):
            titulo = v.get("titulo", "Sem título")
            link = v.get("link", "")
            score = v.get("score", "N/A")
            just = v.get("justificativa", "")
            empresa = v.get("empresa", v.get("empresa_estimada", ""))
            loc = v.get("localizacao", "")
            nivel = v.get("nivel", "")

            # Link clicável no formato Markdown
            if link:
                titulo_link = f"[{titulo}]({link})"
            else:
                titulo_link = titulo

            linhas.append(f"### {i}. {titulo_link}\n")
            if empresa:
                linhas.append(f"- **Empresa:** {empresa}")
            if loc:
                linhas.append(f"- **Localização:** {loc}")
            if nivel:
                linhas.append(f"- **Nível:** {nivel}")
            linhas.append(f"- **Score:** {score}/100")
            if link:
                linhas.append(f"- **Link direto:** <{link}>")
            if just:
                linhas.append(f"- **Justificativa:** {just}")
            linhas.append("")
    else:
        linhas.append("*Nenhuma vaga aprovada nesta execução.*\n")

    linhas.append("---\n")
    linhas.append("## 📄 Cover Letters Geradas\n")
    linhas.append("Verifique a pasta `output/cover_letters/`.\n")
    linhas.append("---\n")
    linhas.append("## 🔍 Output Bruto do Agente\n")
    linhas.append("<details>\n<summary>Clique para expandir</summary>\n")
    linhas.append("```\n" + str(resultado_final) + "\n```\n")
    linhas.append("</details>\n")
    linhas.append("---\n*Gerado automaticamente pelo Agente de IA*\n")

    caminho = "output/relatorio_vagas.md"
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))
    print(f"\n📄 Relatório salvo em: {caminho}")

# ============================================================
# 5. ORQUESTRAÇÃO PRINCIPAL
# ============================================================
def executar_agente():
    if not DEEPSEEK_API_KEY:
        print("❌ DEEPSEEK_API_KEY não configurada.")
        print("\n📝 Crie um arquivo .env na raiz do projeto com:")
        print("   DEEPSEEK_API_KEY=sk-sua-chave-aqui")
        print("\n🔑 Obtenha sua chave em: https://platform.deepseek.com")
        sys.exit(1)

    print("=" * 60)
    print("🚀 AGENTE DE BUSCA DE VAGAS - INICIANDO")
    print("=" * 60)
    print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"👤 Candidato: {CANDIDATE_PROFILE['nome']}")
    print(f"🎯 Foco: {CANDIDATE_PROFILE['nivel']}")
    print("-" * 60)

    llm = criar_llm()
    pesquisador, analista, redator = criar_agentes(llm)

    # --- Tarefa 1: Buscar ---
    tarefa_busca = Task(
        description=(
            "Execute pelo menos 4 buscas diferentes no DuckDuckGo usando a JobSearchTool. "
            "Consolide os resultados em uma lista única de vagas (evite duplicatas por link). "
            "Filtre apenas vagas de nível Júnior/Estágio/Trainee em SP ou remotas."
        ),
        expected_output=(
            "JSON com lista consolidada: [{titulo, link, snippet, empresa_estimada}]"
        ),
        agent=pesquisador,
    )

    # --- Tarefa 2: Analisar ---
    tarefa_analise = Task(
        description=(
            "Para cada vaga da tarefa anterior, calcule o score de compatibilidade (0-100). "
            "Aprove apenas score >= 70. Retorne JSON com vagas aprovadas."
        ),
        expected_output=(
            "JSON: [{titulo, link, score, justificativa}] ordenado por score decrescente."
        ),
        agent=analista,
        context=[tarefa_busca],
    )

    # --- Tarefa 3: Redigir cover letters ---
    tarefa_redacao = Task(
        description=(
            "Para cada vaga aprovada, gere uma cover letter em português (máx. 200 palavras). "
            "Salve cada carta em output/cover_letters/<empresa_ou_id>.md via código Python "
            "dentro do seu raciocínio, retornando os caminhos gerados."
        ),
        expected_output="Lista de caminhos de arquivos .md gerados.",
        agent=redator,
        context=[tarefa_analise],
    )

    crew = Crew(
        agents=[pesquisador, analista, redator],
        tasks=[tarefa_busca, tarefa_analise, tarefa_redacao],
        process=Process.sequential,
        verbose=True,
    )

    print("\n⏳ Executando a crew (isso pode levar alguns minutos)...\n")
    inicio = time.time()
    resultado = crew.kickoff()
    duracao = time.time() - inicio

    print(f"\n⏱️  Duração total: {duracao:.1f}s")
    gerar_relatorio(resultado)

    print("=" * 60)
    print("✅ Agente concluído com sucesso!")
    print("📂 Verifique: output/relatorio_vagas.md e output/cover_letters/")
    print("=" * 60)

    return resultado


if __name__ == "__main__":
    try:
        executar_agente()
    except KeyboardInterrupt:
        print("\n\n⚠️  Execução interrompida pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)