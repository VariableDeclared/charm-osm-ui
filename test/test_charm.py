import sys
import unittest
from unittest.mock import patch


sys.path.append('lib')
from ops.testing import Harness


@patch('interface_mysql.MySQLClient')
class TestOSMCharm(unnittest.TestCase):



    def test_set_leader(self):
        from src.charm import OSMUIK8sCharm
        harness = Harness(OSMUIK8sCharm)

        harness.set_leader(False)
        harness.begin()
        self.assertFalse(harness.charm.model.unit.is_leader())