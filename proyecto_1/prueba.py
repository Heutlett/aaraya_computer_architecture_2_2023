import time
from datetime import datetime

def generate_random(a,b, seed):    

    # Calculamos un número aleatorio entre a y b a partir del tiempo actual en milisegundos
    numero_aleatorio = (((seed * 1115245 + 12345) // 65536) % (b - a + 1)) + a

    return numero_aleatorio

def generate_seed():
    ahora = datetime.now()
    hora_actual = ahora.strftime("%H:%M:%S.%f")

    hora_sin_caracteres = int(hora_actual.replace(":", "").replace(".", ""))
    
    return hora_sin_caracteres

def binomial_distribution(n, p, k):
    """
    Esta función calcula la distribución binomial
    """
    # Calcular el coeficiente binomial
    coef = factorial(n) / (factorial(k) * factorial(n-k))

    # Calcular la probabilidad de éxito y fracaso
    success_prob = p**k
    failure_prob = (1-p)**(n-k)

    # Calcular la probabilidad de k éxitos
    prob = coef * success_prob * failure_prob

    return prob

def geometric_distribution(p, k):
    """
    Esta función calcula la distribución geométrica
    """
    # Calcular la probabilidad de k ensayos hasta el primer éxito
    prob = (1-p)**(k-1) * p

    return prob

def factorial(num):
    """
    Esta función calcula el factorial de un número
    """
    if num == 0:
        return 1
    else:
        return num * factorial(num-1)

# Definimos los límites a y b
a = 1
b = 100

seed = generate_seed()
random = generate_random(5,20,seed)
random = 1/random


print(seed)
print(random)