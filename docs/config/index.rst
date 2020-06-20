.. _index:

Configuration
=============

All of the configuration for **MQTT IO** is contained within one YAML file. The file is made up of sections, which we'll cover here individually.

Schema
------

The config file is validated at run-time to ensure that it adheres to a required schema. This is done using `Cerberus <https://docs.python-cerberus.org/en/stable/>`_. The schema should be fairly self-explanatory, so we'll list the schema for each config section.

MQTT
----

The ``mqtt`` section configures the connection to an MQTT server. A minimal example being:

.. code-block:: yaml

   mqtt:
     host: mqtt.google.com
     port: 1883


.. yamlsection:: ../../config.schema.yml
   :section: mqtt
   :display_top_node:


.. .. literalinclude:: ../../config.schema.yml
..    :language: yaml
..    :lines: -104