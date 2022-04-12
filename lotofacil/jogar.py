from processamento.reajustar_dados import remover_resultado_concursos
from processamento.possibilidades import obter_possibilidades
from processamento.resultados import resultados_ordenados
from calculos.pesos import calcular_numero_pesos
from sorteios.sortear import sortear_numeros
from modelo.modelo import criar_modelo
from dados.dados import carregar_dados
from pandas import DataFrame


def validaGame(jogo):
    cfibo = []
    cimpar = []
    cprimo = []

    fibo = [1, 2, 3, 5, 8, 13, 21]
    impar = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25]
    primo = [2, 3, 5, 7, 11, 13, 17, 19, 23]

    [cfibo.append(n) for n in jogo if n in fibo and n not in cfibo]
    [cimpar.append(n) for n in jogo if n in impar and n not in cimpar]
    [cprimo.append(n) for n in jogo if n in primo and n not in cprimo]

    return cfibo, cimpar, cprimo


# Carrega a base de dados
dados = carregar_dados()

# Inicialização das variáveis
probabilidade = 0.00
predicao_alvo = 0.00
sorteados = list()
procurando = 0

jogos = []

qtd_jogos = int(input("Quantidade de jogos a gerar:\n->"))
qtd_fibo = int(input("Quantidade de fibonacci:\n->"))
qtd_impar = int(input("Quantidade de impares:\n->"))
qtd_primo = int(input("Quantidade de primos:\n->"))

# probabilidade desejada
prob_alvo = 100.0

# Obtém os pesos de cada dezena e um dicionários com as dezenas e seus pesos
peso, numero_pesos = calcular_numero_pesos(dados)

# Obtém o modelo e sua acuracidade
modelo, pontuacao = criar_modelo(dados)

# Carrega e reajusta os demais dados
print()
print('\033[1;33m[Carregando e reajustando os demais dados...]\033[m')
print()

possibilidades = obter_possibilidades()
resultado_concursos = resultados_ordenados(dados)
possibilidades_atualizada = remover_resultado_concursos(possibilidades, resultado_concursos)

# Variável de verificação se o jogo gerado é aceitável
jogo_aceito = False

# Replica até que a probabilidade seja igual à probabilidade desejada e o jogo seja aceitável
while probabilidade < prob_alvo and not jogo_aceito:

    # Atribui a sequência dos números sorteados
    sorteados = sortear_numeros(peso, numero_pesos)
    # Ordena a lista dos números sorteados
    jogo = sorted([numeros[0] for numeros in sorteados])

    # Cria o dataframe com os números sorteados para realizar a predição
    y_alvo = DataFrame(sorteados)
    y_alvo = y_alvo.iloc[:, 0].values
    y_alvo = y_alvo.reshape(1, 15)

    # Faz a predição da Classe/Alvo
    predicao_alvo = modelo.predict(y_alvo)

    # Achando a probabilidade
    predict_proba = modelo.predict(y_alvo)
    probabilidade = round((predict_proba[0][0] * 100), 1)

    # Valida se o jogo é possível e se ainda não foi sorteado em algum concurso
    if probabilidade >= prob_alvo:

        cfibo, cimpar, cprimo = validaGame(jogo)

        if len(cfibo) == qtd_fibo and len(cimpar) == qtd_impar and len(cprimo) == qtd_primo:
            jogo_aceito = [True if jogo in possibilidades_atualizada else False]

            if jogo_aceito and jogo not in jogos and len(jogos) < qtd_jogos:
                jogos.append(jogo)
                jogo_aceito = False
            else:
                continue
    else:
        jogo_aceito = False

    # Conta qts vezes procurou a sequência até atingir a probabilidade desejada
    procurando += 1

    # Formata a sequência de números sorteados para ser imprimida na tela
    sequencia = [str(numero[0]).zfill(2) for numero in sorteados]

    ''' Imprime as informações obtidas no ciclo atual de execução enquanto a
        probabilidade desejada não foi encontrada'''
    print(f'Alvo = ({prob_alvo}%) - ACURAC.: {round((pontuacao * 100), 1)}% - Rep.: {str(procurando).zfill(7)}'
          f' - Prob. Enc.: ({str(probabilidade).zfill(2)}%) Sequência: [ ', end='')

    print(*sequencia, ']')

    # Se o jogo não é aceitável, zera a probabilidade para gerar novo jogo
    if not jogo_aceito:
        probabilidade = 0.0


# Resultados
print(f'\nAcuracidade do Modelo: {round((pontuacao * 100), 1)}%')

print('\n0 = Não tem chance de ganhar | 1 = Tem chance de ganhar')
print(f'Resultado: (Previsão Modelo) = {predicao_alvo[0][0]}')

print(f'\nProbabilidade das dezenas sairem: {probabilidade}%')

for k, v in enumerate(jogos):
    cfibo, cimpar, cprimo = validaGame(v)
    print(f'\nNúmeros ordenados do jogo {k}:  {v}')
    print(f'Números Fibo: {cfibo}')
    print(f'Números Impares: {cimpar}')
    print(f'Números Primos: {cprimo}')
print(f'\n\nTentativas: {procurando}')
