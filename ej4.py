"""Ejercicio 4: recocido simulado con distintos esquemas de enfriamiento."""
import time

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



def ejercicio4(n=40, iteraciones=30_000, corridas=10, semilla=2):
    print("\n=== Ejercicio 4 ===")
    rng = np.random.default_rng(semilla)
    D = matriz_distancias(ciudades_aleatorias(n, rng))
    T0, Tf = D.mean(), 1e-3
    esquemas = ["lineal", "exponencial", "inverso"]
    hist_prom, tiempos, costos = {}, {}, {}
    for e in esquemas:
        hs, ts, cs = [], [], []
        for r in range(corridas):
            r_rng = np.random.default_rng(1000 + r)
            t0 = r_rng.permutation(n)
            ini = time.perf_counter()
            _, c, h = recocido_simulado(D, t0, iteraciones, T0, Tf, e, r_rng)
            ts.append(time.perf_counter() - ini)
            cs.append(c)
            hs.append(h)
        hist_prom[e] = np.mean(hs, axis=0)
        tiempos[e], costos[e] = np.mean(ts), np.array(cs)
        print(f"  {e:<12} costo medio={costos[e].mean():.3f} "
              f"(min {costos[e].min():.3f})  tiempo medio={tiempos[e]:.2f} s")

    fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
    for e in esquemas:
        h = hist_prom[e]
        ax[0].plot(h[:, 0], h[:, 2], label=e)
    ax[0].set_xlabel("Iteración")
    ax[0].set_ylabel("Mejor costo (promedio)")
    ax[0].set_title("Convergencia vs. iteraciones")
    ax[0].legend()
    for e in esquemas:
        h = hist_prom[e]
        ax[1].plot(h[:, 1], h[:, 2], label=e)
    ax[1].set_xscale("log")
    ax[1].invert_xaxis()
    ax[1].set_xlabel("Temperatura (escala log, enfriando →)")
    ax[1].set_title("Convergencia vs. temperatura")
    ax[1].legend()
    for a in ax:
        a.grid(alpha=.3)
    plt.tight_layout()
    plt.savefig("figuras/ej4_convergencia.png", dpi=150)
    plt.close()

    plt.figure(figsize=(6, 4.5))
    for e in esquemas:
        plt.errorbar(tiempos[e], costos[e].mean(), yerr=costos[e].std(), fmt="o",
                     capsize=4, markersize=9, label=e)
    plt.xlabel("Tiempo de ejecución medio (s)")
    plt.ylabel("Costo final (media ± desv. est.)")
    plt.title("Tiempo vs. calidad")
    plt.grid(alpha=.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("figuras/ej4_tiempo_calidad.png", dpi=150)
    plt.close()



if __name__ == "__main__":
    ejercicio4()