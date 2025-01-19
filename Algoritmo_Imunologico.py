import random
import math
import matplotlib.pyplot as plt
import logging

X_MIN = 0
X_MAX = 10
N1 = 50 # Quantidade de melhores indivíduos selecionados é o tamanho da populacao inteira
P = 3 # letra grega rho
BETA = 1 # letra grega beta
PRECISION = 4
MUTATION_MIN = 10**-PRECISION# quantos pontos em x a mutacao pode variar
MUTATION_MAX = 0.01# quantos pontos em x a mutacao pode variar
MAX_IT = 50


logger = logging.basicConfig(level=logging.WARNING, format="%(levelname)s:%(funcName)s:%(message)s")
logger = logging.getLogger(__name__)

# Se nao muta, a referencia podia ser a mesma do pai, otimizacao de memoria


def round_result(res):
    return round(res, PRECISION)

class Individuo:
    def __init__(self, x1 = None, x2 = None, fitness = None, numero_clones = None, taxa_mutacao = None):
        self.x1 = x1
        self.x2 = x2
        self.f_objetivo = self.funcao_objetivo()
        self._fitness = fitness
        self._numero_clones = numero_clones
        self._taxa_mutacao = taxa_mutacao
        #aptidao = fitness
        
    @property
    def fitness(self):
        """ #Debugging purpose
            if self._fitness == None:
            print(f"valor de fitness nao foi atribuido")
            raise ValueError("Valor de fitness nao foi atribuido") """
        return self._fitness
    
    @property
    def numero_clones(self):
        return self._numero_clones
    
    @property
    def taxa_mutacao(self):
        #if self._taxa_mutacao == None:
        #    raise ValueError("Valor de taxa de mutacao nao foi atribuido")
        return self._taxa_mutacao
    
    @fitness.setter
    def fitness(self, value):
        self._fitness = round_result(value)
        
    @numero_clones.setter
    def numero_clones(self, value):
        self._numero_clones = round_result(value)
        
    @taxa_mutacao.setter
    def taxa_mutacao(self, value):
        self._taxa_mutacao = round_result(value)
        
    def funcao_objetivo(self):
        if self.x1 == None or self.x2 == None:
            raise ValueError("Valores de x1 e x2 nao foram atribuidos")
        return round_result(math.sqrt(self.x1)*math.sin(self.x1) * math.sqrt(self.x2)*math.sin(self.x2))
        
    def mutacao(self, convergencia = 0):
        def aplicar_mutacao(valor):
            delta = random.uniform(MUTATION_MIN, MUTATION_MAX) * valor
            if random.uniform(0, 1) <= 0.5:
                delta = -delta
            return round_result(max(X_MIN, min(X_MAX, valor + delta)))
        
        if random.uniform(0, 1) <= 0.5:
            if random.uniform(0, 1) <= self.taxa_mutacao:
                #print(f"Mutacao x1 (antes): {self.x1}")
                self.x1 = aplicar_mutacao(self.x1)
                #print(f"Mutacao x1 (depois): {self.x1}")
                if random.uniform(0, 1) <= self.taxa_mutacao:
                    self.x2 = aplicar_mutacao(self.x2)
                    #logger.debug(f"Mutacao x2: {self.x2}")
                self.f_objetivo = self.funcao_objetivo()
                
        else:
            if random.uniform(0, 1) <= self.taxa_mutacao:
                self.x2 = aplicar_mutacao(self.x2)
                #logger.debug(f"Mutacao x2: {self.x2}")
                if random.uniform(0, 1) <= self.taxa_mutacao:
                    self.x1 = aplicar_mutacao(self.x1)
                    #logger.debug(f"Mutacao x1: {self.x1}")
            self.f_objetivo = self.funcao_objetivo()
            
    def clone(self):
        clone = Individuo(self.x1, self.x2, taxa_mutacao=self.taxa_mutacao)
        clone.mutacao()
        clone.taxa_mutacao = 0
        return clone
    
    def __str__(self):
        return f"x1: {self.x1}, x2: {self.x2}, f_obj: {self.f_objetivo} fitness: {self.fitness}"
        #return f"x1: {self.x1}, x2: {self.x2}, f_obj: {self.f_objetivo} fitss: {self.fitness}, n_clon: {self.numero_clones}, t_mut: {self.taxa_mutacao}"
    
    def __repr__(self):
        return self.__str__()

