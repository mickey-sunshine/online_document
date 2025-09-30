.. _file_format_qorso_strategy_file:

Qorso Strategy File (.xml)
==========================

The qorso strategy file is designed to provide scalable and adaptive *Quality-of-Result Sign-Off* (Qorso) methodology across different FPGA architectures.
The qorso strategy file is loaded when creating or load a tapeout project (See details in :ref:`file_format_arch_template_file`)

An example of file is shown as follows.

.. literalinclude:: example_qorso_strategy.xml
  :language: xml

.. _file_format_qorso_strategy_file_reserved_words:

Reserved Words
--------------

The reserved words can be used in defining file paths

.. option:: ${PWD}

  The current working directory when running ArkAngel. This keyword will be replaced during runtime

.. option:: ${ROOT_PATH}

  The root path which starting ArkAngel

Global Variables
----------------

Define all the global variables across all the Qorso strategies files that will be loaded.
In the architecture template file, a number of Qorso strategies will be loaded. The global variables are shared among all the strategies in the same type.

There are two types of global variables

- ``sweep`` where the variable in the given name will be swept from a starting value to an end value in a given step
- ``constant`` where the variable will be a constant value 

.. note:: Only numeric values are supported currently!

.. option:: name

  Define the name of the variable, which should be unique. Once defined, the variable can be used as ``${<name>}`` in all the ``from_pins`` and ``to_pins`` definition. For example,

.. code-block:: xml

  <global_variables>
    <sweep name="idx" start="1" end="10" step="1"/>
    <constant name="idx_b" value="2"/>
  </global_variables>
  <strategy ...>
    <path ...>
      <from_pins>
        <!-- This will result in 10 tasks to be auto-generated -->
        <pin>grid_*/fle_${idx}/*in*/<pin>
        <!-- This will result in grid_*/fle_2/*out* to be generated.-->
        <pin>grid_*/fle_${idx_b}/*out*/<pin>
      </from_pins>
    </path>
  </strategy>

.. note:: Only 1 sweep variable is allowed for one strategy
  
.. option:: start="<int>"

  Define the starting value for a variable to sweep

.. option:: end="<int>"

  Define the ending value for a variable to sweep. The end value will be swepted when step is set to ``1``. 

.. option:: step="<int>"

  Define the step for a variable to sweep. Can be either positive or negative numbers. If not specified, the default step is ``1``

.. option:: value="<int>"

  Define the constant value of the variable

Strategy
--------

A strategy can be applied to a number of designs whose name matches the pattern.

.. option:: name="<string>"

  A unique name of the strategy

.. option:: type="<string>"

  Specify the type of the strategy. Can be [ ``timing`` | ``power`` ], each of which will require different set of syntax

.. _file_format_qorso_strategy_file_summary:

Summary
```````

The data to be collected from sign-off reports will be written to ``yaml`` and ``csv`` files
This section defined the type of data to be collected

.. option:: timing_data="<string>"

  For timing strategies, it can be [ ``required time`` | ``arrival time`` | ``slack`` ] 
  For power strategies, it can be [ ``leak power`` | ``total power`` ] 

.. option:: data_type="<string>"

  Only required by timing strategies, it can be [ ``Max`` | ``Min`` | ``Average`` ]

.. option:: scale_factor="<float>"

  Apply a scaling factor on the timing value that is extracted from reports. For example, a required time of 1ns is extracted from report, and a scaling factor of ``1.1`` is defined, the final timing value appears in the summary file will be ``1.1ns``. By default, the scaling factor is set to ``1.0``

.. option:: variable="<string>"

  Define the human readable variable which will represent the extracted timing/power data in the resulting CSV summary file

.. option:: name="<string>"

  Define the architecture variable will represent the extracted timing/power data in the resulting YAML summary file.

.. note:: The architecture variable must match the variable name in arch timing files! Otherwise, timing back-annotation may fail!

Tasks
`````

Under a strategy, a number of tasks can be defined. Each task may be designed to extract a specific type of timing/power data.
All the data of the tasks under the same strategy will be concluded in the summary files (CSV and YAML)

.. _file_format_qorso_strategy_file_design:

