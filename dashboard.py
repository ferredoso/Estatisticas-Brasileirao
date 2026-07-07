import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Brasileirão Dashboard", layout="wide")

# ===== Estilo customizado (tema escuro) =====
st.markdown("""
    <style>
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        h1 {
            font-weight: 700 !important;
            letter-spacing: -1px;
            color: #00c896 !important;
        }
        h2, h3 {
            font-weight: 600 !important;
            color: #e8eaf0 !important;
        }
        div[data-testid="stMetric"] {
            background: #1a1d27;
            border: 1px solid #2a2d3e;
            border-radius: 14px;
            padding: 16px 20px;
        }
        div[data-testid="stMetricLabel"] {
            color: #7b8099 !important;
        }
        div[data-testid="stMetricValue"] {
            color: #00c896 !important;
            font-weight: 700 !important;
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid #2a2d3e;
            border-radius: 12px;
            overflow: hidden;
        }
        div[data-baseweb="select"] {
            border-radius: 8px;
        }
        section[data-testid="stSidebar"] {
            background: #1a1d27;
            border-right: 1px solid #2a2d3e;
        }
        hr {
            border-color: #2a2d3e !important;
        }
    </style>
""", unsafe_allow_html=True)


def estilizar_grafico(fig):
    fig.update_layout(
        plot_bgcolor='#1a1d27',
        paper_bgcolor='#1a1d27',
        font_color='#e8eaf0',
        title_font_color='#e8eaf0',
        legend_font_color='#e8eaf0',
        xaxis=dict(gridcolor='#2a2d3e', color='#7b8099'),
        yaxis=dict(gridcolor='#2a2d3e', color='#7b8099'),
    )
    return fig


NOMES_COLUNAS = {
    'time': 'Time',
    'jogos': 'Jogos',
    'vitorias': 'Vitórias',
    'empates': 'Empates',
    'derrotas': 'Derrotas',
    'gols_pro': 'Gols Pró',
    'gols_contra': 'Gols Contra',
    'saldo_gols': 'Saldo de Gols',
    'pontos': 'Pontos',
    'posicao': 'Posição',
    'ano': 'Ano'
}


def formatar_tabela(df):
    return df.rename(columns=NOMES_COLUNAS)


@st.cache_data
def carregar_dados():
    df = pd.read_csv('campeonato-brasileiro-full.csv')
    df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
    df['ano'] = df['data'].dt.year

    def classificar_resultado(linha):
        if linha['mandante_Placar'] > linha['visitante_Placar']:
            return 'vitoria_mandante'
        elif linha['mandante_Placar'] < linha['visitante_Placar']:
            return 'vitoria_visitante'
        else:
            return 'empate'

    df['resultado'] = df.apply(classificar_resultado, axis=1)
    return df


def calcular_pontos_tabela(df):
    times = pd.concat([df['mandante'], df['visitante']]).unique()
    tabela = []

    for time in times:
        jogos_casa = df[df['mandante'] == time]
        jogos_fora = df[df['visitante'] == time]

        vitorias = len(jogos_casa[jogos_casa['resultado'] == 'vitoria_mandante']) + \
                   len(jogos_fora[jogos_fora['resultado'] == 'vitoria_visitante'])
        empates = len(jogos_casa[jogos_casa['resultado'] == 'empate']) + \
                  len(jogos_fora[jogos_fora['resultado'] == 'empate'])
        derrotas = len(jogos_casa[jogos_casa['resultado'] == 'vitoria_visitante']) + \
                   len(jogos_fora[jogos_fora['resultado'] == 'vitoria_mandante'])

        gols_pro = jogos_casa['mandante_Placar'].sum() + jogos_fora['visitante_Placar'].sum()
        gols_contra = jogos_casa['visitante_Placar'].sum() + jogos_fora['mandante_Placar'].sum()

        jogos = vitorias + empates + derrotas
        pontos = vitorias * 3 + empates

        tabela.append({
            'time': time, 'jogos': jogos, 'vitorias': vitorias,
            'empates': empates, 'derrotas': derrotas,
            'gols_pro': gols_pro, 'gols_contra': gols_contra,
            'saldo_gols': gols_pro - gols_contra, 'pontos': pontos
        })

    return pd.DataFrame(tabela).sort_values(
        ['pontos', 'saldo_gols'], ascending=False
    ).reset_index(drop=True)


# ===== Carregar dados =====
df = carregar_dados()
times_disponiveis = sorted(pd.concat([df['mandante'], df['visitante']]).unique())

# ===== Cabeçalho =====
st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
        <span style="font-size: 2.2rem;">⚽</span>
        <div>
            <h1 style="margin: 0; padding: 0;">Brasileirão Dashboard</h1>
            <p style="color: #7b8099; margin: 0; font-size: 14px;">
                Análise histórica do Campeonato Brasileiro (2003–2022)
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)

# ===== Filtro de temporada =====
anos_disponiveis = sorted(df['ano'].unique(), reverse=True)
ano_selecionado = st.sidebar.selectbox("Selecione a temporada", anos_disponiveis)

