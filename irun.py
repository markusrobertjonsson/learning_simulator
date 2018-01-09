import sys
import unittest

from tests.test_plot_properties import TestPlotProperties

suite = unittest.TestLoader().loadTestsFromTestCase(TestPlotProperties)
unittest.TextTestRunner(verbosity=1, stream=sys.stderr).run(suite)
