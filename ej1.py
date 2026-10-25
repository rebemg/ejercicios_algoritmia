"""Ejercicio 1: aceleración paralela (estimate_pi con 1, 2, 4 y 8 procesos)."""
import os
import time
from multiprocessing import Pool, cpu_count

import matplotlib.pyplot as plt
import numpy as np

os.makedirs("figuras", exist_ok=True)


def _aciertos(args):
    n, semilla = args
    rng = np.random.default_rng(semilla)
    xy = rng.random((n, 2))
    return int(np.count_nonzero((xy ** 2).sum(axis=1) <= 1.0))


def estimate_pi(n_muestras, n_procesos, semilla=0):
    trozo = n_muestras // n_procesos
    tareas = [(trozo, semilla + k) for k in range(n_procesos)]
    if n_procesos == 1:
        total = _aciertos(tareas[0])
    else:
        with Pool(n_procesos) as pool:
            total = sum(pool.map(_aciertos, tareas))
    return 4.0 * total / (trozo * n_procesos)


def ejercicio1(n_muestras=40_000_000, repeticiones=3):
    print(f"\n=== Ejercicio 1 (CPUs disponibles: {cpu_count()}) ===")
    procesos = [1, 2, 4, 8]
    tiempos = []
    for p in procesos:
        mejor = np.inf
        for _ in range(repeticiones):
            t0 = time.perf_counter()
            pi = estimate_pi(n_muestras, p)
            mejor = min(mejor, time.perf_counter() - t0)
        tiempos.append(mejor)
        print(f"  {p} procesos: {mejor:.3f} s  (pi ≈ {pi:.5f})")
    speedup = tiempos[0] / np.array(tiempos)

    plt.figure(figsize=(6, 4.5))
    plt.plot(procesos, speedup, "o-", label="Speedup medido")
    plt.plot(procesos, procesos, "k--", label="Speedup ideal")
    plt.xlabel("Número de procesos")
    plt.ylabel("Speedup  (T1 / Tp)")
    plt.title("Ejercicio 1: aceleración paralela")
    plt.xticks(procesos)
    plt.grid(alpha=.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("figuras/ej1_speedup.png", dpi=150)
    plt.close()


if __name__ == "__main__":
    ejercicio1()