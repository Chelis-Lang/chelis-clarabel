# Changelog

## [0.1.4] - 2026-11-14

### Changed

- Build with Chelis 0.23.1 and its exact native-provider identity.
- Preserve the canonical QP source and solver behavior.

## [0.1.3] - 2026-10-30

### Changed

- Build against Chelis 0.23.0 with its matching Clarabel native-provider identity.

The QP source and numerical algorithm are unchanged.

## [0.1.2] - 2026-10-25

### Changed

- Build against Chelis 0.22.1 with its matching Clarabel native-provider identity.
- Add Reef conformance scaffolding and compiler-pin guards.
- Check solver examples through evaluator and compiled C execution, including
  invalid cones, wrong dtypes, and unregistered package versions and source bodies.
- Publish the verified source archive and shell artifact together after checking
  the release tag, solver execution, and package identity.

The QP source and numerical algorithm are unchanged.
