#Importa as bibliotecas utilizadas no codigo para fazer análise dos dados
import numpy as np
import matplotlib.pyplot as mp

#Abre o arquivo .txt com os dados coletados
with open('dados.txt', 'r') as arquivo:
    # Lê todas as linhas do arquivo
    linhas = arquivo.readlines()

#Divide a primeira linha em nomes de ativos
ativos = linhas[0].strip().split(';')

#Dicionário para mapear cada ativo às suas rentabilidades
ativos_dict = {}
for ativo in ativos:
    ativos_dict[ativo] = []

# Loop pelas linhas de rentabilidade dos ativos
for linha in linhas[1:]:
    rentabilidades = linha.strip().split(';')

    # Loop pelas rentabilidades e as atribui aos ativos correspondentes
    for ativo, rentabilidade in zip(ativos, rentabilidades):
        if rentabilidade:
            ativos_dict[ativo].append(float(rentabilidade))
        else:
            # Se a rentabilidade estiver em branco, tratar como 0
            ativos_dict[ativo].append(0)

# Calcula o Coeficiente de Variação de Pearson para cada ativo
coef_variacao = {}
for ativo, retornos in ativos_dict.items():
    media = np.mean(retornos)
    desvio_padrao = np.std(retornos)
    coef_variacao[ativo] = (desvio_padrao / media) * 100

# Dividindo os ativos em títulos públicos e títulos privados (formatação do txt deve conter esse formato)
ativos_publicos = ativos[:5]
ativos_privados = ativos[5:]

# Selecionando os 2 ativos com os menores coeficientes de variação entre títulos públicos e privados
ativos_selecionados_publicos = []
ativos_selecionados_privados = []

for ativo in coef_variacao:
    if ativo in ativos_publicos:
        ativos_selecionados_publicos.append((ativo, coef_variacao[ativo]))
    elif ativo in ativos_privados:
        ativos_selecionados_privados.append((ativo, coef_variacao[ativo]))

#Formata os ativos selecionados em: ("titulo","menor coeficente de variação")
ativos_selecionados_publicos = sorted(ativos_selecionados_publicos, key=lambda x: x[1])[:2]
ativos_selecionados_privados = sorted(ativos_selecionados_privados, key=lambda x: x[1])[:2]

#Lista para indices dos privados
indice_sharpe_privado = []

#Lista para indices dos publicos
indice_sharpe_publico = []

#Função para calcular variância, média e matriz 
def obtemvalor(origem, tipocalculo,  linha, coluna):
    match tipocalculo:
        case "var":
            return np.var(ativos_dict[origem[linha][coluna]])
        case "array":
            return np.array(ativos_dict[origem[linha][coluna]])
        case "mean":
            return np.mean(ativos_dict[origem[linha][coluna]])

#Obtem variaveis dos ativos privados
media1_privado = obtemvalor(ativos_selecionados_privados, "mean", 0, 0) 
media2_privado = obtemvalor(ativos_selecionados_privados, "mean", 1, 0) 
matriz1_priv = obtemvalor(ativos_selecionados_privados, "array", 0, 0) 
matriz2_priv = obtemvalor(ativos_selecionados_privados, "array", 1, 0) 
var1_privado = obtemvalor(ativos_selecionados_privados, "var", 0, 0) 
var2_privado = obtemvalor(ativos_selecionados_privados, "var", 1, 0) 

#Obtem variaveis dos ativos publicos
media1_publico = obtemvalor(ativos_selecionados_publicos, "mean", 0, 0) 
media2_publico = obtemvalor(ativos_selecionados_publicos, "mean", 1, 0)
matriz1_pub = obtemvalor(ativos_selecionados_publicos, "array", 0, 0) 
matriz2_pub = obtemvalor(ativos_selecionados_publicos, "array", 1, 0) 
var1_publico = obtemvalor(ativos_selecionados_publicos, "var", 0, 0)
var2_publico = obtemvalor(ativos_selecionados_publicos, "var", 1, 0) 

#Calcular a covariancia dos privados
cov_priv = np.cov(matriz1_priv,matriz2_priv)[0][1]

#Calcular a covariancia dos publicos
cov_pub = np.cov(matriz1_pub,matriz2_pub)[0][1]