class Populacao:
    def __init__(self, individuos = []):
        self.individuos = individuos
        self.gen_fitness()
    
    def __getitem__(self, index):
        return self.individuos[index]
    
    def __setitem__(self, index, value):
        self.individuos[index] = value
     
    def append(self, individuo:Individuo):
        self.individuos.append(individuo)
        
    def __len__(self):
        return len(self.individuos)       
            
    def selecao(self, top):
        # Seleciona os melhores individuos
        self.individuos = self.individuos[:top]

    def gen_fitness(self):
        for individuo in self.individuos:
            individuo.fitness = round_result(individuo.funcao_objetivo() + 10) # Adiciona 10 para evitar valores negativos
        
        self.sort_on_fitness()
        return 
    
    def sort_on_fitness(self):
        self.individuos = sorted(self.individuos, key=lambda x: x.fitness, reverse=True)
        return self.individuos
    
    def str_top(self, amount):
        string_pop = ""
        for i in range(amount):
            string_pop += f"Individuo {i}: {self.individuos[i]}\n"
        #string_pop = string_pop.rstrip("\n")  # Remove the last newline character
        return string_pop
    
    def __str__(self):
        index = 0
        string_pop = ""
        for individuo in self.individuos:
            string_pop += "Individuo " + str(index) + ": "
            string_pop += str(individuo) + "\n"
            index += 1
        string_pop = string_pop.rstrip("\n")  # Remove the last newline character
        #string_pop += "]"
        return f"{string_pop}"
    
class Infeccao:
    # Pratica uma iteracao de infeccao
    def __init__(self, mem_populacao:Populacao):
        self.mem_populacao = mem_populacao # deve estar sorteada o fitness dela ja       

    def cloning(self, Dmax):
        def taxa_mutacao(individuo:Individuo, Dmax) -> float:
            D_star = individuo.fitness / Dmax
            alpha = round_result(math.exp(-P*D_star))
            return alpha

        # Taxa mutacao
        for individuo in self.mem_populacao:
            individuo.taxa_mutacao = taxa_mutacao(individuo, Dmax)
        
        # Numero Clones
        for i in range(len(self.mem_populacao)):
            self.mem_populacao[i].numero_clones = int(BETA * len(self.mem_populacao) / (i+1))
        
        tam_populacao = len(self.mem_populacao)
        for i in range(tam_populacao):
            for j in range(self.mem_populacao[i].numero_clones):
                clone = self.mem_populacao[i].clone()
                self.mem_populacao.append(clone)
                # Todos os membros da populacao inicial podem ser substituidos

        return

    def infeccao(self):
        # A populacao ja vem ordenada
        Dmax = self.mem_populacao[0].fitness
        self.cloning(Dmax)
        self.mem_populacao.gen_fitness()
        self.mem_populacao.selecao(N1)
        return
    
    def __repr__(self) -> str:
        return f"tam populacao: {len(self.mem_populacao)}"
        
class Geracao:
    def __init__(self, populacao: Populacao, populacao_anterior = None):
        self.populacao = populacao
        #self.populacao_anterior = populacao_anterior
        
    def new_gen(self):
        #max_it = 50
        infeccao = Infeccao(self.populacao)
        infeccao.infeccao()
        logger.debug(f"Populacao apos infeccao:\n{self.populacao.str_top(3)}")
        return self.populacao
    
    def make_generations(self):
        # Retorna o melhor de cada geracao
        max_it = MAX_IT
        melhores = []
        melhores.append(self.populacao[0])
        while(max_it > 0):
            self.new_gen()
            melhores.append(self.populacao[0])
            max_it -= 1
        return melhores
            
    def __str__(self):
        return f"Populacao: {self.populacao}, Populacao Anterior: {self.populacao_anterior}"    

def populacao_inicial(tamanho_populacao = N1):
    #if tamanho_populacao != N1:
    tamanho_populacao *= 2
    populacao = []
    for i in range(tamanho_populacao):
        x1 = round_result(random.uniform(X_MIN, X_MAX))
        x2 = round_result(random.uniform(X_MIN, X_MAX))
        populacao.append(Individuo(x1, x2))
    return populacao

def populacao_teste():
    populacao = []
    populacao.append(Individuo(1.8116, 7.3516))
    populacao.append(Individuo(1.8116, 7.3516))
    populacao.append(Individuo(1.8116, 7.3516))
    populacao.append(Individuo(1.8116, 7.3516))
    populacao.append(Individuo(1.8014, 7.3521))
    populacao.append(Individuo(1.8219, 7.3511))
    populacao.append(Individuo(1.8116, 7.3516))
    populacao.append(Individuo(1.8116, 7.3516))
    populacao.append(Individuo(1.8219, 7.3511))
    populacao.append(Individuo(1.8014, 7.3521))
    
    return populacao

def plot_evolution(melhores, tamanho_populacao = N1):
    x = [i for i in range(len(melhores))]
    y = [melhor.f_objetivo for melhor in melhores]
    plt.figure(figsize=(14, 6))
    plt.xticks(range(0, max(x) + 1, 20))
    plt.grid()
    plt.plot(x, y, marker='o')
    #plt.text(1, 1, 'boxed italics text in data coords', style='italic',)
    plt.xlabel('Geracao')
    plt.ylabel('Melhor Individuo (f_objetivo)')
    plt.title(f'Evolução da População (Tamanho: {tamanho_populacao})')
    plt.show()

# populacao_teste = populacao_inicial(5)

# print(populacao_teste[2])
pop = Populacao(populacao_inicial())
logger.debug(f"Populacao Inicial\n{pop.str_top(10)}")
gen = Geracao(pop)
melhores = gen.make_generations()

#melhores = gen.make_generations(100)
print(f"Final Population: \n{gen.populacao.str_top(3)}")
plot_evolution(melhores)
