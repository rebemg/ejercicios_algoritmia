"""Ejercicio 5: razón de aproximación del algoritmo basado en MST."""
import itertools

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




def mst_tour(D):
    n = len(D)
    en_arbol = np.zeros(n, bool)
    dist = D[0].copy()
    padre = np.zeros(n, int)
    en_arbol[0] = True
    hijos = {i: [] for i in range(n)}
    dist[0] = np.inf
    for _ in range(n - 1):
        d = np.where(en_arbol, np.inf, dist)
        v = int(np.argmin(d))
        hijos[padre[v]].append(v)
        en_arbol[v] = True
        mejor = (D[v] < dist) & ~en_arbol
        dist[mejor] = D[v][mejor]
        padre[mejor] = v
    orden, pila = [], [0]
    while pila:
        u = pila.pop()
        orden.append(u)
        pila.extend(reversed(hijos[u]))
    return np.array(orden)


def optimo_fuerza_bruta(D, perms):
    n = len(D)
    ruta = np.concatenate([np.zeros((len(perms), 1), int), perms,
                           np.zeros((len(perms), 1), int)], axis=1)
    return D[ruta[:, :-1], ruta[:, 1:]].sum(axis=1).min()


def ejercicio5(n=9, instancias=100, semilla=3):
    print("\n=== Ejercicio 5 ===")
    rng = np.random.default_rng(semilla)
    perms = np.array(list(itertools.permutations(range(1, n))))
    nombres = ["MST puro", "MST + 2-opt", "2-opt (inicio aleatorio)",
               "2-opt (vecino más cercano)", "Recocido simulado"]
    costos = {k: [] for k in nombres}
    optimos = []
    for _ in range(instancias):
        D = matriz_distancias(ciudades_aleatorias(n, rng))
        opt = optimo_fuerza_bruta(D, perms)
        optimos.append(opt)
        t_mst = mst_tour(D)
        costos["MST puro"].append(costo_tour(t_mst, D))
        costos["MST + 2-opt"].append(costo_tour(dos_opt(t_mst, D)[0], D))
        costos["2-opt (inicio aleatorio)"].append(
            costo_tour(dos_opt(rng.permutation(n), D)[0], D))
        costos["2-opt (vecino más cercano)"].append(
            costo_tour(dos_opt(vecino_mas_cercano(D, int(rng.integers(n))), D)[0], D))
        _, c, _ = recocido_simulado(D, rng.permutation(n), 5000, D.mean(), 1e-3,
                                    "exponencial", rng, paso_hist=1000)
        costos["Recocido simulado"].append(c)

    optimos = np.array(optimos)
    razon = np.array(costos["MST puro"]) / optimos
    print(f"  Razón MST puro: media={razon.mean():.3f}, máx={razon.max():.3f} (límite teórico 2)")
    for k in nombres[1:]:
        r = np.array(costos[k]) / optimos
        print(f"  Razón {k:<28} media={r.mean():.3f}  máx={r.max():.3f}")

    fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
    ax[0].hist(razon, bins=15, edgecolor="k", alpha=.8)
    ax[0].axvline(2, color="r", ls="--", label="Límite teórico = 2")
    ax[0].axvline(1, color="g", ls=":", label="Óptimo = 1")
    ax[0].set_xlabel("C_obtenido / C_óptimo")
    ax[0].set_ylabel("Frecuencia")
    ax[0].set_title("Razón de aproximación (MST puro)")
    ax[0].set_xlim(0.9, 2.1)
    ax[0].legend()
    ax[1].boxplot([costos[k] for k in nombres])
    ax[1].set_xticklabels(nombres)
    ax[1].plot(range(1, len(nombres) + 1), [np.mean(optimos)] * len(nombres), "g--",
               label="Óptimo (promedio)")
    ax[1].set_ylabel("Costo del tour")
    ax[1].set_title("Costo por método")
    ax[1].tick_params(axis="x", rotation=25)
    ax[1].legend()
    for a in ax:
        a.grid(alpha=.3)
    plt.tight_layout()
    plt.savefig("figuras/ej5_aproximacion.png", dpi=150)
    plt.close()



if __name__ == "__main__":
    ejercicio5()