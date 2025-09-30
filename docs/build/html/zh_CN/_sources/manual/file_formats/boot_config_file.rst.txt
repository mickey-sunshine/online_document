.. _file_format_boot_config_file:

Boot Config File (.xml)
=======================

The boot configuration file contains the path to third-party tools which ArkAngel relies on.
The file unlock possibilities for ArkAngel to interface various version of third-party tools.
Also the file is used to adapt ArkAngel for diverse deployment conditions.

An example of file is shown as follows.

.. literalinclude:: example_boot_config.xml
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

.. _file_format_boot_config_file_boot_type:

Boot Type
---------

The boot type is specified under the node ``boot_type``.
There are two types:

- ``build``: The binaries are organized based on source code compilation
- ``install``: The binaries are organized based on an installer

Binary Paths
------------

Binary path for each third-party tool can be defined under the node ``bin_relpaths``.

.. option:: file

  Define the path to specific type of file

.. option:: type="<string>"

  Can be one of the following:

  - ``openfpga``: The binary of OpenFPGA
  - ``fabric_key_assistant``: The binary of fabric key assistant, part of the OpenFPGA project
  - ``pin_table_generator``: The python script of pin table generator, using during architecture development
  - ``netlist_makeup``: The python script of netlist makeup, used during netlist development
  - ``ccff_makeup``: The python script of configuration-chain makeup, used during netlist development
  - ``netlist_synthesis``: The python script of fabric netlist synthesis, used during netlist development
  - ``frontend``: The binary of ArkAngel frontend
  - ``qorso``: The python script of Quality-of-Result Sign-off 
  - ``bus_group_generator``: The python script to generate bus group file
  - ``cocotb_util``: The python script to run cocotb tasks
  - ``cocotb_force_bitstream``: The python script to force bitstream for cocotb
  - ``cocotb_makefile_inc``: The makefile header to enable cocotb simulation
