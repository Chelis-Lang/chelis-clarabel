# Chelis Clarabel

`Clarabel.Qp.solve` provides a typed dense `f64` interface to Clarabel. It takes
`P`, `q`, `A`, `b`, a cone list, and explicit settings, then returns either
`Solved` with primal, dual, slack, and diagnostics or `Stopped` with a status.

The package requires Chelis 0.21.0. Its evaluator and compiled C paths use the
native provider carried by that toolchain. The compiler admits the provider
only for this package version and the exact `src/qp.ch` source. A modified
package body runs as ordinary Chelis code and reports provider unavailability.

Install the Reef package from its release, then add it to a project's manifest:

```sh
chelis reef install --from-github Chelis-Lang/chelis-clarabel@v0.1.1
```

```toml
[dependencies]
chelis-clarabel = { version = "=0.1.1" }
```

The solver returns numerical approximations. A property may opt into
`clarabel.qp.ideal_optimality` for a specific dependency-owned `solve` call's
`Solved` arm. That proof assumes an exact real optimum for that call and reports
`proven_modulo_asserted_axiom` with `real_arithmetic`; it does not certify the
returned floating-point vector. The proof lowerer covers supported fixed-size
symbolic QPs with zero and nonnegative cones, including PSD matrices formed as
`BᵀB`.

Run the package examples with the released toolchain:

```sh
chelis eval --file tests/nonnegative.ch
chelis build --target c --output build/nonnegative tests/nonnegative.ch
build/nonnegative/nonnegative
```

The source package and release artifact pair are built with `chelis reef
publish`. Release assets are `chelis-clarabel-0.1.1.tar.zst` and
`chelis-clarabel-0.1.1.chb`; both belong to the same published package version.