df_ano = df[df['ano'] == ano_selecionado]
tabela = calcular_pontos_tabela(df_ano)
tabela.index = tabela.index + 1

# ===== Tabela de classificação =====
st.subheader(f"Classificação — {ano_selecionado}")
st.dataframe(formatar_tabela(tabela), use_container_width=True)

# ===== Gráfico de pontos =====
st.subheader("Pontos por time")
fig = px.bar(
    tabela.head(10), x='time', y='pontos', color='pontos',
    color_continuous_scale='Greens',
    labels={'time': 'Time', 'pontos': 'Pontos'}
)
st.plotly_chart(estilizar_grafico(fig), use_container_width=True)

# ===== Análise de mandante x visitante =====
st.subheader(f"🏠 Efeito de jogar em casa — {ano_selecionado}")

col1, col2 = st.columns([1, 2])

with col1:
    contagem_resultados = df_ano['resultado'].value_counts().reset_index()
    contagem_resultados.columns = ['resultado', 'quantidade']
    contagem_resultados['resultado'] = contagem_resultados['resultado'].map({
        'vitoria_mandante': 'Vitória do mandante',
        'empate': 'Empate',
        'vitoria_visitante': 'Vitória do visitante'
    })

    fig_pizza = px.pie(
        contagem_resultados,
        names='resultado',
        values='quantidade',
        color='resultado',
        color_discrete_map={
            'Vitória do mandante': '#00c896',
            'Empate': '#f7b84f',
            'Vitória do visitante': '#ff5c5c'
        },
        title="Resultado geral dos jogos"
    )
    st.plotly_chart(estilizar_grafico(fig_pizza), use_container_width=True)

with col2:
    def calcular_taxa_mandante_visitante(df):
        times = pd.concat([df['mandante'], df['visitante']]).unique()
        dados = []

        for time in times:
            jogos_casa = df[df['mandante'] == time]
            jogos_fora = df[df['visitante'] == time]

            if len(jogos_casa) == 0 or len(jogos_fora) == 0:
                continue

            vitorias_casa = len(jogos_casa[jogos_casa['resultado'] == 'vitoria_mandante'])
            vitorias_fora = len(jogos_fora[jogos_fora['resultado'] == 'vitoria_visitante'])

            taxa_casa = (vitorias_casa / len(jogos_casa)) * 100
            taxa_fora = (vitorias_fora / len(jogos_fora)) * 100

            dados.append({'time': time, 'local': 'Em casa', 'taxa_vitoria': taxa_casa})
            dados.append({'time': time, 'local': 'Fora de casa', 'taxa_vitoria': taxa_fora})

        return pd.DataFrame(dados)

    df_taxas = calcular_taxa_mandante_visitante(df_ano)

    ordem_times = df_taxas[df_taxas['local'] == 'Em casa'].sort_values(
        'taxa_vitoria', ascending=False
    )['time'].tolist()

    fig_barras = px.bar(
        df_taxas,
        x='time',
        y='taxa_vitoria',
        color='local',
        barmode='group',
        category_orders={'time': ordem_times},
        color_discrete_map={'Em casa': '#4f8ef7', 'Fora de casa': '#ff9f43'},
        title="Taxa de vitória: em casa x fora",
        labels={'taxa_vitoria': '% de vitórias', 'time': 'Time'}
    )
    st.plotly_chart(estilizar_grafico(fig_barras), use_container_width=True)

# ===== Evolução de um time ao longo dos anos =====
st.subheader("📈 Evolução de um time ao longo das temporadas")

time_selecionado = st.selectbox("Selecione um time", times_disponiveis, key="time_evolucao")


@st.cache_data
def calcular_evolucao_time(df, time):
    jogos_do_time = df[(df['mandante'] == time) | (df['visitante'] == time)]
    primeiro_ano = jogos_do_time['ano'].min()
    ultimo_ano = jogos_do_time['ano'].max()
    anos_com_dados = set(df['ano'].unique())

    evolucao = []

    for ano in range(int(primeiro_ano), int(ultimo_ano) + 1):
        if ano not in anos_com_dados:
            continue

        df_ano_loop = df[df['ano'] == ano]
        jogou_serie_a = time in df_ano_loop['mandante'].values or time in df_ano_loop['visitante'].values

        if jogou_serie_a:
            tabela_ano = calcular_pontos_tabela(df_ano_loop)
            tabela_ano['posicao'] = tabela_ano.index + 1
            linha_time = tabela_ano[tabela_ano['time'] == time].iloc[0]

            evolucao.append({
                'ano': ano,
                'divisao': 'Série A',
                'pontos': linha_time['pontos'],
                'vitorias': linha_time['vitorias'],
                'empates': linha_time['empates'],
                'derrotas': linha_time['derrotas'],
                'saldo_gols': linha_time['saldo_gols'],
                'posicao': linha_time['posicao']
            })
        else:
            evolucao.append({
                'ano': ano,
                'divisao': 'Série B (rebaixado)',
                'pontos': None,
                'vitorias': None,
                'empates': None,
                'derrotas': None,
                'saldo_gols': None,
                'posicao': None
            })

    return pd.DataFrame(evolucao)


