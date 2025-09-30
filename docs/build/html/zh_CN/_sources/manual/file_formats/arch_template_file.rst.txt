.. _file_format_arch_template_file:

Arch Template File (.xml)
=========================

The arch template file includes a list of files required to define an eFPGA fabric.
The files are the starting point for users to develop their eFPGA fabrics.
The arch template file is provided to import files when user selected a specific eFPGA architecture.

An example of file is shown as follows.

.. literalinclude:: example_arch_template.xml
  :language: xml

Reserved Words
--------------

The reserved words can be used in defining file paths

.. option:: ${PWD}

  The current working directory when running ArkAngel. This keyword will be replaced during runtime

.. option:: ${ROOT_PATH}

  The root path which starting ArkAngel

Synthesis Settings
------------------

Netlist synthesis settings can be defined under the node ``synth``.

For each PDK, dedicated synthesis settings can be defined under the node ``pdk``.
If user defines a PDK which is not supported here, custom synthesis settings will be required. User should provide through command-line options

.. option:: name="<string>"

  Specify the name of the PDK which can be found in the PDK configuration file. The dedicated synthesis settings can only be available when the name of PDK matches.

.. option:: sdc

  The root directory that contains all the SDC files required by netlist synthesis

.. option:: strategy

  The synthesis strategy file required to run netlist synthesis. See details in :ref:`file_format_synth_strategy_file`

.. option:: ccff_max_fanout

  The integer to specify the maximum number of fan-out which is allowed for configuration chain optimization

Floorplan Settings
------------------

eFPGA fabric floorplan settings can be defined under the node ``floorplan``.

For each PDK, dedicated floorplan settings can be defined under the node ``pdk``.
If user defines a PDK which is not supported here, custom floorplan settings will be required. User should provide through command-line options

.. option:: name="<string>"

  Specify the name of the PDK which can be found in the PDK configuration file. The dedicated floorplan settings can only be available when the name of PDK matches.

.. option:: strategy

  The floorplan strategy file required to run coarse flooplanning which will applied to physical design steps. See details in :ref:`file_format_floorplan_strategy_file`

Qorso Tasks
-----------

QoR Extraction settings can be defined under the node ``qorso``.
A number of QoR tasks can be defined under the node ``qorso``, each of which has dedicated settings

For each PDK, dedicated QoR tasks can be defined under the node ``pdk``.
If user defines a PDK which is not supported here, custom QoR tasks will be required. User should provide through command-line options

.. option:: <pdk name="<string>">

  Specify the name of the PDK which can be found in the PDK configuration file. The dedicated floorplan settings can only be available when the name of PDK matches.

.. option:: <task name="<string>">

  A unique name of the task

.. option:: type="<string>"

  The type of the task. Can be [ ``leakage`` | ``power`` | ``timing`` ]. Used to perform selective QoR extraction

.. option:: config

  The strategy file required to run the QoR task. See details in :ref:`file_format_qorso_strategy_file`

.. _file_format_arch_template_file_builtin_corner_map:

Built-in Corners
----------------

The built-in corners for each PDK can be defined under the node ``builtin_corner_map``.
For each PDK, a list of corners can be defined under the node ``pdk``.

.. option:: name="<string>"

  Specify the name of the PDK which can be found in the PDK configuration file. The built-in corners can only be available when the name of PDK matches.

.. option:: default="<string>"

  Default name of the corner to be considered when not specified by user during the development flow. For each PDK, a default corner can be specified

For each corner, the following attributes can be defined.

.. option:: name="<string>"

  The unique name of the corner. The corner-related timing files are under the node ``arch_timing`` of arch template (See details in :ref:`file_format_arch_template_file_arch_template`), which is only applicable to the ``ultimate`` fabric.

.. option:: sclib="<string>"

  The corner name of a standard cell library. See details in :ref:`file_format_pdk_file` 

.. option:: spef="<string>"

  The corner name to be used when naming SPEF files

.. _file_format_arch_template_file_arch_template:

Arch Templates
--------------

Architecture-level settings can be defined under the node ``arch_templates``.

.. option:: route_chan_width="<int>"

  The number of routing channel wires to be applied 

The configuration file required to parse QoR metrics from OpenFPGA logs are defined under the node ``openfpga_stats_conf_file``. See detailes in the :ref:`file_format_openfpga_stats_conf_file``.

The configuration file required to parse error from OpenFPGA logs are defined under the node ``openfpga_error_conf_file``. See detailes in the :ref:`file_format_log_check_conf_file``.

