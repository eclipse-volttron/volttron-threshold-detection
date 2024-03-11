# -*- coding: utf-8 -*- {{{
# ===----------------------------------------------------------------------===
#
#                 Installable Component of Eclipse VOLTTRON
#
# ===----------------------------------------------------------------------===
#
# Copyright 2024 Battelle Memorial Institute
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# ===----------------------------------------------------------------------===
# }}}

import logging
import sys
import unittest
import uuid

import mock
import pytest
from mock import Mock
from volttron import utils
from volttron.client.messaging.health import STATUS_BAD, Status
from volttron.client.vip.agent import RPC, Agent, Core, PubSub
from volttrontesting.utils import AgentMock

from threshold_detection.agent import ThresholdDetectionAgent

utils.setup_logging()
_log = logging.getLogger(__name__)
__version__ = '3.7'


class TestAgent(unittest.TestCase):

    def setUp(self):
        ThresholdDetectionAgent.__bases__ = (AgentMock.imitate(Agent, Agent()), )

    def test_config(self):
        agent = ThresholdDetectionAgent('..\\thresholddetection.config')
        assert agent is not None
        agent.vip.assert_has_calls(agent.vip.config.set_default('config', 'thresholddetection.config'))
        agent.vip.assert_has_calls(agent.vip.config.subscribe(agent._config_add, actions="NEW", pattern="config"))
        agent.vip.assert_has_calls(agent.vip.config.subscribe(agent._config_del, actions="DELETE", pattern="config"))
        agent.vip.assert_has_calls(agent.vip.config.subscribe(agent._config_mod, actions="UPDATE", pattern="config"))

    def test_alert_high(self):
        all_calls = []
        agent = ThresholdDetectionAgent('../thresholddetection.config')
        agent._alert('datalogger/log/platform/cpu_percent', 99, 100)
        for call in agent.vip.mock_calls:
            all_calls.append(call)
        assert 'above' in all_calls[4].args[1].context

    def test_alert_low(self):
        all_calls = []
        agent = ThresholdDetectionAgent('../thresholddetection.config')
        agent._alert('datalogger/log/platform/cpu_percent', 99, 90)
        for call in agent.vip.mock_calls:
            all_calls.append(call)
        assert 'below' in all_calls[4].args[1].context


def main(argv=sys.argv):
    agent = ThresholdDetectionAgent()


if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