Designs
```````

Multiple patterns can be defined under node ``designs``, in order to capture all the designs required.

.. option:: auto_infer_from_tile_type="<string>"

  Define the matching pattern (which can be a regular expression) for the type of tiles which the strategy should be applied to.

Path
````

.. option:: from_pins="<string>"

  Specify the pins which are the starting points of the timing paths which the report timing task should consider. Users can define multiple pins as a list. For instance

.. code-block:: xml

  <from_pins>
    <pin>[get_pins CellA/inputA*]</pin>
    <pin>CellA/inputB*</pin>
  </from_pins>
    

.. note:: If pin is defined as ``[get_pins <pin_name>]``, the pin will be added to the group of starting points of the timing path.

.. note:: If pin is defined without ``get_pins``, the pin existence will be checked, before being added to the group of starting points of the timing path. We also support bus definition in such case. For example, ``cellA/inputB[3:5]``. Each pin in the bus will pass through ``get_pins`` check and then be added to the group of starting points

.. option:: from_edge="<string>"

  Can be [ ``rise`` | ``fall`` | ``both`` ]. Specify the edge type to be considered when analyzing the starting point of a timing path. Typically useful in clock paths. By default, it is ``both``, indicating both rising and falling edges should be considered.

.. option:: to_pin="<string>"

  Specify the pins which are the ending points of the timing paths which the report timing task should consider. The syntax is the same as ``from_pin``

.. option:: to_edge="<string>"

  Can be [ ``rise`` | ``fall`` | ``both`` ]. Specify the edge type to be considered when analyzing the end point of a timing path. Typically useful in clock paths. By default, it is ``both``, indicating both rising and falling edges should be considered.

.. option:: through_pin="<string>"

  Specify the pins which are through points of the timing paths which the report timing task should consider. The syntax is the same as ``from_pin``

.. note:: The sequence of the through pins in the list matters! It determines the sequence of through points which PTPX will follow when analyzing a given timing path. For example, the following code forces a report timing task which starts from ``input_a`` and ends to ``input_b``, which should go through first either ``pin_c[0]`` or ``pin_c[1]``, and then ``pin_d``.

.. code-block:: yaml

    <from_pins>
      <pin>[get_pins input_a]</pin>
    </from_pins>
    <to_pins>
      <pin>[get_pins input_b]</pin>
    </to_pins>
    <through_pins>
      <pin>[get_pins pin_c[0:1]]</pin>
      <pin>[get_pins pin_d]</pin>
    </through_pins>

.. option:: max_delay="<float>"

  Specify the maximum delay between the starting points ``from_pin`` and ending points ``to_pin`` of the timing paths

.. option:: min_delay="<float>"

  Specify the minimum delay between the starting points ``from_pin`` and ending points ``to_pin`` of the timing paths

.. option:: delay_type="<string>"

  Specify the type of the timing paths which the report timing task should consider. Accept the following:

  - ``comb_max`` represents the maximum delay of a combinational timing path
  - ``comb_min`` represents the minimum delay of a combinational timing path
  - ``setup`` represents the setup-time of a in-reg or reg-to-reg timing path
  - ``hold`` represents the hold-time of a in-reg or reg-to-reg timing path

  When the delay type of setup or hold time is specified, users must provide the clock group related to the timing paths using the syntax ``clock_group``

.. option:: clock_group="<string>"

  Specify the clocks related to the timing paths which the report timing task should consider

.. option:: nworst="<int>"

  Specify the number of worst-case paths to be reported. If set a number larger than 1, the timing report will include a number of paths. Use the timing summary task (see details in :ref:`file_format_task_file_timing_summary`) to extract the timing values for better data visibility

.. option:: max_paths="<int>"

  Specify the maximum number of worst-case paths to be reported. If set a number larger than 1, the timing report will include a number of paths. Use the timing summary task (see details in :ref:`file_format_qorso_strategy_file_summary`) to extract the timing values for better data visibility

SDC
```

Specify a list of SDC files that the report timing task should consider. Currently, we support files whose names end with ``.tcl`` or ``.sdc``.

.. note:: Reserved words are applicable to file paths. See details in :ref:`file_format_synth_strategy_file_reserved_words`

For example, 

.. code-block:: xml

  <sdc> 
    <file>${ROOT_PATH}/sdc/common/constants.tcl</file> 
    <file>${ROOT_PATH}/sdc/common/dont_use_cell.tcl</file> 
    <file>${ROOT_PATH}/sdc/io/area_dchain.tcl</file> 
    <file>${ROOT_PATH}/sdc/io/timing.tcl</file> 
    <file>${ROOT_PATH}/sdc/io/power.tcl</file> 
  </sdc> 
