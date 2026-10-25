import subprocess
import unittest

from check_package import require_failure, require_main


class PackageCheckTests(unittest.TestCase):
    def test_true_main_and_extra_observations_are_accepted(self):
        require_main("empty_values = []\nmain = true\n")

    def test_missing_false_and_duplicate_main_are_rejected(self):
        for output in ("", "main = false\n", "main = true\nmain = true\n", "main = true\nmain = false\n"):
            with self.subTest(output=output), self.assertRaises(RuntimeError):
                require_main(output)

    def test_expected_failure_requires_the_domain_exit_and_diagnostic(self):
        require_failure(subprocess.CompletedProcess([], 1, "", "error: expected f64"), "expected f64")
        for code, diagnostic in ((0, "expected f64"), (-11, "expected f64"), (2, "expected f64"), (1, "unrelated error")):
            with self.subTest(code=code, diagnostic=diagnostic), self.assertRaises(RuntimeError):
                require_failure(subprocess.CompletedProcess([], code, "", diagnostic), "expected f64")


if __name__ == "__main__":
    unittest.main()
