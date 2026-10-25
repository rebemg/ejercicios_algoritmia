"""Ejercicio 2: mochila voraz (valor/peso vs. menor peso)."""
import matplotlib.pyplot as plt
import os

os.makedirs("figuras", exist_ok=True)

def mochila_voraz(items, capacidad, criterio):
    if criterio == "razon":
        orden = sorted(items, key=lambda x: -x[2] / x[1])
    elif criterio == "peso":
        orden = sorted(items, key=lambda x: x[1])
    else:
        raise ValueError(criterio)
    elegidos, usado, valor = [], 0, 0
    for nombre, w, v in orden:
        if usado + w <= capacidad:
            elegidos.append(nombre)
            usado += w
            valor += v
    return elegidos, usado, valor


def ejercicio2():
    print("\n=== Ejercicio 2 ===")
    capacidad = 5
    items = [("A", 1, 1), ("B", 2, 2), ("C", 4, 10)]
    print(f"  Capacidad = {capacidad}; objetos (nombre, peso, valor) = {items}")

    res = {}
    for crit, etiqueta in [("razon", "Valor/peso"), ("peso", "Menor peso")]:
        res[etiqueta] = mochila_voraz(items, capacidad, crit)

    print(f"  {'Método':<12}{'Objetos':<12}{'Capacidad usada':<17}{'Valor'}")
    for m, (el, u, v) in res.items():
        print(f"  {m:<12}{','.join(el):<12}{u}/{capacidad:<15}{v}")

    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    metodos = list(res)
    ax[0].bar(metodos, [res[m][1] for m in metodos], color=["tab:blue", "tab:orange"])
    ax[0].axhline(capacidad, color="k", ls="--", label="Capacidad")
    ax[0].set_title("Capacidad usada")
    ax[0].legend()
    ax[1].bar(metodos, [res[m][2] for m in metodos], color=["tab:blue", "tab:orange"])
    ax[1].set_title("Valor total")
    for a in ax:
        for r in a.patches:
            a.annotate(f"{r.get_height():g}", (r.get_x() + r.get_width() / 2, r.get_height()),
                       ha="center", va="bottom")
    fig.suptitle(f"Mochila voraz (capacidad {capacidad}); objetos: "
                 + ", ".join(f"{n}(w={w},v={v})" for n, w, v in items))
    plt.tight_layout()
    plt.savefig("figuras/ej2_mochila.png", dpi=150)
    plt.close()



if __name__ == "__main__":
    ejercicio2()