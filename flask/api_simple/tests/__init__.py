import os
import unittest


def run():
    tests = unittest.TestLoader().discover(os.path.dirname(__file__))
    suite = unittest.TestSuite(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
