# Chelis Clarabel

`Clarabel.Qp.solve` provides a typed dense `f64` interface to Clarabel. It takes
`P`, `q`, `A`, `b`, a cone list, and explicit settings, then returns either
`Solved` with primal, dual, slack, and diagnostics or `Stopped` with a status.

The compiler pin in [`reef.toml`](reef.toml) selects Chelis 0.23.1.

Its evaluator and compiled C paths use the native provider for
`chelis-clarabel` version `0.1.4` and the exact [`src/qp.ch`](src/qp.ch) source.

The source SHA-256 is `dbb1d56ad68458785a7c20bf558dce0136d85ac13d9140fc1fe9d9ab00a1142a`.

This source matches `packages/chelis-clarabel/src/qp.ch` in the compiler source.

A different package version cannot use this provider.
A modified package body executes as ordinary Chelis code and reports provider unavailability.

Install the Reef package from its release, then add it to a project's manifest:

```sh
chelis reef install --from-github Chelis-Lang/chelis-clarabel@v0.1.4
```

```toml
[dependencies]
chelis-clarabel = { version = "=0.1.4" }
```

## Solver contract

The dense quadratic program minimizes `0.5 xᵀ P x + qᵀ x` subject to
`A x + s = b`, with `s` in the declared cones. `P` has shape `[n, n]`,
`q` has shape `[n]`, `A` has shape `[m, n]`, and `b` has shape `[m]`;
every tensor uses `f64`. Cone dimensions must sum to `m`.

[`src/qp.ch`](src/qp.ch) defines the cone constructors, explicit tolerances,
iteration limit, and result types. Handle both `Solved` and `Stopped`:
reaching an iteration limit is a solver outcome, while a wrong dtype or
inconsistent cone dimension is an error.

The solver returns numerical approximations. A property may opt into
`clarabel.qp.ideal_optimality` for a specific dependency-owned `solve` call's
`Solved` arm. That proof assumes an exact real optimum for that call and reports
`proven_modulo_asserted_axiom` with `real_arithmetic`; it does not certify the
returned floating-point vector. The proof lowerer covers supported fixed-size
symbolic QPs with zero and nonnegative cones, including PSD matrices formed as
`BᵀB`.

## Run the examples

From this checkout, use the toolchain selected by the manifest:

```sh
chelis eval --file tests/solve.ch
chelis eval --file tests/nonnegative.ch
chelis eval --file tests/stopped.ch
```

Each prints `main = true`: an unconstrained optimum, a nonnegative-cone
constraint, and an explicit iteration-limit result, respectively. The
[`nonnegative.ch`](tests/nonnegative.ch) example also builds as a native C
executable:

```sh
chelis build --target c --output build/nonnegative tests/nonnegative.ch
build/nonnegative/nonnegative
```

The rejection fixtures are separate from the runnable examples:

```sh
chelis eval --file tests/invalid_cone.ch
chelis eval --file tests/wrong_dtype.ch
```

Both commands must exit with an error: mismatched cone dimensions and an `f32`
matrix passed to the `f64` solver, respectively.

## Package artifacts

The source package and release artifact pair are built with `chelis reef
publish`. Release assets are `chelis-clarabel-0.1.4.tar.zst` and
`chelis-clarabel-0.1.4.chb`. Both belong to the same published package version.
