.. _file_format_benchmark_file:

Benchmark File (.xml)
=====================

The benchmark file aims to provide a standard way for users to define the required benchmark files for eFPGA evaluation
It is an interchangeable file between *Graphical User Interface* (GUI) and EDA engines.
Users can use GUI to generate a benchmark file or write their own benchmark file.
Benchmark files are loaded when creating or load a tapeout project (See details in :ref:`file_format_project_file`)

An example of file is shown as follows.

.. literalinclude:: example_benchmark.xml
  :language: xml

Reserved Words
--------------

The reserved words can be used in defining file paths

.. option:: ${PWD}

  The current working directory when running ArkAngel. This keyword will be replaced during runtime

.. option:: ${ROOT_PATH}

  The root path which starting ArkAngel

Time Stamps
-----------

.. option:: author="<string>"

  The author who creates the project file. Used by GUI.

.. option:: created="<string>"

  The date when the project file is created for the first time. If this is a new project to create, the stamp will be overwritten by the actual creation date.

.. option:: last_modified="<string>"

  The date when the project file is modified for the last time.

.. option:: tool_version="<string>"

  The tool version when the project file should be used. This is to avoid mis-use of project files across different versions of ArkAngel.


Benchmark
---------

For each benchmark, these are the general syntax 

.. option:: name="<string>"

  A unique name of the benchmark, impacting the naming of files/directories in the assoicated workspace

.. option:: suite="<string>"

  The benchmark suite which the benchmark is categorized. Evaluation can be applied by suites.

Design Files
------------

RTL design files can be defined under the node ``design``.

.. option:: file

  Define the path to specific type of file

.. option:: type="<string>"

  Can be one of the following:

  - ``verilog``: Verilog file for the RTL design
  - ``system_verilog``: SystemVerilog file for the RTL design
  - ``blif``: BLIF file for the RTL design. This is considered to be the post-synthesis netlist

Cocotb Files
------------

Cocotb simulaton files can be defined under the node ``cocotb``.

.. option:: file

  Define the path to specific type of file

.. option:: type="<string>"

  Can be one of the following:

  - ``source``: python scripts required by the top-level testbench
  - ``top``: Top-level python cocotb testbench
  - ``makefile``: Makefile to run the cocotb testbench

Constraints
-----------

Design constraint files can be defined under the node ``constraints``.

.. option:: file

  Define the path to specific type of file

.. option:: type="<string>"

  Can be one of the following:

  - ``sdc``: VPR sdc file
  - ``pcf``: Pin constraint file for datapath signals
  - ``pcf_gclk``: Pin constraint file for global signals, such as clock and reset

