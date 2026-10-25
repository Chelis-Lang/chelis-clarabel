# chelis-clarabel, a Chelis shell

## Repo Identity

State this shell's intent (what users can ultimately do with it) and link a
vision doc. A deliverables checklist is not an intent statement.

<!-- BEGIN CHELIS MANAGED BLOCK: agents-inheritance chelis@0.22.1 (sha256:c56bb9ac6e9f36af) -->
# Chelis Agent Contract

Keep this file concise and relevant to every agent working in this repository.
Each added token is read tens of thousands of times. State a rule once, link the
document that owns the detail, and put the explanation in that document, not here.

`CLAUDE.md` is a symlink to this file so Claude-style and Codex-style entry points do
not drift.

## What Chelis Is

Chelis is a numerical computing language for code that agents write and people
supervise. Tensors carry named dimensions and precision in their type; the compiler
checks shapes, precision, effects, and ownership before anything runs, and `chelis
prove` checks the properties an author states, naming the method behind each result.
The bet is that numerical code an agent can reason about, and a person can review
through its types and properties, beats code whose mistakes first surface at run time.
Chelis is general purpose within numerical computing; the worked examples come from
quantitative finance. Differentiation and machine-learning programs are research
directions, not the definition of the language. It is not a systems language, a web
framework, a deep-learning framework, or a general scripting replacement for Python.
`spec/00-context.md` and `spec/design/chelis_canonical_reference.md` own the full
statement; their specifics may lag, their intent does not. When a tradeoff
appears, apply these in order:

1. **Unambiguity over ergonomics.** The author is an agent. The friction a human feels
   spelling out every type, effect, dtype, and dimension is not worth a reading the
   compiler has to guess at.
2. **Composition over special cases.** A new capability composes existing primitives
   before it earns a new one.
3. **Inference over annotation.** Where the checker determines something uniquely, the
   author does not repeat it; intermediates carry no ascription.
4. **Machine generation first.** A convenience that exists only for a human typist is
   not a reason to add syntax, a default, or a fallback.
5. **Additive sugar only.** Every surface form desugars to the core; nothing in the
   surface has semantics the core lacks.
6. **Explicit over implicit.** No implicit broadcasting (`expand` only), no implicit
   precision promotion, no implicit currying or partial application, no silent
   narrowing at ingress, no hidden effects. Where intent cannot be determined uniquely,
   the compiler rejects.
7. **Small language, big library.** The compiler knows only the closed RISC primitive
   set and its derived built-ins; everything else is a library. The canonical reference
   §8.5 has the core/standard-library/external-library taxonomy.
8. **Future-proof without over-building.** Decide the rule fully now, implement what
   the phase needs, and never narrow a rule to what a lane implements today.

Two corollaries govern how the compiler itself is changed. Chelis is pre-compatibility
unless a controlling contract says otherwise, so prefer the structural design that
makes a defect class impossible over a smaller-blast-radius patch, a legacy default, a
versionless compatibility fallback, or phase deferral; close the class, not the
instance. And determinism is part of the contract: for fixed program text, compiler
build, target, and declared inputs, every check, evaluation, and build result is a
function of those inputs, and feedback that varies between identical runs is a defect.

## Quality Standards

### Spec-First Development

- Before writing implementation, write test stubs derived from the owning spec.
- Every spec requirement should have a corresponding test before the code exists.
- If the spec says "X is a type error," write the failing test before implementing
  the checker.

### Negative Test Parity

- For every test that checks something works, add the corresponding failure test.
- If you cannot name the failure case, the spec understanding is still weak.

### Do Not Trust Green

- Passing tests prove alignment with the tests, not necessarily with the spec.
- After green CI, check what active requirements still lack tests.
- Audit silent fallbacks, default values, empty error vectors, and `unwrap_or` paths.

## Environment And Tooling

### Worktree And Branch Discipline

- The primary checkout (the main worktree in `git worktree list --porcelain`) is live
  developer state. Read-only queries are fine there; never switch branches, edit, build,
  or create scratch artifacts in it.
- Create a dedicated worktree before the first write of every task, including small
  documentation edits and throwaway probes, and give it its own `.venv` with
  `uv venv --python 3.11`; never copy or symlink another checkout's `.venv`.
