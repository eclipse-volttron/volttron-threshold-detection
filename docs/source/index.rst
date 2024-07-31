volttron-threshold-detection
============================

The ThresholdDetectionAgent will publish an alert when a value published to a topic exceeds or falls below a configured value.

The agent subscribes to the topics listed in the configuration file and publishes alerts when the callback receives a value for the point above the max (if configured) or below the min (if configured) corresponding to the point in the configuration file.

Requires
--------

* python >= 3.10
* volttron >= 10.0

Installation
------------

Before installing, VOLTTRON should be installed and running. Its virtual environment should be active. Information on how to install the VOLTTRON platform can be found `here <https://github.com/eclipse-volttron/volttron-core>`_.

Create a directory called ``config`` and use the change directory command to enter it.

.. code-block:: shell

    mkdir config
    cd config

After entering the config directory, create a file called ``threshold_detection_config.json``, use the below JSON to populate your new file. Refer to the configuration overview if needed.

The Threshold Detection agent supports observing individual point values from their respective topics or from a device's "all" publish. Points to watch are configured as JSON key-value pairs as follows:

* **Key**: The key is the point topic for the point to watch, or the device's "all" topic if watching points from the all publish (i.e. ``"devices/campus/building/device/point"`` or ``"devices/campus/building/device/all"`` if using the all topic).

* **Value**: Using point topic: JSON object specifying the min (``'threshold_min'``) and max (``'threshold_max'``) threshold values for the point. Only one of the thresholds are required, but both may be used.

  Example:

  .. code-block:: json

      {
          "point0": {
              "threshold_max": 10,
              "threshold_min": 0
          },
          "point1": {
              "threshold_max": 42
          }
      }

  Using device "all" topic: JSON object with the key as the point name and value being the threshold object described above.

  Example 2:

  .. code-block:: json

      {
          "devices/fake/fakedevice/all": {
              "OutsideAirTemperature1": {
                  "threshold_max": 60,
                  "threshold_min": 0
              },
              "OutsideAirTemperature2": {
                  "threshold_max": 42
              }
          }
      }

After creating your configuration file, install and start the threshold detection agent in VOLTTRON.

.. code-block:: shell

    vctl install volttron-threshold-detection --agent-config threshold_detection_config.json --vip-identity platform.threshold_detection --start

View the status of the installed agent.

.. code-block:: shell

    vctl status

Development