#Calcular o rf (utilizado no calculo tanto dos privados quanto dos publicos) com base na selic do ano (13.75)
rf = (((13.75/100)+1)**(1/365))

def preenchesharpe(variavelapreencher, m1, m2, var1, var2, covpriv, rf):
    for i in np.arange(0, 1.02, 0.02):
        med_portifolio = (i*m1 + (1-i)*m2)
        var_portifolio = ((i**2)*var1)
        var_portifolio = var_portifolio + (((1-i)**2)*var2)
        var_portifolio = var_portifolio + 2*((i+0.02)*((1-i)-0.02)*covpriv)
        dp_portifolio = var_portifolio**0.5
        variavelapreencher.append((med_portifolio-rf)/dp_portifolio)

#Calcular o menor índice de sharpe dos privados
preenchesharpe(indice_sharpe_privado, media1_privado, media2_privado, var1_privado, var2_privado, cov_priv, rf)

#Selecionar melhor indice sharpe
menor_sharpe_privado = max(indice_sharpe_privado)

#Relaciona o menor índice as devidas porcentagens
for i in np.arange(0,1.02,0.02):
    med_portifolio = (i*media1_privado + (1-i)*media2_privado)
    var_portifolio = ((i**2)*var1_privado)+(((1-i)**2)*var2_privado)+2*((i+0.02)*((1-i)-0.02)*cov_priv)
    dp_portifolio = var_portifolio**0.5
    indice_sharpe_portifolio = (med_portifolio-rf)/dp_portifolio    
    if indice_sharpe_portifolio == menor_sharpe_privado:
        porcentagem_carteira_privada = (str(i*100)+"% no "+(ativos_selecionados_privados[0][0])+" e "+str((i-1)*100)+"% no "+(ativos_selecionados_privados[1][0]))
        porcentagem_ativo1_privado = (i)
        porcentagem_ativo2_privado = (1-i)

#Calcular o menor índice de sharpe dos privados
preenchesharpe(indice_sharpe_publico, media1_publico, media2_publico, var1_publico, var2_publico, cov_pub, rf)

#Selecionar menor indice sharpe
menor_sharpe_publico = max(indice_sharpe_publico)

#Relaciona o menor índice as devidas porcentagens
for i in np.arange(0, 1.02, 0.02):
    med_portifolio = (i*media1_publico + (1-i)*media2_publico)
    var_portifolio = ((i**2)*var1_publico)+(((1-i)**2)*var2_publico)+2*((i+0.02)*((1-i)-0.02)*cov_pub)
    dp_portifolio = var_portifolio**0.5
    indice_sharpe_portifolio = (med_portifolio-rf)/dp_portifolio     
    if indice_sharpe_portifolio == menor_sharpe_publico:
        porcentagem_carteira_publica = (str(i*100)+"%  no "+(ativos_selecionados_publicos[0][0])+" e "+str((i-1)*100)+"% no "+(ativos_selecionados_publicos[1][0]))
        porcentagem_ativo1_publico = (i)
        porcentagem_ativo2_publico = (1-i)

#Retorno carteira privada com base nas porcentagens 
retorno_carteira_privada = (((sum(ativos_dict[ativos_selecionados_privados[0][0]])-251))*porcentagem_ativo1_privado*100)+((sum(ativos_dict[ativos_selecionados_privados[1][0]])-251)*porcentagem_ativo2_privado)

#Retorno carteira privada com base nas porcentagens
retorno_carteira_publica = ((sum(ativos_dict[ativos_selecionados_publicos[0][0]])-251)*porcentagem_ativo1_publico*100)+((sum(ativos_dict[ativos_selecionados_publicos[1][0]])-251)*porcentagem_ativo2_publico)

#Cria a lista da rentabilidade geral da carteira diária
rentabilidade_dia_geral = []

