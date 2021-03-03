"""
Script to generate unit test vectors for the galois package using Sage.

Install Sage with:
```
sudo apt install sagemath
```
"""
import json
import os
import pickle
import shutil
import numpy as np
from sage.all import *


def io_1d(x_low, x_high):
    X = np.arange(x_low, x_high, dtype=int)
    Z = np.zeros(X.shape, dtype=int)
    return X, Z


def io_2d(x_low, x_high, y_low, y_high):
    X, Y = np.meshgrid(np.arange(x_low, x_high, dtype=int), np.arange(y_low, y_high, dtype=int), indexing="ij")
    Z = np.zeros(X.shape, dtype=int)
    return X, Y, Z


def random_coeffs(low, high, size_low, size_high):
    size = np.random.randint(size_low, size_high)
    return [np.random.randint(low, high) for i in range(size)]


def save_pickle(d, folder, name):
    with open(os.path.join(folder, name), "wb") as f:
        pickle.dump(d, f)


def save_json(d, folder, name, indent=False):
    indent = 4 if indent else None
    with open(os.path.join(folder, name), "w") as f:
        json.dump(d, f, indent=indent)


def make_luts(field, folder):
    print(f"Making LUTs for {field}")
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.mkdir(folder)
    order = field.order()
    ring = PolynomialRing(field, names="x")
    assert field.gen() == field.multiplicative_generator()

    d = {
        "characteristic": int(field.characteristic()),
        "degree": int(field.degree()),
        "order": int(field.order()),
        "alpha": int(field.primitive_element()),
        "prim_poly": np.flip(np.array(field.modulus().list(), dtype=int)).tolist()
    }
    save_json(d, folder, "properties.json", indent=True)

    X, Y, Z = io_2d(0, order, 0, order)
    for i in range(Z.shape[0]):
        for j in range(Z.shape[1]):
            Z[i,j] = field(X[i,j]) +  field(Y[i,j])
    d = {"X": X, "Y": Y, "Z": Z}
    save_pickle(d, folder, "add.pkl")

    X, Y, Z = io_2d(0, order, 0, order)
    for i in range(Z.shape[0]):
        for j in range(Z.shape[1]):
            Z[i,j] = field(X[i,j]) -  field(Y[i,j])
    d = {"X": X, "Y": Y, "Z": Z}
    save_pickle(d, folder, "sub.pkl")

    X, Y, Z = io_2d(0, order, -order-2, order+3)
    for i in range(Z.shape[0]):
        for j in range(Z.shape[1]):
            Z[i,j] = field(X[i,j]) * Y[i,j]
    d = {"X": X, "Y": Y, "Z": Z}
    save_pickle(d, folder, "mul.pkl")

    X, Y, Z = io_2d(0, order, 1, order)
    for i in range(Z.shape[0]):
        for j in range(Z.shape[1]):
            Z[i,j] = field(X[i,j]) /  field(Y[i,j])
    d = {"X": X, "Y": Y, "Z": Z}
    save_pickle(d, folder, "div.pkl")

    X, Z = io_1d(0, order)
    for i in range(X.shape[0]):
        Z[i] = -field(X[i])
    d = {"X": X, "Z": Z}
    save_pickle(d, folder, "add_inv.pkl")

    X, Z = io_1d(1, order)
    for i in range(X.shape[0]):
        Z[i] = 1 / field(X[i])
    d = {"X": X, "Z": Z}
    save_pickle(d, folder, "mul_inv.pkl")

    X, Y, Z = io_2d(1, order, -order-2, order+3)
    for i in range(Z.shape[0]):
        for j in range(Z.shape[1]):
            Z[i,j] = field(X[i,j]) **  Y[i,j]
    d = {"X": X, "Y": Y, "Z": Z}
    save_pickle(d, folder, "exp.pkl")

    X, Z = io_1d(1, order)
    for i in range(Z.shape[0]):
        Z[i] = log(field(X[i]))
    d = {"X": X, "Z": Z}
    save_pickle(d, folder, "log.pkl")

    MIN_COEFFS = 1
    MAX_COEFFS = 12

    X = [random_coeffs(0, order, MIN_COEFFS, MAX_COEFFS) for i in range(20)]
    Y = [random_coeffs(0, order, MIN_COEFFS, MAX_COEFFS) for i in range(20)]
    Z = []
    for i in range(len(X)):
        x = ring(X[i][::-1])
        y = ring(Y[i][::-1])
        z = x + y
        z = np.array(z.list()[::-1], dtype=int).tolist()
        z = z if z != [] else [0]
        Z.append(z)
    d = {"X": X, "Y": Y, "Z": Z}
    save_pickle(d, folder, "poly_add.pkl")

    X = [random_coeffs(0, order, MIN_COEFFS, MAX_COEFFS) for i in range(20)]
    Y = [random_coeffs(0, order, MIN_COEFFS, MAX_COEFFS) for i in range(20)]
    Z = []
    for i in range(len(X)):
        x = ring(X[i][::-1])
        y = ring(Y[i][::-1])
        z = x - y
        z = np.array(z.list()[::-1], dtype=int).tolist()
        z = z if z != [] else [0]
        Z.append(z)
    d = {"X": X, "Y": Y, "Z": Z}
    save_pickle(d, folder, "poly_sub.pkl")

    X = [random_coeffs(0, order, MIN_COEFFS, MAX_COEFFS) for i in range(20)]
    Y = [random_coeffs(0, order, MIN_COEFFS, MAX_COEFFS) for i in range(20)]
    Z = []
    for i in range(len(X)):
        x = ring(X[i][::-1])
        y = ring(Y[i][::-1])
        z = x * y
        z = np.array(z.list()[::-1], dtype=int).tolist()
        z = z if z != [] else [0]
        Z.append(z)
    d = {"X": X, "Y": Y, "Z": Z}
    save_pickle(d, folder, "poly_mul.pkl")

    X = [random_coeffs(0, order, MIN_COEFFS, MAX_COEFFS) for i in range(20)]
    Y = [random_coeffs(0, order, MIN_COEFFS, MAX_COEFFS) for i in range(20)]
    # Ensure no zero polynomials in Y for division
    for i in range(len(Y)):
        while np.array(Y[i]).sum() == 0:
            Y[i] = random_coeffs(0, order, MIN_COEFFS, MAX_COEFFS)
    Q = []
    R = []
    for i in range(len(X)):
        x = ring(X[i][::-1])
        y = ring(Y[i][::-1])
        q = x // y
        r = x % y
        q = np.array(q.list()[::-1], dtype=int).tolist()
        q = q if q != [] else [0]
        Q.append(q)
        r = np.array(r.list()[::-1], dtype=int).tolist()
        r = r if r != [] else [0]
        R.append(r)
    d = {"X": X, "Y": Y, "Q": Q, "R": R}
    save_pickle(d, folder, "poly_divmod.pkl")

    X = random_coeffs(0, order, 1, 6)
    Y = np.arange(0, 5+1, dtype=int)
    Z = []
    x = ring(X[::-1])
    for j in range(len(Y)):
        y = Y[j]
        z = x ** y
        z = np.array(z.list()[::-1], dtype=int).tolist()
        z = z if z != [] else [0]
        Z.append(z)
    d = {"X": X, "Y": Y, "Z": Z}
    save_pickle(d, folder, "poly_exp.pkl")

    X = [random_coeffs(0, order, MIN_COEFFS, MAX_COEFFS) for i in range(20)]
    Y = np.arange(0, order, dtype=int)
    Z = np.zeros((len(X),len(Y)), dtype=int)
    for i in range(len(X)):
        for j in range(len(Y)):
            x = ring(X[i][::-1])
            y = field(Y[j])
            z = x(y)
            Z[i,j] = z
    d = {"X": X, "Y": Y, "Z": Z}
    save_pickle(d, folder, "poly_eval.pkl")


if __name__ == "__main__":
    # Seed the RNG so the outputs are the same for subsequent runs
    np.random.seed(123456789)

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

    field = GF(2, modulus="primitive", repr="int")
    folder = os.path.join(path, "gf2")
    make_luts(field, folder)

    field = GF(5, modulus="primitive", repr="int")
    folder = os.path.join(path, "gf5")
    make_luts(field, folder)

    field = GF(7, modulus="primitive", repr="int")
    folder = os.path.join(path, "gf7")
    make_luts(field, folder)

    field = GF(31, modulus="primitive", repr="int")
    folder = os.path.join(path, "gf31")
    make_luts(field, folder)