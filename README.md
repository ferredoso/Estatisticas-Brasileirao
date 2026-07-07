# ⚽ Brasileirão Dashboard

Dashboard interativo de análise de dados do Campeonato Brasileiro (2003-2022), desenvolvido em Python com Streamlit. Permite explorar classificações históricas, comparar times, analisar o efeito de jogar em casa e visualizar a evolução de qualquer clube ao longo das temporadas.

## 🚀 Funcionalidades

- Classificação completa por temporada, calculada a partir dos dados brutos de cada partida
- Análise do efeito de jogar em casa (taxa de vitória mandante x visitante)
- Evolução histórica de qualquer time (pontos e posição na tabela ano a ano)
- Identificação de temporadas em que o time disputou a Série B
- Comparação direta entre dois times, com retrospecto de confrontos e gráfico radar

## 🛠️ Tecnologias utilizadas

- **Python 3**
- **Pandas** — manipulação e análise dos dados
- **Streamlit** — interface web interativa
- **Plotly** — gráficos interativos

## 📊 Fonte dos dados

Dataset [Campeonato Brasileiro de Futebol](https://www.kaggle.com/datasets/adaoduque/campeonato-brasileiro-de-futebol), disponível publicamente no Kaggle, contendo todas as partidas da Série A de 2003 a 2022.

> **Observação:** o dataset contém apenas jogos da Série A. Anos em que um time não aparece correspondem a temporadas na Série B.

## ⚙️ Como rodar o projeto localmente

**1. Clone o repositório**
```bash
git clone https://github.com/ferredoso/brasileirao-dashboard.git
cd brasileirao-dashboard
```

**2. Crie e ative o ambiente virtual**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

**3. Instale as dependências**
```bash
pip install -r requirements.txt
```

**4. Inicie o dashboard**
```bash
streamlit run dashboard.py
```

**5. Acesse no navegador**

O Streamlit abre automaticamente em:

http://localhost:8501

## 👨‍💻 Autor

Feito por **Gabriel Cardoso Ferreira** — [LinkedIn](https://www.linkedin.com/in/gabriel-cardoso-ferreira/) · [GitHub](https://github.com/ferredoso)
