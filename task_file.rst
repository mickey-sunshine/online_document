.. _file_format_task_file:

Task File (.yaml)
=================

- The task file aims to provide a standard way for users to create a DC task run. 
- The task file is the key input file for users to craft, before running a DC task.
- The task file contains essential information required to set up DC scripts.

An example of file designed for synthesis tasks is shown as follows.

.. literalinclude:: example_dc_task.yaml
  :language: yaml


Technology-related Syntax
-------------------------

Technology-related information should be defined under the ``technology`` section

.. note:: The technology can be overwritten by the custom PDK file. See details in (:ref:`user_interface`). The corner selection will not be impacted 

.. option:: name="<string>"

  A unique name of the technology. Available technologies are ``s40ulp`` and ``t22ulp``

.. option:: root="<string>"

  Define the root directory of a PDK. Suggest to use absolute path when running a local test. 

.. option:: corner="<string>"

  Specify the corner to be considered for process variations. Can be 

  - ``tt``: typical-typical
  - ``tt_v1p0``: typical-typical, under Vdd=1.0V, only available for S40
  - ``tt_v1p1``: typical-typical, under Vdd=1.1V, only available for S40
  - ``tt85c``: typical-typical corner at the highest temperature required by commercial standard
  - ``bc``: best case
  - ``wc``: worst case

  .. note:: The corner names are pre-defined. It is different from the given names in PDKs. If you are not clear, please ask your manager.

Netlist-related Syntax
----------------------

Netlist-related information should be defined under the ``netlist`` section
The netlists are modeling the eFPGA fabric that are going to be analyzed

.. option:: input="<string>"

  Define the root directory of input (pre-synthesis) netlists where all the netlists (``.v`` or ``.v.gz``) are placed. Suggest to use absolute path when running a local test. 

.. option:: system_verilog_filter="<string>"

.. note:: This is optional

  By default, input files whose names end with ``sv`` will be recognized as system verilog netlists. Additional options will be appeneded to the auto-generated tcl scripts. This option provides an alternative for the input files which should be identified as system verilog netlists despite their file names. For example,

.. code-block:: yaml 

  netlist:
    input: "./release/"
    system_verilog_filter:
      - "pcounter_breg.v"
    exclude:
      - "counter_top.v"
    output: "./post_synth_netlist"

If you prefer all the netlists to be treated as system verilog, wildcard string is supported

.. code-block:: yaml 

  # All the verilog input netlists will be treated as system verilog
  netlist:
    input: "./release/"
    system_verilog_filter:
      - "*.v"
    exclude:
      - "counter_top.v"
    output: "./post_synth_netlist"

.. option:: exclude="<string>"

.. note:: This is optional

  Define the list of netlist files which should **NOT** be included when synthesis. For example, some netlists which are designed for simulation only, e.g., only include other netlists, are suggested to be excluded.

.. option:: link_path="<string>"

.. note:: This is optional when you are synthesizing RTL-level netlists

  Define the list of database files which are required to be linked before synthesis. For example, some IPs are treated as blackboxes during synthesis, which do require a timing library (.db) to be linked.

.. option:: output="<string>"

  Define the root directory of output (post-synthesis) netlists where all the netlists (``.v`` or ``.v.gz``) are placed. Suggest to use absolute path when running a local test. 

Synthesis Tasks
---------------

Report-area tasks should be defined under the ``report_area`` section.
Each task should constain the following information.

.. option:: name="<string>"

  Specify the unique name for this synthesis task. A synthesis task can be considered as a unique synthesis recipe, that are applicable to a number of designs (see definition in ``current_design``). The name and current design name will be used to create runtime directory.

.. option:: current_design="<string>"

  Specify the list of design names which the synthesis task should consider. All the designs under the same task will share the same synthesis receipe.

.. option:: compile="<string>"

  Specify options when compile the design using DC

  .. note:: When not specified, this is an analyze flow!

.. option:: type="<string>"

  Can be [ultra|regular]. Define the compilation command to be used when running synthesis. ``Ultra`` indicates to use the ``compile_ultra`` command, while ``regular`` indicates to use the widely used ``compile``.

.. option:: optimize="<string>"

  Can be [area|timing|power|balanced]. Define the optimization objective when compile the design. Only applicable when regular compilation type is applied.

.. option:: effort="<string>"

  Can be [high|low]. Define the level of optimization effort to be applied. Only applicable when optimization objective is specified. 

.. option:: target_library="<string>"

  Specify the target library when optimization should utilize. The applicable library name depends on the technology node. Only a tag is required. For example, ``lvt``.

.. option:: sdc: 

  Specify a list of SDC files that the report timing task should consider
  Currently, we support files whose names end with ``.tcl`` or ``.sdc``.
  For example,

.. code-block:: yaml
  
  sdc:
    - sdc/user_case1.sdc
    - sdc/user_case2.sdc
    - sdc/user_case3.tcl

.. option:: save_session="<string>"

  When defined, the synthesis flow will be saved to a disk as a session. Easy for user to quickly reload and continue analysis. Session name can be customized through the string. For example,

.. option:: remove_time_stamp="<bool>"

  Specify if the time stamp in the synthesized netlists and report files will be removed or not. By default, it is removed.

.. option:: name_rule="<bool>"

  Specify if the simple name rule should be applied in the synthesized netlists. By default, it is applied. When enable, special characters will not be used in any names of nets and modules, to comply with Verilog syntax.

.. code-block:: yaml

  save_session: my_session

.. option:: report_area="<string>"

  Specify if area report should be generated by the end of the synthesis task.

.. option:: report_timing="<string>"

  Specify if timing report should be generated by the end of the synthesis task

.. option:: report_power="<string>"

  Specify if power report should be generated by the end of the synthesis task

.. option:: file="<string>"

  .. note:: Applicable to ``report_area``, ``report_timing`` and ``report_power``

  Specify the path to output report file

  .. note:: Use keyword ``[current_design]`` in the path to customize the report file name. For example, when applied to ``current_design=tileA", ``./report/[current_design]_area.rpt" will be converted to ``./report/tileA_area.rpt"

.. option:: hierarchy="<string>"

  .. note:: Only applicable to ``report_power``

  Specify if the power report should include block-level details, i.e., breakdown.
