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

import os
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

_log = logging.getLogger(__name__)
__version__ = '3.7'


class TestAgent(unittest.TestCase):

    def _create_agent(self, config='../thresholddetection.config'):
        agent = ThresholdDetectionAgent.__new__(ThresholdDetectionAgent)
        agent.vip = Mock()
        agent.config_topics = {}
        agent.vip.config.set_default("config", config)
        agent.vip.config.subscribe(agent._config_add, actions="NEW", pattern="config")
        agent.vip.config.subscribe(agent._config_del, actions="DELETE", pattern="config")
        agent.vip.config.subscribe(agent._config_mod, actions="UPDATE", pattern="config")
        return agent

    def test_config(self):
        agent = self._create_agent('..\\thresholddetection.config')
        assert agent is not None
        agent.vip.config.set_default.assert_called_with('config', '..\\thresholddetection.config')
        agent.vip.config.subscribe.assert_any_call(agent._config_add, actions="NEW", pattern="config")
        agent.vip.config.subscribe.assert_any_call(agent._config_del, actions="DELETE", pattern="config")
        agent.vip.config.subscribe.assert_any_call(agent._config_mod, actions="UPDATE", pattern="config")

    def test_alert_high(self):
        all_calls = []
        agent = self._create_agent('../thresholddetection.config')
        agent._alert('datalogger/log/platform/cpu_percent', 99, 100)
        for call in agent.vip.mock_calls:
            all_calls.append(call)
        assert 'above' in all_calls[4].args[1].context

    def test_alert_low(self):
        all_calls = []
        agent = self._create_agent('../thresholddetection.config')
        agent._alert('datalogger/log/platform/cpu_percent', 99, 90)
        for call in agent.vip.mock_calls:
            all_calls.append(call)
        assert 'below' in all_calls[4].args[1].context

    def test_multi_topic_device_subscription(self):
        agent = self._create_agent()
        config = {
            "devices/campus/building/fake/multi": {
                "OutsideAirTemperature1": {
                    "threshold_max": 60,
                    "threshold_min": 0
                },
                "OutsideAirTemperature2": {
                    "threshold_max": 42
                }
            }
        }
        subscriptions = []
        def mock_subscribe(peer, topic, callback):
            subscriptions.append((topic, callback))

        agent.vip.pubsub.subscribe.side_effect = mock_subscribe
        agent._config_add("config", "NEW", config)

        assert len(subscriptions) == 2
        cb1 = subscriptions[0][1]
        cb2 = subscriptions[1][1]

        # Reset mocks to track _alert calls
        agent.vip.reset_mock()

        # Point 1 > 60: should alert
        cb1('pubsub', 'sender', 'bus', 'devices/campus/building/fake/multi', {}, [{'OutsideAirTemperature1': 75}])
        agent.vip.health.send_alert.assert_called_once()
        assert 'OutsideAirTemperature1' in agent.vip.health.send_alert.call_args[0][1].context
        assert 'above' in agent.vip.health.send_alert.call_args[0][1].context

        agent.vip.reset_mock()

        # Missing point: should not crash or alert
        cb1('pubsub', 'sender', 'bus', 'devices/campus/building/fake/multi', {}, [{'OtherPoint': 100}])
        agent.vip.health.send_alert.assert_not_called()

        # None value: should not crash or alert
        cb1('pubsub', 'sender', 'bus', 'devices/campus/building/fake/multi', {}, [{'OutsideAirTemperature1': None}])
        agent.vip.health.send_alert.assert_not_called()

        # Point 2 > 42: should alert for point 2
        cb2('pubsub', 'sender', 'bus', 'devices/campus/building/fake/multi', {}, [{'OutsideAirTemperature2': 50}])
        agent.vip.health.send_alert.assert_called_once()
        assert 'OutsideAirTemperature2' in agent.vip.health.send_alert.call_args[0][1].context

    def test_standard_subscription_resilience(self):
        agent = self._create_agent()
        config = {
            "campus/building/fake/single_point": {
                "threshold_max": 50,
                "threshold_min": 10
            }
        }
        subscriptions = []
        agent.vip.pubsub.subscribe.side_effect = lambda peer, topic, callback: subscriptions.append((topic, callback))
        agent._config_add("config", "NEW", config)

        assert len(subscriptions) == 1
        cb = subscriptions[0][1]

        # High alert
        agent.vip.reset_mock()
        cb('pubsub', 'sender', 'bus', 'campus/building/fake/single_point', {}, 65)
        agent.vip.health.send_alert.assert_called_once()

        # Low alert
        agent.vip.reset_mock()
        cb('pubsub', 'sender', 'bus', 'campus/building/fake/single_point', {}, 5)
        agent.vip.health.send_alert.assert_called_once()

        # Non-numeric / None resilience
        agent.vip.reset_mock()
        cb('pubsub', 'sender', 'bus', 'campus/building/fake/single_point', {}, "INVALID_STRING")
        cb('pubsub', 'sender', 'bus', 'campus/building/fake/single_point', {}, None)
        cb('pubsub', 'sender', 'bus', 'campus/building/fake/single_point', {}, {'nested': 123})
        agent.vip.health.send_alert.assert_not_called()


def main(argv=sys.argv):
    agent = ThresholdDetectionAgent()


if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
