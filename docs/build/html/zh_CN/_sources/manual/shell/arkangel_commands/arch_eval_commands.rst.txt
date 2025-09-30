.. _arkangel_arch_eval_commands:

Arch Evaluation Commands
------------------------

eval_arch
~~~~~~~~~

  Evaluate the architecture by benchmarking its *Performance, Power and Area* (P.P.A.). For each benchmark, a full flow of HDL-to-Bitstream generation will be performed. If finished without any error, this is the step to generate golden bitstream, for the future use in design verification.

.. option:: --run <string>

  Specify the run id. Each run is independent from each other. If not specified, a default name will be provided. 

  .. note:: If you specify an existing run, the data will be overwritten.

.. option:: --corner <string>

  Specify the corner defined through project file. If not specified, use the default corner. Use the keyword ``all`` to sweep all the available corners. 

.. note:: Expect long runtime and high-usage on computing resource when you choose to sweep all the corners

.. option:: --arch_run <string>

  Specify the run id of architecture development. See details in :ref:`arkangel_arch_dev_commands`. Note that the architecture development should be finished successfully. If not specifed, the latest run will be automatically consideried.

.. option:: --report_qor <string>

  Specify the file path where the *Quality-of-Results* (QoR) should be written to. The file format is csv. See below for an example file which is outputted.

.. csv-table:: Example of arch evaluation QoR report file
  :file: examples/arch_eval_qor.csv
  :header-rows: 1

.. option:: --verbosity <int>

  Control the verbosity of the messages. For debugging usage, recommend to set to ``1``. By default, it is `0``, leading to minimum logging messages.
