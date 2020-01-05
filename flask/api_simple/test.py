import unittest

from . import test_case


def main():
    tests = unittest.TestLoader().loadTestsFromModule(test_case)
    suite = unittest.TestSuite(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == "__main__":
    main()
