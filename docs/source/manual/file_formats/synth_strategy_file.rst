.. _file_format_synth_strategy_file:

Synthesis Strategy File (.xml)
==============================

The synthesis strategy file is designed to provide scalable and adaptive synthesis methodology across different FPGA architectures.
The synthesis strategy file is loaded when creating or load a tapeout project (See details in :ref:`file_format_arch_template_file`)

An example of file is shown as follows.

.. literalinclude:: example_synth_strategy.xml
  :language: xml

.. _file_format_synth_strategy_file_reserved_words:

Reserved Words
--------------

The reserved words can be used in defining file paths

.. option:: ${PWD}

  The current working directory when running ArkAngel. This keyword will be replaced during runtime

.. option:: ${ROOT_PATH}

  The root path which starting ArkAngel

Strategy
--------

A strategy can be applied to a number of designs whose name matches the pattern.

.. option:: name="<string>"

  A unique name of the strategy

.. option:: default="<bool>"

  Specify if the strategy should be considered as default. By default, it is false. The default strategy is used for blocks whose names do not match any existing patterns of strategies. See :ref:`file_format_synth_strategy_file_design:` for details.


.. _file_format_synth_strategy_file_design:

Designs
```````

Multiple patterns can be defined under node ``designs``, in order to capture all the designs required.

.. option:: pattern="<string>"

  Define the matching pattern (which can be a regular expression) for design names which the strategy should be applied to.

Target Libraries
````````````````

Define a list of standard cell libraries to be used in this strategy. The names of the libraries must match the definition in the PDK configuration file. See details in :ref:`file_format_pdk_file_stdcell`

.. option:: lib="<string>"

  Define the target libraries to be used for the blocks.

Compile Options
```````````````

Define the options when synthesis the fabric netlists.

.. option:: type="<string>"

  Can be ``ultra`` or ``regular``. Define the compilation command to be used when running synthesis. Take example of Synopsys Design Compiler, the ``ultra`` indicates to use the ``compile_ultra`` command, while the ``regular`` indicates to use the widely used ``compile``

.. option:: optimization="<string>

  Can be [ ``area`` | ``timing`` | ``power`` | ``balanced`` ]. Define the optimization objective when compile the design. Only applicable when regular compilation type is applied.

.. option:: effort="<string>"

  Can be [ ``high`` | ``low`` ]. Define the level of optimization effort to be applied. Only applicable when optimization objective is specified.

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
