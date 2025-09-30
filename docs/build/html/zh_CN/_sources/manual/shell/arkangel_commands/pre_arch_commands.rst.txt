.. _arkangel_pre_arch_commands:

Pre-Arch Commands
----------------

analyze_logic_resource
~~~~~~~~~~~~~~~~~~~~~~

Analyze the requirements on the number of logic resources, including LUTs, FFs, DSPs etc., for the given benchmarks and device family.
This is to provide the guidelines when selecting and customize FPGA architectures.

.. note:: Running the command will not create/modify any FPGA architecture, casting no impact on any steps in eFPGA development flow


.. option:: --run <string>

  Specify the run id. Each run is independent from each other. If not specified, a default name will be provided. 

  .. note:: If you specify an existing run, the data will be overwritten.

.. option:: --min_lut_size <int>

  Specify the minimum number of inputs for LUT. This is used to sweep the LUT size and find the proper value.  By default, it is 4.

.. option:: --max_lut_size <int>

  Specify the maximum number of inputs for LUT. This is used to sweep the LUT size and find the proper value.  By default, it is 7.

.. option:: --report_qor <string>

  Specify the file path where the *Quality-of-Results* (QoR) should be written to. The file format is csv. See below for an example file which is outputted.

.. csv-table:: Example of pre-arch analysis QoR report file
  :file: examples/pre_arch_qor.csv
  :header-rows: 1

.. option:: --verbosity <int>

  Control the verbosity of the messages. For debugging usage, recommend to set to ``1``. By default, it is `0``, leading to minimum logging messages.