- A worktree isolates the working tree, the index, and its HEAD reflog. The stash
  stack, `.git/info/exclude`, the hooks directory, and branch reflogs are shared by
  every worktree on the clone. Do not run `git stash` in a shared clone: to discard your
  own changes use `git checkout -- <paths>`; to park them, copy the files to task-owned
  scratch space or commit them on your branch.
- Do not repurpose an unrelated worktree because it appears idle. Reuse only for the
  same PR or immediate follow-up after checking ownership, exact head, status, and active
  processes. Never share a worktree with a reviewer while either of you writes to it.
- After a PR merges, remove its worktree and task-owned target with individual
  `git worktree remove <path>` and `cargo clean --target-dir <path>` commands, never a
  blanket loop, after confirming the PR is merged, nothing uncommitted is worth keeping,
  and no process owns the target. Squash merges mean "commits ahead of `origin/main`"
  proves nothing; compare patch ids when in doubt. Branch deletion is a separate decision.

## Subagents

[`docs/investigations/agent_contract_rationale.md`](https://github.com/Chelis-Lang/chelis/blob/v0.22.1/docs/investigations/agent_contract_rationale.md)
holds the measurements behind these rules.

- Every subagent prompt names the delivery mechanism and the complete expected report.
  A report that is not sent through the platform's final-report channel has not been
  delivered. A subagent never ends its turn merely to wait for a background build or
  notification that cannot wake it: keep ownership through a synchronous wait, or return
  an honest partial result. A reviewer that has delivered its round report is not
  waiting; it stays available for the orchestrator to resume with the fix.
- CI is watched by at most one background waiter whose exit wakes the session, or by
  nobody. Never watch CI from a foreground sleep or poll loop.
- If an agent returns "waiting" or goes idle without the deliverable, resume it
  immediately with the exact missing items. Prefer a labelled partial report over
  silence or an overstated completion claim, and deduplicate repeated reports that
  race with a resume nudge.
- Every follow-up message to a running subagent, and every message to a peer session,
  ends by asking the recipient to acknowledge it and confirm what it will do. No
  acknowledgement by the recipient's next reply means the message was not received:
  resend it, consolidated.
- More than five subagents live at once under one orchestrator needs the user's
  explicit approval and a stated reason. Five is the widest fan-out measured working
  here, not a certified safe width, and it is a separate budget from the CPU one above.
- Every spawn names its model tier and says in one clause why that tier fits: the
  expensive tier for judgement whose errors are costly to detect, the cheap tier for
  mechanical work such as waiting on CI, polling, or transcribing a result. The
  orchestrator states its own context size in the message that announces a spawn.
- Every brief states a numeric report-length budget, and a numeric context budget except
  for red-team rounds. An agent that will exceed its context budget says so and returns
  what it has.
- A brief says which facts the orchestrator has already verified, against what head, and
  that the agent must not re-derive them, and it names what the agent still has to
  establish itself.
- A brief longer than a few paragraphs is a file passed by absolute path, stored where
  it outlives both the agent and the session, never in a per-session scratchpad.
  Inter-agent messages truncate silently near four kilobytes. "Inline" means
  self-contained, the opposite of "read `AGENTS.md`", not pasted into the spawn message.
- Reports come back the same way: the agent writes the report to a file and replies with
  the absolute path and a one-line summary. That reply is the delivery.
- A subagent that reuses a worktree restores its temporary probes and reports the final
  worktree status unless asked to retain them. Before a heavyweight cargo command it
  reports the exact command and expected weight to the orchestrator.

## Writing Chelis Source

Load the [`example-corpus` skill](agent-skills/example-corpus/SKILL.md) before writing
any `.ch`; it carries the Surf style rules, the parse-breaking spellings, and the Deep
AST contract. `spec/02-surf-syntax.md` §0.1 is the authority.

- `chelis build`, `check`, `validate`, and `eval --file` run `chelis fmt --check` and the
  blocking `chelis lint` rules before the front end; style failures block the build.
  `--allow-style-violations` is for emergency local builds only, never CI, and
  `CHELIS_STYLE_GATE_DISABLE=1` is reserved for the integration-test corpus. Run
  `chelis fmt --inplace <file>` and `chelis lint --check` before pushing.
- Type system: no implicit precision promotion, named tensor dimensions match by name,
  no implicit broadcasting (explicit `expand` only), integer literals default to `i32`
  and float literals to `f32`.
- `chelis build` invokes the native compiler for C, HIP, or Metal and produces an
  executable or static library, retaining sources and runtime artifacts. `--emit-c`
  stops after source emission. CPU is the acceptance priority; GPU targets remain
  prerelease. In the chelis repository, `docs/book/src/backends.md` covers C
  builds and `docs/gpu_backends.md` covers HIP and Metal.

## Book

If this shell has a user-facing book (an mdBook under `docs/`): this section
applies to it. If the shell is also published on chelis.ch
(https://chelis.ch/docs/), chelis.ch mirrors the book page for page at
`https://chelis.ch/docs/<package name>/` (chelis: https://chelis.ch/docs/chelis/),
and the chelis.ch text is canonical: book pages are rendered from the site by
the website's `scripts/sync_books.py`, so edit prose on the site and re-render,
or make the same edit in both places in the same change.

The reader is an engineer, or an AI coding agent, writing Chelis code against
this shell. They know the domain but not this repo's internals or history, and
they want to call the API correctly the first time. Every page teaches: what the
API does, a runnable example with its real output, the contract (inputs, domain,
shapes, precision, errors) and the pitfalls.

Never in the book: issue or PR numbers, repo-internal paths (`spec/`, `src/`
internals, `scripts/`, `tests/`, maintainer docs), maintainer or CI commands,
contributor history, process talk (gates, red teams, agent instructions),
status words (planned, not yet, stub, phase, milestone), "see the source" in
place of documentation, em-dashes, and the word "load-bearing". In a shell
published on chelis.ch, `scripts/check_book.py` enforces the mechanical part
in CI.

A change that alters user-visible behavior says so in its changelog entry.
The book documents the latest release: the book, and its chelis.ch page when
published, take the change when that release is documented.

<!-- END CHELIS MANAGED BLOCK: agents-inheritance -->

## Toolchain Policy

Install the pinned toolchain via `chelisup`; never hand-symlink a machine-global
default. Python is uv-managed. See the managed block above for the upstream contract.

## Pin Bump Checklist

A pin bump is a de-narrowing event. Bump only through a `chelis reef conform bump`
PR that runs the blocked-probe suite, the staleness/narrowing audit, and restamps
`docs/CHELIS_SURFACE.md`. Never edit the pin directly on `main`.

## Scaffolding Drift Rule

All shells share one scaffolding shape. Mirror any structural change into the
sibling shells in the same change set, or record a per-repo divergence. Contract
changes land upstream first (`Chelis-Lang/chelis`) and propagate here via
`chelis reef conform sync`.

<!-- shell-local:exclude:begin -->
<!-- ## Review And Merge -->
<!-- ## Spec Authority And Design Discipline -->
<!-- ## Change Hygiene -->
<!-- ## Issue Tracking -->
<!-- ### Build And Gate Commands -->
<!-- ### Python And Scripts -->
<!-- ## The Chelis-Lang Repositories -->
<!-- ## Pointers -->
<!-- shell-local:exclude:end -->

## Package validation and release

This package uses the exact native-provider identity carried by its compiler.
Preserve `src/qp.ch` when changing only packaging. Use published compiler assets;
never rebuild a compiler inside this shell or weaken provider admission.

Every PR receives a fresh local review through `agent-skills/redteam-exec/SKILL.md`.
Hand over a clean exact head and idle worktree; keep its reviewer through repair
verification. Run conformance, formatting, lint, artifact validation and the
positive/negative solver examples. Inspect exact-head hosted CI before squash
merge, then publish versioned artifacts from that merge when authorized.

Positive solver cases must evaluate and execute through native C with
`main = true`. Invalid cones, wrong dtypes, and an unregistered package version
must fail. A build alone does not establish solver execution.

## Scripting

Use each worktree's uv-managed Python 3.11 environment for scripts. CI invokes
`scripts/check_package.py` and its unit tests directly; compiler gate scripts
and compiler path-rule registries do not apply to this package.

## Coordinated compiler updates

Compiler updates use manually reviewed PRs because the native provider identity
must match the carried package version. This package omits the scheduled bump
workflow generated by the generic shell scaffold.
