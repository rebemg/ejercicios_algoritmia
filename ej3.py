"""Ejercicio 3: 2-opt desde inicio aleatorio vs. vecino más cercano."""
import matplotlib.pyplot as plt
import numpy as np

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

os.makedirs("figuras", exist_ok=True)


def ciudades_aleatorias(n, rng):
    return rng.random((n, 2))


def matriz_distancias(p):
    return np.linalg.norm(p[:, None, :] - p[None, :, :], axis=2)


def costo_tour(t, D):
    t = np.asarray(t)
    return D[t, np.roll(t, -1)].sum()


def vecino_mas_cercano(D, inicio):
    n = len(D)
    visitado = np.zeros(n, bool)
    tour = [inicio]
    visitado[inicio] = True
    for _ in range(n - 1):
        d = D[tour[-1]].copy()
        d[visitado] = np.inf
        sig = int(np.argmin(d))
        tour.append(sig)
        visitado[sig] = True
    return np.array(tour)


def dos_opt(tour, D):
    t = np.array(tour)
    n = len(t)
    mejoras = 0
    hay_mejora = True
    while hay_mejora:
        hay_mejora = False
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                a, b, c, d = t[i - 1], t[i], t[j], t[(j + 1) % n]
                if D[a, c] + D[b, d] - D[a, b] - D[c, d] < -1e-12:
                    t[i:j + 1] = t[i:j + 1][::-1].copy()
                    mejoras += 1
                    hay_mejora = True
    return t, mejoras


def recocido_simulado(D, tour0, iteraciones, T0, Tf, esquema, rng, paso_hist=100):
    n = len(D)
    t = np.array(tour0)
    costo = costo_tour(t, D)
    mejor, mejor_costo = t.copy(), costo
    hist = []
    for k in range(iteraciones):
        f = k / iteraciones
        if esquema == "lineal":
            T = T0 - (T0 - Tf) * f
        elif esquema == "exponencial":
            T = T0 * (Tf / T0) ** f
        elif esquema == "inverso":
            T = T0 / (1 + (T0 / Tf - 1) * f)
        else:
            raise ValueError(esquema)
        i = rng.integers(1, n - 1)
        j = rng.integers(i + 1, n)
        a, b, c, d = t[i - 1], t[i], t[j], t[(j + 1) % n]
        delta = D[a, c] + D[b, d] - D[a, b] - D[c, d]
        if delta < 0 or rng.random() < np.exp(-delta / T):
            t[i:j + 1] = t[i:j + 1][::-1].copy()
            costo += delta
            if costo < mejor_costo - 1e-12:
                mejor_costo, mejor = costo, t.copy()
        if k % paso_hist == 0:
            hist.append((k, T, mejor_costo))
    return mejor, mejor_costo, np.array(hist)



def ejercicio3(n=30, instancias=50, semilla=1):
    print("\n=== Ejercicio 3 ===")
    rng = np.random.default_rng(semilla)
    mej = {"Aleatoria": [], "Vecino más cercano": []}
    cost = {"Aleatoria": [], "Vecino más cercano": []}
    for _ in range(instancias):
        D = matriz_distancias(ciudades_aleatorias(n, rng))
        t_ale = rng.permutation(n)
        t_nn = vecino_mas_cercano(D, int(rng.integers(n)))
        for nombre, t0 in [("Aleatoria", t_ale), ("Vecino más cercano", t_nn)]:
            t, m = dos_opt(t0, D)
            mej[nombre].append(m)
            cost[nombre].append(costo_tour(t, D))
    for k in mej:
        print(f"  {k:<20} mejoras: media={np.mean(mej[k]):.1f}  "
              f"costo óptimo local: media={np.mean(cost[k]):.3f}")

    fig, ax = plt.subplots(1, 2, figsize=(10, 4.5))
    ax[0].boxplot(list(mej.values()))
    ax[0].set_xticklabels(list(mej.keys()))
    ax[0].set_title("Nº de mejoras hasta el óptimo local")
    ax[1].boxplot(list(cost.values()))
    ax[1].set_xticklabels(list(cost.keys()))
    ax[1].set_title("Costo del óptimo local alcanzado")
    for a in ax:
        a.grid(alpha=.3)
    fig.suptitle(f"2-opt, {instancias} instancias de {n} ciudades")
    plt.tight_layout()
    plt.savefig("figuras/ej3_2opt.png", dpi=150)
    plt.close()



if __name__ == "__main__":
    ejercicio3()