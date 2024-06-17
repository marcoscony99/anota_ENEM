from flask import Flask, render_template, request
import pandas as pd
import os
import matplotlib
matplotlib.use('Agg')  # Defina o backend antes de importar pyplot
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)

# Caminhos para os arquivos CSV de 2022, 2023 e 2021
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
    'C': 'R$ 1.320,01 a R$ 1.980,00',
    'D': 'R$ 1.980,01 a R$ 2.640,00',
    'E': 'R$ 2.640,01 a R$ 3.300,00',
    'F': 'R$ 3.300,01 a R$ 3.960,00',
    'G': 'R$ 3.960,01 a R$ 5.280,00',
    'H': 'R$ 5.280,01 a R$ 6.600,00',
    'I': 'R$ 6.600,01 a R$ 7.920,00',
    'J': 'R$ 7.920,01 a R$ 9.240,00',
    'K': 'R$ 9.240,01 a R$ 10.560,00',
    'L': 'R$ 10.560,01 a R$ 11.880,00',
    'M': 'R$ 11.880,01 a R$ 13.200,00',
    'N': 'R$ 13.200,01 a R$ 15.840,00',
    'O': 'R$ 15.840,01 a R$ 19.800,00',
    'P': 'R$ 19.800,01 a R$ 26.400,00',
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
    anos = request.form.getlist('ano')
    disciplina = request.form.get('disciplina')
    metrica = request.form.get('metrica')
    criterio = request.form.get('criterio')

    if not disciplina or not metrica or not criterio or not anos:
        return "Dados do formulário incompletos.", 400

    resultados = {}
    grafico = None

    for ano in sorted(anos):  # Ordena os anos em ordem crescente
        if ano not in data:
            return f"Ano inválido: {ano}", 400

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

        resultados[ano] = {'disciplina': disciplina_nome, 'criterio': criterio, 'data': formatted_data}

        # Gerar gráfico
        if grafico is None:
            img = BytesIO()
            plt.figure(figsize=(10, 6))

           
        if len(anos) == 1:
            plt.bar(formatted_data.keys(), formatted_data.values())
            plt.xlabel('Categoria')
            plt.ylabel('Média')
            plt.title(f'{disciplina_nome} - {criterio} ({ano})')
            plt.xticks(rotation=45, ha="right")
        else:
            for categoria in formatted_data.keys():
                plt.plot(list(resultados.keys()), [resultados[a]['data'].get(categoria, None) for a in resultados], label=categoria)
            plt.xlabel('Ano')
            plt.ylabel('Média')
            plt.title(f'{disciplina_nome} - desempenho por {criterio}')
            plt.legend()

        plt.tight_layout()
        plt.savefig(img, format='png')
        plt.close()
        img.seek(0)
        grafico = base64.b64encode(img.getvalue()).decode()

    return render_template('result.html', resultados=resultados, grafico=grafico)

def filter_data(disciplina, metrica, criterio, ano):
    if disciplina == 'matemática':
        coluna_disciplina = 'NU_NOTA_MT'
    elif disciplina == 'redação':
        coluna_disciplina = 'NU_NOTA_REDACAO'
    elif disciplina == 'natureza':
        coluna_disciplina = 'NU_NOTA_CN'
    elif disciplina == 'humanas':
        coluna_disciplina = 'NU_NOTA_CH'
    elif disciplina == 'linguagens':
        coluna_disciplina = 'NU_NOTA_LC'
    else:
        raise ValueError("Disciplina inválida")

    if metrica == 'média':
        metrica_func = 'mean'
    elif metrica == 'mediana':
        metrica_func = 'median'
    else:
        raise ValueError("Métrica inválida")

    if criterio == 'tipo de escola':
        coluna_criterio = 'TP_ESCOLA'
    elif criterio == 'renda familiar':
        coluna_criterio = 'Q006'
    elif criterio == 'acesso à internet':
        coluna_criterio = 'Q025'
    elif criterio == 'escolaridade da mãe':
        coluna_criterio = 'Q002'
    elif criterio == 'estado':
        coluna_criterio = 'SG_UF_PROVA'
    elif criterio == 'cor_raca':
        coluna_criterio = 'TP_COR_RACA'
    else:
        raise ValueError("Critério inválido")

    df = data[ano]
    filtered_data = df.groupby(coluna_criterio)[coluna_disciplina].agg(metrica_func)
    return filtered_data.to_dict()

if __name__ == '__main__':
    plt.switch_backend('Agg')
    app.run(debug=True)