df_evolucao = calcular_evolucao_time(df, time_selecionado)

col1, col2 = st.columns(2)

with col1:
    fig_pontos = px.line(
        df_evolucao,
        x='ano',
        y='pontos',
        markers=True,
        title=f"Pontos por temporada — {time_selecionado}",
        color_discrete_sequence=['#00c896'],
        labels={'ano': 'Ano', 'pontos': 'Pontos'}
    )
    fig_pontos.update_layout(xaxis=dict(dtick=1))
    st.plotly_chart(estilizar_grafico(fig_pontos), use_container_width=True)

with col2:
    fig_posicao = px.line(
        df_evolucao,
        x='ano',
        y='posicao',
        markers=True,
        title=f"Posição na tabela por temporada — {time_selecionado}",
        color_discrete_sequence=['#4f8ef7'],
        labels={'ano': 'Ano', 'posicao': 'Posição'}
    )
    fig_posicao.update_layout(
        yaxis=dict(autorange='reversed'),
        xaxis=dict(dtick=1)
    )
    st.plotly_chart(estilizar_grafico(fig_posicao), use_container_width=True)

st.caption("⚠️ Este dataset contém apenas jogos da Série A. Anos marcados como 'Série B (rebaixado)' indicam que o time não disputou a primeira divisão naquela temporada.")

tabela_evolucao = formatar_tabela(df_evolucao)
tabela_evolucao = tabela_evolucao.rename(columns={'divisao': 'Divisão'})
st.dataframe(tabela_evolucao, use_container_width=True, hide_index=True)

# ===== Comparação entre dois times =====
st.subheader("🆚 Comparação entre dois times")

col_a, col_b = st.columns(2)
with col_a:
    time_a = st.selectbox("Time A", times_disponiveis, index=0, key="time_a")
with col_b:
    time_b = st.selectbox("Time B", times_disponiveis, index=1, key="time_b")

if time_a == time_b:
    st.warning("Selecione dois times diferentes para comparar.")
else:
    confrontos = df[
        ((df['mandante'] == time_a) & (df['visitante'] == time_b)) |
        ((df['mandante'] == time_b) & (df['visitante'] == time_a))
    ].sort_values('data')

    vitorias_a = len(confrontos[
        ((confrontos['mandante'] == time_a) & (confrontos['resultado'] == 'vitoria_mandante')) |
        ((confrontos['visitante'] == time_a) & (confrontos['resultado'] == 'vitoria_visitante'))
    ])
    vitorias_b = len(confrontos[
        ((confrontos['mandante'] == time_b) & (confrontos['resultado'] == 'vitoria_mandante')) |
        ((confrontos['visitante'] == time_b) & (confrontos['resultado'] == 'vitoria_visitante'))
    ])
    empates_confronto = len(confrontos[confrontos['resultado'] == 'empate'])

    c1, c2, c3 = st.columns(3)
    c1.metric(f"Vitórias {time_a}", vitorias_a)
    c2.metric("Empates", empates_confronto)
    c3.metric(f"Vitórias {time_b}", vitorias_b)

    tabela_geral = calcular_pontos_tabela(df)
    stats_a = tabela_geral[tabela_geral['time'] == time_a].iloc[0]
    stats_b = tabela_geral[tabela_geral['time'] == time_b].iloc[0]

    categorias = ['Vitórias', 'Empates', 'Derrotas', 'Gols pró', 'Gols contra', 'Pontos']
    valores_a = [stats_a['vitorias'], stats_a['empates'], stats_a['derrotas'],
                 stats_a['gols_pro'], stats_a['gols_contra'], stats_a['pontos']]
    valores_b = [stats_b['vitorias'], stats_b['empates'], stats_b['derrotas'],
                 stats_b['gols_pro'], stats_b['gols_contra'], stats_b['pontos']]

    df_radar = pd.DataFrame({
        'categoria': categorias * 2,
        'valor': valores_a + valores_b,
        'time': [time_a] * 6 + [time_b] * 6
    })

    fig_radar = px.line_polar(
        df_radar, r='valor', theta='categoria', color='time',
        line_close=True,
        color_discrete_map={time_a: '#00c896', time_b: '#4f8ef7'},
        title="Comparação geral (todas as temporadas do dataset)"
    )
    fig_radar.update_traces(fill='toself')
    st.plotly_chart(estilizar_grafico(fig_radar), use_container_width=True)

    st.write(f"**Últimos confrontos diretos ({len(confrontos)} jogos no total):**")
    tabela_confrontos = confrontos[['data', 'mandante', 'mandante_Placar', 'visitante_Placar', 'visitante']].tail(10)
    tabela_confrontos.columns = ['Data', 'Mandante', 'Placar Casa', 'Placar Fora', 'Visitante']
    tabela_confrontos['Data'] = tabela_confrontos['Data'].dt.strftime('%d/%m/%Y')
    st.dataframe(tabela_confrontos, use_container_width=True, hide_index=True)