#Calcula a rentabilidade geral de cada dia
for i in range(251):
    rentabilidade_dia_privado_1 = (ativos_dict[ativos_selecionados_privados[0][0]][i]- 1) * porcentagem_ativo1_privado
    rentabilidade_dia_privado_2 = (ativos_dict[ativos_selecionados_privados[1][0]][i]- 1) * porcentagem_ativo2_privado
    rentabilidade_dia_publico_1 = (ativos_dict[ativos_selecionados_publicos[0][0]][i]- 1) * porcentagem_ativo1_publico
    rentabilidade_dia_publico_2 = (ativos_dict[ativos_selecionados_publicos[1][0]][i]- 1) * porcentagem_ativo2_publico
    rentabilidade_dia_publico = (rentabilidade_dia_publico_1+rentabilidade_dia_publico_2)/2
    rentabilidade_dia_privado = (rentabilidade_dia_privado_1+rentabilidade_dia_privado_2)/2
    soma_rent = rentabilidade_dia_publico + rentabilidade_dia_privado + 1
    rentabilidade_dia_geral.append(soma_rent)

#Calcula a rentabilidade geral
rentabilidade_geral = sum(rentabilidade_dia_geral)-251

#Cria os dias úteis para ser o eixo x do gráfico
dias_uteis = []

for i in range(251):
    dias_uteis.append(i)

#Lê os dados de títulos para comparação nos gráficos
with open('selic.txt', 'r') as arquivo:
    # Lê todas as linhas do arquivo
    linhas_comparacao = arquivo.readlines()

#Divide a primeira linha em nomes de ativos
ativos_comparacao = linhas_comparacao[0].strip().split(';')

#Inicializa um dicionário para mapear cada ativo às suas rentabilidades
ativos_comp_dict = {}
for ativo_comp in ativos_comparacao:
    ativos_comp_dict[ativo_comp] = []

#Loop pelas linhas de rentabilidade dos ativos
for linha_comp in linhas_comparacao[1:]:
    rentabilidades_comp = linha_comp.strip().split(';')

    # Loop pelas rentabilidades e as atribui aos ativos correspondentes
    for ativo_comp, rentabilidade_comparacao in zip(ativos_comparacao, rentabilidades_comp):
        if rentabilidade_comparacao:
            ativos_comp_dict[ativo_comp].append(float(rentabilidade_comparacao))
        else:
            # Se a rentabilidade estiver em branco, tratar como 0
            ativos_comp_dict[ativo_comp].append(0)

# Inicialize uma lista para armazenar o acumulado da carteira
acumulado_carteira = [1] 

# Loop para calcular o acumulado da rentabilidade diária da carteira
for i in range(1, 251):
    acumulado_carteira.append(acumulado_carteira[-1] * ( rentabilidade_dia_geral[i]))

# Inicialize uma lista para armazenar o acumulado da selic
acumulado_comp1 = [1] 

# Loop para calcular o acumulado da rentabilidade diária da selic
for i in range(1, 251):
    acumulado_comp1.append(acumulado_comp1[-1] * (ativos_comp_dict[ativos_comparacao[0]][i]))

# Inicialize uma lista para armazenar o acumulado da IBOV
acumulado_comp2 = [1] 

# Loop para calcular o acumulado da rentabilidade diária da IBOV
for i in range(1, 251):
    acumulado_comp2.append(acumulado_comp2[-1] * (ativos_comp_dict[ativos_comparacao[1]][i]))

def resultados():
    print("")
    print("-"*70)
    print("Ativos com os menores coeficientes de variação entre títulos públicos:")
    print("")
    for ativo, coef in ativos_selecionados_publicos:
        print(ativo, coef)
    print("-"*70)
    print("Ativos com os menores coeficientes de variação entre títulos privados:")
    print("")
    for ativo, coef in ativos_selecionados_privados:
        print(ativo, coef)
    print("-"*70)
    print(f"Na carteira privada devemos investir: {porcentagem_carteira_privada}")
    print("-"*70)
    print(f"Na carteira Pública devemos investir: {porcentagem_carteira_publica}")
    print("")
    print("-"*70)
    print(f"A carteira terá a rentabilidade anual de: {rentabilidade_geral*100}%")
    print("-"*70)
    mp.plot(dias_uteis,acumulado_carteira,label="Carteira")
    mp.plot(dias_uteis,acumulado_comp1,label="Selic")
    mp.plot(dias_uteis,acumulado_comp2,label="IBOV")
    mp.legend()
    mp.show()
        
resultados()