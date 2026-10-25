"""Execute the package's solver examples and provider-admission controls."""

from pathlib import Path
import shutil
import subprocess
import tempfile
import tomllib


def require_main(output: str) -> None:
    if [line for line in output.splitlines() if line.startswith("main =")] != ["main = true"]:
        raise RuntimeError(f"expected exactly one true main result: {output!r}")


def require_failure(result: subprocess.CompletedProcess[str], diagnostic: str) -> None:
    if result.returncode != 1 or diagnostic not in result.stderr:
        raise RuntimeError(f"expected exit 1 with {diagnostic!r}: {result}")


def validate(root: Path) -> None:
    root = root.resolve()
    manifest = (root / "reef.toml").read_text()
    package = tomllib.loads(manifest)["package"]
    compiler = package["compiler"]
    if not compiler.startswith("="):
        raise RuntimeError("package compiler must be pinned exactly")
    prefix = ["chelis", "+" + compiler[1:]]

    def run(arguments: list[str], directory: Path = root) -> subprocess.CompletedProcess[str]:
        return subprocess.run(prefix + arguments, cwd=directory, capture_output=True, text=True, timeout=180)

    def success(result: subprocess.CompletedProcess[str]) -> None:
        if result.returncode:
            raise RuntimeError(f"command failed: {result}")

    def build(name: str, directory: Path) -> Path:
        output = directory / "target" / "package-check" / name
        success(run(["build", f"tests/{name}.ch", "--target", "c", "--output", str(output)], directory))
        return output / name

    def execute(binary: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run([str(binary)], capture_output=True, text=True, timeout=30)

    for name in ("solve", "nonnegative", "stopped"):
        evaluated = run(["eval", "--file", f"tests/{name}.ch"])
        success(evaluated)
        require_main(evaluated.stdout)
        native = execute(build(name, root))
        success(native)
        if native.stdout != evaluated.stdout:
            raise RuntimeError(f"{name}: evaluator and native output differ")

    require_failure(run(["eval", "--file", "tests/wrong_dtype.ch"]), "expected f64, got f32")
    require_failure(run(["build", "tests/wrong_dtype.ch", "--target", "c", "--output", "target/wrong-dtype"]), "expected f64, got f32")
    require_failure(run(["eval", "--file", "tests/invalid_cone.ch"]), "cone dimensions sum")
    require_failure(execute(build("invalid_cone", root)), "cone dimensions sum")

    target = root / "target"
    target.mkdir(exist_ok=True)
    for variant in ("wrong-version", "changed-source"):
        with tempfile.TemporaryDirectory(prefix=variant + "-", dir=target) as temporary:
            directory = Path(temporary)
            shutil.copytree(root / "src", directory / "src")
            (directory / "tests").mkdir()
            shutil.copy2(root / "tests/solve.ch", directory / "tests/solve.ch")
            changed = manifest
            diagnostic = "Clarabel native provider unavailable"
            if variant == "wrong-version":
                token = f'version = "{package["version"]}"'
                if manifest.count(token) != 1:
                    raise RuntimeError("expected one package version declaration")
                changed = manifest.replace(token, 'version = "0.0.0"')
            else:
                source = directory / "src/qp.ch"
                body = source.read_text()
                token = 'fail("Clarabel native provider unavailable")'
                if body.count(token) != 1:
                    raise RuntimeError("expected the ordinary provider fallback body")
                diagnostic = "modified package body"
                source.write_text(body.replace(token, f'fail("{diagnostic}")'))
            (directory / "reef.toml").write_text(changed)
            require_failure(run(["eval", "--file", "tests/solve.ch"], directory), diagnostic)
            require_failure(execute(build("solve", directory)), diagnostic)
    print("PACKAGE CHECK: PASS")


if __name__ == "__main__":
    validate(Path(__file__).resolve().parents[1])
