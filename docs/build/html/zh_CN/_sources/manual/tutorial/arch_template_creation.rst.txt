.. _tutorial_arch_template_creation:

Create an Arch Template
-----------------------

The architecture template contains a set of files that are required to 

- describe, model and customize the eFPGA architecture with various options
- conduct performance evaluation on eFPGA architecture
- generate gate-level netlists and perform QoR extraction
- implement physical designs

This is an All-in-One package when an eFPGA architecture is released
This section introduces the detailed content of the package
A live example can be found at ``etc/device/ALKDL``

Arch Description
````````````````

Architecture description files are required to model the eFPGA architecture.
Currently, we need two fabrics defined for each eFPGA architecture, ``dp`` for design planning and ``ultimate`` for actual fabric.
Some files are common between the fabrics while some are not.

.. list-table:: architecture description files
  :widths: 50 20 30
  :header-rows: 1

 * - File Type
   - Example
   - Notes
 * - VPR architecture description
   - vpr_arch.xml
   - Common
 * - OpenFPGA architecture description
   - openfpga_arch.xml
   - Common
 * - OpenFPGA global network description
   - openfpga_global_network.xml
   - Separated file
 * - architecture design variables
   - arch_var.yml
   - Separated files
 * - architecture timing files
   - arch_timing_tt_25C_v0p9.yml
   - Separated file for each corner

OpenFPGA Settings
`````````````````

The default setting files required to run various OpenFPGA flows.
The default setting files are designed to be general-purpose so that most of benchmarks can pass OpenFPGA flows without human effort.

.. list-table:: OpenFPGA setting files
  :widths: 70 30
  :header-rows: 1

  * - File Type
    - Example
  * - Default VPR SDC
    - vpr_dummy.sdc
  * - Default VPR place constraints
    - fix_pins_dummy.place
  * - Default Pin Constraints for global signals
    - pin_constraints_dummy.xml
  * - Default Pin Constraints for single-clock design
    - pcf_1clk_default.xml
  * - Default Pin Constraints for data signals
    - pcf_dummy.pcf
  * - Tile configuration
    - tile_config.xml
  * - Simulation settings
    - efpga_fix_sim_openfpga.xml

Note that the default setting files do not guarantee best QoR.
SDC or other design constraints are mostly required when 

- QoR is a concern 
- Benchmark have most than 1 clocks and resets
- Pin constraints are needed

OpenFPGA Shell Scripts
``````````````````````

The OpenFPGA shell scripts are the template scripts used to run various OpenFPGA flows. 
Typically, the files are kept under a subdirectory ``openfpga_shell_script``

.. list-table:: OpenFPGA setting files
  :widths: 70 30
  :header-rows: 1

  * - File example
    - Descriptin
  * - generate_bitstream.openfpga
    - Script to generate golden bitstream for a benchmark
  * - generate_base_bitstream.openfpga
    - Script to generate golden base bitstream file for an architecture
  * - generate_device_data.openfpga
    - Script to generate device data caches for an architecture
  * - generate_init_module_names.openfpga
    - Scripts to generate reference module names for an architecture
  * - generate_init_fabric_key.openfpga
    - Scripts to generate reference fabric key for an architecture
  * - generate_io_coordinate.openfpga
    - Scripts to generate I/O coordinates for an architecture
  * - generate_fabric.openfpga
    - Scripts to generate RTL netlists for an architecture
  * - generate_preconfig_testbench.openfpga
    - Scripts to generate preconfigured testbenches for a benchmark
  * - generate_full_testbench.openfpga
    - Scripts to generate full testbenches for a benchmark

Yosys Scripts
`````````````

Yosys scripts are the templates required to call yosys for specific purpose
The files are typically kept under the subdirectory ``yosys_script``

.. list-table:: OpenFPGA setting files
  :widths: 70 30
  :header-rows: 1

  * - File example
    - Descriptin
  * - synth.ys
    - Default script to perform synthesis on benchmarks
  * - sweep_k.ys
    - The script to perform LUT size sweeping on benchmarks, to find best LUT sizes


Custom Netlists
```````````````

The custom netlists include third-party RTL or gate-level netlists which are required by the eFPGA architecture.
They could be a component like, programmable flip-flop, DSP *etc.*

The third-party IPs are typically kept under the subdirectory ``ips``, as submodules
To seamlessly integrate the third-party IP into eFPGA, wrappers are required in some cases, which are typically kept under the subdirectory ``custom_modules``

.. note:: Symbolic links of the verilog models of standard cells are required for efpga_circuits.v to perform RTL simulation

.. list-table:: Custom module files
  :widths: 70 30
  :header-rows: 1

  * - File example
    - Descriptin
  * - efpga_ccff.v
    - Configuration Chain Flip-flops required by CCFF-based FPGA
  * - efpga_stdcell_wrapper.v
    - Wrappers for standard cells so that OpenFPGA architecture description can be independent from PDK
  * - efpga_circuits.v
    - A list of third-party files required to perform rtl-level simulation
  * - mmff_wrapper.v
    - Wrapper for multi-mode flip-flop IP. Only needed when the IP is used in the eFPGA architecture
  * - rf_pcounter_wrapper.v
    - Wrapper for programmable counter IP. Only needed when the IP is used in the eFPGA architecture

Under the ``netlist_wrapper`` subdirectory, some gate-level netlists are required by eFPGA top-level netlists

.. note:: The ``netlist_wrapper`` may not be needed in future as the flow is improved.

Netlist Makeup
``````````````

Netlist makeup is an optimization which is applied on the RTL netlists generated by OpenFPGA
This is an optional step which can skipped for some eFPGA architecture
The configuration files of netlist makeup are typically kept under ``netlist_makeup``

Netlist Synthesis
`````````````````

Fabric netlist synthesis recipes are different from one eFPGA architecture to another.
The configuration files are typically kept under the subdirectory ``synth``

.. list-table:: Custom module files
  :widths: 70 30
  :header-rows: 1

  * - File example
    - Description
  * - config/synth_strategies.xml
    - The default strategies to be applied for the eFPGA architecture
  * - sdc
    - Contain all the SDC files required by the default strategy file

QoR Extraction
``````````````

QoR extraction recipes are different from one eFPGA architecture to another.
The configuration files are typically kept under the subdirectory ``qor_signoff``

Flow Configuration
``````````````````

The common utility to enable ArkAngel flow is typically kept under the subdirectory ``flow_conf``

.. list-table:: Custom module files
  :widths: 70 30
  :header-rows: 1

  * - File example
    - Description
  * - efpga_arch_template.xml
    - The template file required to create any ArkAngel project
  * - log_error_keywords.xml
    - The keywords to detect Yosys and OpenFPGA log errors
  * - openfpga_log_keywords.xml
    - The keywords to extract performance metrics from OpenFPGA logs. These will be shown in architecture evaluation reports

