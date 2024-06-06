from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

# Caminhos para os arquivos CSV de 2022 e 2023
csv_paths = {
    '2023': "C:\\Users\\marco\\OneDrive\\MICRODADOS_ENEM_2023.csv",
    '2022': "C:\\Users\\marco\\OneDrive\\MICRODADOS_ENEM_2022.csv",
    '2021': "C:\\Users\\marco\\OneDrive\\MICRODADOS_ENEM_2021.csv"
}

data = {}

# Verifica se os arquivos existem e carrega os dados
for year, path in csv_paths.items():
    if os.path.exists(path):
        try:
            data[year] = pd.read_csv(path, sep=';', encoding='ISO-8859-1', usecols=['NU_NOTA_MT', 'NU_NOTA_REDACAO', 'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'TP_ESCOLA', 'Q006', 'Q025', 'Q002', 'SG_UF_PROVA', 'TP_COR_RACA'])
            print(f"Arquivo {path} ({year}) carregado com sucesso.")
        except Exception as e:
            print(f"Erro ao carregar o arquivo {path} ({year}): {e}")
            data[year] = pd.DataFrame()  # DataFrame vazio para evitar erros
    else:
        print(f"Arquivo {path} ({year}) não encontrado.")
        data[year] = pd.DataFrame()  # DataFrame vazio para evitar erros

# Dicionário para mapear as disciplinas para descrições
disciplinas_dict = {
    'matemática': 'Matemática',
    'redação': 'Redação',
    'natureza': 'Ciências da Natureza',
    'humanas': 'Ciências Humanas',
    'linguagens': 'Linguagens e Códigos'
}

# Dicionários de mapeamento existentes
tipo_escola_dict = {
    1.0: 'Não informado',
    2.0: 'Pública',
    3.0: 'Privada'
}

faixa_renda_dict = {
    'A': 'Nenhuma Renda',
    'B': 'Até R$ 1.320,00',
    'C': 'De R$ 1.320,01 até R$ 1.980,00',
    'D': 'De R$ 1.980,01 até R$ 2.640,00',
    'E': 'De R$ 2.640,01 até R$ 3.300,00',
    'F': 'De R$ 3.300,01 até R$ 3.960,00',
    'G': 'De R$ 3.960,01 até R$ 5.280,00',
    'H': 'De R$ 5.280,01 até R$ 6.600,00',
    'I': 'De R$ 6.600,01 até R$ 7.920,00',
    'J': 'De R$ 7.920,01 até R$ 9.240,00',
    'K': 'De R$ 9.240,01 até R$ 10.560,00',
    'L': 'De R$ 10.560,01 até R$ 11.880,00',
    'M': 'De R$ 11.880,01 até R$ 13.200,00',
    'N': 'De R$ 13.200,01 até R$ 15.840,00',
    'O': 'De R$ 15.840,01 até R$ 19.800,00',
    'P': 'De R$ 19.800,01 até R$ 26.400,00',
    'Q': 'Acima de R$ 26.400,00'
}

acesso_internet_dict = {
    'A': 'Sem Internet',
    'B': 'Com Internet'
}

escolaridade_mae_dict = {
    'A': 'Nunca estudou',
    'B': 'Não completou a 4ª série/5º ano do Ensino Fundamental',
    'C': 'Completou a 4ª série/5º ano, mas não completou a 8ª série/9º ano do Ensino Fundamental',
    'D': 'Completou a 8ª série/9º ano do Ensino Fundamental, mas não completou o Ensino Médio',
    'E': 'Completou o Ensino Médio, mas não completou a Faculdade',
    'F': 'Completou a Faculdade, mas não completou a Pós-graduação',
    'G': 'Completou a Pós-graduação',
    'H': 'Não sei'
}

estado_dict = {
    'AC': 'Acre',
    'AL': 'Alagoas',
    'AP': 'Amapá',
    'AM': 'Amazonas',
    'BA': 'Bahia',
    'CE': 'Ceará',
    'DF': 'Distrito Federal',
    'ES': 'Espírito Santo',
    'GO': 'Goiás',
    'MA': 'Maranhão',
    'MT': 'Mato Grosso',
    'MS': 'Mato Grosso do Sul',
    'MG': 'Minas Gerais',
    'PA': 'Pará',
    'PB': 'Paraíba',
    'PR': 'Paraná',
    'PE': 'Pernambuco',
    'PI': 'Piauí',
    'RJ': 'Rio de Janeiro',
    'RN': 'Rio Grande do Norte',
    'RS': 'Rio Grande do Sul',
    'RO': 'Rondônia',
    'RR': 'Roraima',
    'SC': 'Santa Catarina',
    'SP': 'São Paulo',
    'SE': 'Sergipe',
    'TO': 'Tocantins'
}

# Dicionário para mapear as cores/raças para descrições
cor_raca_dict = {
    0: 'Não Declarado',
    1: 'Branca',
    2: 'Preta',
    3: 'Parda',
    4: 'Amarela',
    5: 'Indígena',
    6: 'Não Dispõe da Informação'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():
    disciplina = request.form.get('disciplina')
    metrica = request.form.get('metrica')
    criterio = request.form.get('criterio')
    ano = request.form.get('ano')

    if not disciplina or not metrica or not criterio or not ano:
        return "Dados do formulário incompletos.", 400

    if ano not in data:
        return "Ano inválido.", 400

    filtered_data = filter_data(disciplina, metrica, criterio, ano)
    disciplina_nome = disciplinas_dict.get(disciplina, 'Desconhecido')

    if criterio == 'tipo de escola':
        formatted_data = {tipo_escola_dict.get(float(key), 'Desconhecido'): round(value, 1) for key, value in filtered_data.items()}
    elif criterio == 'renda familiar':
        formatted_data = {faixa_renda_dict.get(key, 'Desconhecido'): round(value, 1) for key, value in filtered_data.items()}
    elif criterio == 'acesso à internet':
        formatted_data = {acesso_internet_dict.get(key, 'Desconhecido'): round(value, 1) for key, value in filtered_data.items()}
    elif criterio == 'escolaridade da mãe':
        formatted_data = {escolaridade_mae_dict.get(key, 'Desconhecido'): round(value, 1) for key, value in filtered_data.items()}
    elif criterio == 'estado':
        formatted_data = {estado_dict.get(key, 'Desconhecido'): round(value, 1) for key, value in filtered_data.items()}
    elif criterio == 'cor_raca':
        formatted_data = {cor_raca_dict.get(key, 'Desconhecido'): round(value, 1) for key, value in filtered_data.items()}

    else:
        formatted_data = {key: round(value, 1) for key, value in filtered_data.items()}

    return render_template('result.html', result_data=formatted_data, criterio=criterio, disciplina=disciplina_nome, ano=ano)

def filter_data(disciplina, metrica, criterio, ano):
    colunas_disciplinas = {
        'matemática': 'NU_NOTA_MT',
        'redação': 'NU_NOTA_REDACAO',
        'natureza': 'NU_NOTA_CN',
        'humanas': 'NU_NOTA_CH',
        'linguagens': 'NU_NOTA_LC'
    }

    col = colunas_disciplinas.get(disciplina)
    df = data.get(ano)

    if not col or df is None or df.empty:
        return {}

    if criterio == 'tipo de escola':
        data_cleaned = df.dropna(subset=[col, 'TP_ESCOLA'])
        result = data_cleaned.groupby('TP_ESCOLA')[col].mean().reset_index()
        result_data = {str(row['TP_ESCOLA']): row[col] for index, row in result.iterrows()}
    elif criterio == 'renda familiar':
        data_cleaned = df.dropna(subset=[col, 'Q006'])
        result = data_cleaned.groupby('Q006')[col].mean().reset_index()
        result_data = {row['Q006']: row[col] for index, row in result.iterrows()}
    elif criterio == 'acesso à internet':
        data_cleaned = df.dropna(subset=[col, 'Q025'])
        result = data_cleaned.groupby('Q025')[col].mean().reset_index()
        result_data = {row['Q025']: row[col] for index, row in result.iterrows()}
    elif criterio == 'escolaridade da mãe':
        data_cleaned = df.dropna(subset=[col, 'Q002'])
        result = data_cleaned.groupby('Q002')[col].mean().reset_index()
        result_data = {row['Q002']: row[col] for index, row in result.iterrows()}
    elif criterio == 'estado':
        data_cleaned = df.dropna(subset=[col, 'SG_UF_PROVA'])
        result = data_cleaned.groupby('SG_UF_PROVA')[col].mean().reset_index()
        result_data = {row['SG_UF_PROVA']: row[col] for index, row in result.iterrows()}
    elif criterio == 'cor_raca':
        data_cleaned = df.dropna(subset=[col, 'TP_COR_RACA'])
        result = data_cleaned.groupby('TP_COR_RACA')[col].mean().reset_index()
        result_data = {row['TP_COR_RACA']: row[col] for index, row in result.iterrows()}
    else:
        return {}

    return result_data

if __name__ == '__main__':
    app.run(debug=True)