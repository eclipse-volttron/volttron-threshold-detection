# volttron-threshold-detection
The ThresholdDetectionAgent will publish an alert when a value published to a topic exceeds or falls below a configured
value.

The agent subscribes to the topics listed in the configuration file and publishes alerts when the callback receives a
value for the point above the max (if configured) or below the min (if configured) corresponding to the point in the
configuration file.
# Prerequisites

* Python 3.8

## Python

<details>
<summary>To install Python 3.8, we recommend using <a href="https://github.com/pyenv/pyenv"><code>pyenv</code></a>.</summary>

```bash
# install pyenv
git clone https://github.com/pyenv/pyenv ~/.pyenv

# setup pyenv (you should also put these three lines in .bashrc or similar)
export PATH="${HOME}/.pyenv/bin:${PATH}"
export PYENV_ROOT="${HOME}/.pyenv"
eval "$(pyenv init -)"

# install Python 3.8
pyenv install 3.8.10

# make it available globally
pyenv global system 3.8.10
```
</details>

# Installation
If VOLTTRON is already installed, proceed to setp 3.

1. Create and activate a virtual environment.

    ```shell
    python -m venv env
    source env/bin/activate
    ```
2. Install volttron and start the platform.

    ```shell
    pip install volttron

    # Start platform with output going to volttron.log
    volttron -vv -l volttron.log &
    ```

1. Create a config directory and navigate to it:

    ```shell
    mkdir config
    cd config
    ```
    Navigate to the config directory and create a file called `threshold_detection.config`. Use the examlpes below to populate that file with the correct JSON.
* The Threshold Detection agent supports observing individual point values from their respective topics or from a device's
    all publish.  Points to watch are configured as JSON key-value pairs as follows:

    * Key:  The key is the point topic for the point to watch, or the device's "all" topic if watching points from the all
    publish (i.e. "devices/campus/building/device/point" or "devices/campus/building/device/all" if using the all topic)

    * Value:  Using point topic: JSON object specifying the min ('threshold_min') and max ('threshold_max) threshold values
    for the point.  Only one of the thresholds are required, but both may be used.

    Example:

    ```json
    {
        "point0": {
            "threshold_max": 10,
            "threshold_min": 0
        },
        "point1": {
            "threshold_max": 42
        }
    }
    ```

    Using device "all" topic:  JSON object with the key as the point name and value being the threshold object described
    above

    Example 2:

    ```json
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
    ```
5. After creating your configuration file. install and start the threshold detection agent in VOLTTRON.

    ```shell
    vctl install volttron-threshold-detection --agent-config threshold_detection.config --vip-identity platform.threshold_detection --start --force
    ```

### Example Publish

This example publish uses the example config above along with a fake driver running on the platform.

```
Peer: pubsub
Sender: platform.threshold_detection
Bus:
Topic: alerts/ThresholdDetectionAgent/None_platform_threshold-detection
Headers: {'alert_key': 'devices/fake/fakedevice/all', 'min_compatible_version': '3.0', 'max_compatible_version': ''}
Message: ('{"status": "BAD", "context": '
 '"devices/fake/fakedevice/all(OutsideAirTemperature2) value (50.0)is above '
 'acceptable limit (42)", "last_updated": "2023-11-13T20:30:10.025105+00:00"}')
```
# Disclaimer Notice

This material was prepared as an account of work sponsored by an agency of the
United States Government.  Neither the United States Government nor the United
States Department of Energy, nor Battelle, nor any of their employees, nor any
jurisdiction or organization that has cooperated in the development of these
materials, makes any warranty, express or implied, or assumes any legal
liability or responsibility for the accuracy, completeness, or usefulness or any
information, apparatus, product, software, or process disclosed, or represents
that its use would not infringe privately owned rights.

Reference herein to any specific commercial product, process, or service by
trade name, trademark, manufacturer, or otherwise does not necessarily
constitute or imply its endorsement, recommendation, or favoring by the United
States Government or any agency thereof, or Battelle Memorial Institute. The
views and opinions of authors expressed herein do not necessarily state or
reflect those of the United States Government or any agency thereof.