The configuration file required to parse error from Yosys logs are defined under the node ``yosys_error_conf_file``. See detailes in the :ref:`file_format_log_check_conf_file``.

The arch timing files are defined under the node ``arch_timing`` which only works for the ``ultimate`` fabric.

.. note:: The type of each arch timing file should matches the arch timing tag in the corner map (See details in :ref:`file_format_project_file_corner_map`)

The fabric ``dp`` for design planning is defined under the node ``dp``.
The fabric ``ultimate`` for actual eFPGA is defined under the node ``ultimate``.

.. option:: file

  Define the path to specific type of file

.. option:: type="<string>"

  Can be one of the following:

  - ``vpr_arch``: The VPR architecture description
  - ``openfpga_arch``: The OpenFPGA architecture description
  - ``openfpga_global_network_arch``: The OpenFPGA global signal network architecture description
  - ``openfpga_clock_buffer_location_map``: The OpenFPGA clock buffer location map 
  - ``design_variable``: The design variables which are applicable to the vpr architecture and openfpga architecture files

Arch Generator
--------------

Each architecture template requires a architecture generator whose binary exectuable should be specified

.. option:: file

  Define the path to binary of the architecture generator

.. option:: type="<string>"

  Specify the type of the binary executable. Valid type must be one of the types in the boot config file (See details in :ref:`file_format_boot_config_file_boot_type`)


Netlist Flags
-------------

Custom netlist flags can be defined under the node ``netlist_flags``.
All the flags will be applied during netlist generation.
The flags may be required from external IP files.

For each PDK, dedicated netlist flags can be defined under the node ``pdk``.
If user defines a PDK which is not supported here, netlist flags may be defined through project file

.. option:: name="<string>"

  Specify the name of the PDK which can be found in the PDK configuration file. The dedicated netlist flags can only be available when the name of PDK matches.

.. options:: flag

  Specify the value of the flag

.. option:: name="<string>"

  Specify the name of the flag

IP Files
--------

External IP files can be defined under the node ``ips``.

.. option:: file

  Define the path to specific type of file

.. option:: type="<string>"

  Can be one of the following:

  - ``ip_rtl``: RTL-level netlists which be optimized during netlist synthesis
  - ``ip_gl``: Gate-level netlists which should stay don't touch during netlist synthesis

.. option:: format="<string>"

  Can be one of the following:

  - ``verilog``: Verilog netlist. Support Verilog-1991, Verilog-2001 and Verilog-2005 standards
  - ``system_verilog``: System Verilog netlist.

  If not specified, all the IP files are inferred by their file names:

  - ``verilog``: file whose names end with ``.v`` or ``.v.gz`` 
  - ``system_verilog``: file whose names end with ``.sv`` or ``.sv.gz`` 

OpenFPGA Settings
-----------------

OpenFPGA setting files can be defined under the node ``openfpga_settings``.

.. option:: file

  Define the path to specific type of file

.. option:: type="<string>"

  Can be one of the following:

  - ``openfpga_sim_setting``: The openfpga simulation setting files
  - ``openfpga_bitstream_setting``: The openfpga bitstream setting files
  - ``tile_config``: The tile configuration file
  - ``gclk_pcf``: The default pin constraints file for global network. This is applied when the benchmark does not have any global signals, such as clock, reset, *etc*.
  - ``vpr_sdc``: The default SDC file for VPR. This is applied when the benchmark does not have one
  - ``pcf``: The default pin constraints file. This is applied when the benchmark does not have one

OpenFPGA Scripts
----------------

OpenFPGA shell scripts can be defined under the node ``openfpga_shell_scripts``. These are scripts that are applied during development steps.

.. option:: file

  Define the path to specific type of file

.. option:: type="<string>"

  Can be one of the following:

  - ``generate_bitstream``: Script to generate golden bitstream for a benchmark
  - ``generate_base_bitstream``: Script to generate golden base bitstream file for an architecture
  - ``generate_device_data``: Script to generate device data caches for an architecture
  - ``generate_init_module_names``: Scripts to generate reference module names for an architecture
  - ``generate_init_fabric_key``: Scripts to generate reference fabric key for an architecture
  - ``generate_io_coordinate``: Scripts to generate I/O coordinates for an architecture
  - ``generate_fabric``: Scripts to generate RTL netlists for an architecture
  - ``generate_preconfig_testbench``: Scripts to generate preconfigured testbenches for a benchmark
  - ``generate_full_testbench``: Scripts to generate full testbenches for a benchmark
    
Yosys Scripts
-------------

Yosys scripts can be defined under the node ``yosys_scripts``. These are scripts that are applied during development steps.

.. option:: file

  Define the path to specific type of file

.. option:: type="<string>"

  Can be one of the following:

  - ``synthesis``: Script to generate golden bitstream for a benchmark
  - ``sweep_k``: Script to sweep various number of LUT size for a pre-arch analysis

Netlist Makeup
--------------

Netlist makeup settings can be defined under the node ``netlist_makeup_key``

.. option:: root="<string>"

  Specify the root directory for netlist makeup scripts

For each PDK, dedicated netlist makeup configuration can be defined under the node ``pdk``.
If user defines a PDK which is not supported here, netlist flags may be defined through project file

.. option:: name="<string>"

  Specify the name of the PDK which can be found in the PDK configuration file. The dedicated netlist makeup configuration files can only be available when the name of PDK matches.

.. option:: ccff_makeup_buf_config="<string>"

 Specify the path to the buffer configuration file required for ccff makeup. This should be a relative path to the root path defined in this section

An example of file is shown as follows.

.. literalinclude:: example_ccff_makeup_buf_config.yaml
  :language: yaml
