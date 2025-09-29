.. _arkangel_project_commands:

Project Commands
----------------

create_tapeout
~~~~~~~~~~~~~~

Create a new project based on a configuration file.

.. note:: Only 1 project should be created or loaded in the session! Suggest to launch another ArkAngel session if you need to access another project!

.. option:: --config_file <string>

  Specify the project configuration file to be used. For details about a project file, please refer to :ref:`file_format_project_file`.

.. option:: --verbosity <int>

  Control the verbosity of the messages. For debugging usage, recommend to set to ``1``. By default, it is ``0``, leading to minimum logging messages.

load_tapeout
~~~~~~~~~~~~

Load an existing project based on a configuration file.

.. note:: Only 1 project should be created or loaded in the session! Suggest to launch another ArkAngel session if you need to access another project!

.. option:: --config_file <string>

  Specify the project configuration file to be used. For details about a project file, please refer to :ref:`file_format_project_file`.

.. option:: --no_validation

  Disable all the validation on existing result files.

.. warning:: This may cause errors or extra effort in debugging during your development!

.. option:: --verbosity <int>

  Control the verbosity of the messages. For debugging usage, recommend to set to ``1``. By default, it is ``0``, leading to minimum logging messages.

save_tapeout
~~~~~~~~~~~~

Save the current project to a configuration file. If the same configuration file is provided when create or load the project. The project configuration file will be overwritten.

.. option:: --config_file <string>

  Specify the project configuration file to be used. For details about a project file, please refer to :ref:`file_format_project_file`.

.. option:: --verbosity <int>

  Control the verbosity of the messages. For debugging usage, recommend to set to ``1``. By default, it is ``0``, leading to minimum logging messages.

show_status
~~~~~~~~~~~

Show the status of a given step in the development flow, including the status of substeps.

.. option:: --step <string> 

  Specify the step name

.. option:: --run <string>

  Specify the run id for the selected step. If not specified, consider the latest run.

.. option:: --verbosity <int>

  Control the verbosity of the messages. For debugging usage, recommend to set to ``1``. By default, it is ``0``, leading to minimum logging messages.

show_dashboard
~~~~~~~~~~~~~~

Show the dashboard of the development flow. Note that only the latest run of major steps are shown. For detailed status, please use the ``show_status`` command.

.. option:: --verbosity <int>

  Control the verbosity of the messages. For debugging usage, recommend to set to ``1``. By default, it is ``0``, leading to minimum logging messages.

report_corners
~~~~~~~~~~~~~~

Report all the available corners that are defined in the project

.. option:: --verbosity <int>

  Control the verbosity of the messages. For debugging usage, recommend to set to ``1``. By default, it is ``0``, leading to minimum logging messages.

.. _arkangel_project_commands_report_module_names:

report_module_names
~~~~~~~~~~~~~~~~~~~

Report all the module names for a selected architecture development flow. Require the final module names are committed and passed all the checks. 

.. option:: --run <string>

  Specify the run id for the selected step. If not specified, consider the latest run.

.. option:: --verbosity <int>

  Control the verbosity of the messages. For debugging usage, recommend to set to ``1``. By default, it is ``0``, leading to minimum logging messages.

.. _arkangel_project_commands_report_io:

report_io
~~~~~~~~~

Report all the available I/O of the eFPGA that are defined in the project

.. option:: --run <string>

  Specify the run id for the selected step. If not specified, consider the latest run.

.. option:: --verbosity <int>

  Control the verbosity of the messages. For debugging usage, recommend to set to ``1``. By default, it is ``0``, leading to minimum logging messages.

report_static_power
~~~~~~~~~~~~~~~~~~~

Report the static power of an eFPGA fabric under a specific netlist development and a selected corner

.. option:: --run <string>

  Specify the run id for the netlist development. If not specified, consider the latest run.

.. option:: --corner <string>

  Specify the corner name to be considered. If not specified, the default corner will be considered. Use the keyword ``all`` to sweep all the available corners. 

.. option:: --verbosity <int>

  Control the verbosity of the messages. For debugging usage, recommend to set to ``1``. By default, it is ``0``, leading to minimum logging messages.


report_config_power
~~~~~~~~~~~~~~~~~~~

Report the configuration power of an eFPGA fabric under a specific netlist development and a selected corner

.. option:: --run <string>

  Specify the run id for the netlist development. If not specified, consider the latest run.

.. option:: --corner <string>

  Specify the corner name to be considered. If not specified, the default corner will be considered. Use the keyword ``all`` to sweep all the available corners. 

.. option:: --verbosity <int>

  Control the verbosity of the messages. For debugging usage, recommend to set to ``1``. By default, it is ``0``, leading to minimum logging messages.


report_config_stats
~~~~~~~~~~~~~~~~~~~

Report the estimated configuration time and detailed bitstream sizes of an eFPGA fabric under a specific netlist development

.. option:: --run <string>

  Specify the run id for the netlist development. If not specified, consider the latest run.

.. option:: --pclk_freq <float>

  Specify the frequency of programming clock to be considered when estimating the configuration time. 

.. option:: --verbosity <int>

  Control the verbosity of the messages. For debugging usage, recommend to set to ``1``. By default, it is ``0``, leading to minimum logging messages.

report_qor_scale
~~~~~~~~~~~~~~~~

Report the qor scale factors of an eFPGA fabric under a specific netlist development and a selected corner

.. option:: --run <string>

  Specify the run id for the netlist development. If not specified, consider the latest run.

.. option:: --corner <string>

  Specify the corner name to be considered. If not specified, the default corner will be considered. Use the keyword ``all`` to sweep all the available corners. 

.. option:: --type <string>

  Specify the type of the qor scale factors to be extracted. Can be [ ``timing`` | ``leakage`` | ``power`` ]. If not specified, the default type ``timing`` will be considered.

.. option:: --file <string>

  Specify the output file name for the generated qor scale report. If not specified, qor scale factors will be printed on screen.

.. option:: --precision <int>

  Specify the precision of the qor scale factors. If not specified, a default precision of ``2`` is used to round scale factor values.

.. option:: --verbosity <int>

  Control the verbosity of the messages. For debugging usage, recommend to set to ``1``. By default, it is ``0``, leading to minimum logging messages.

export_netlist
~~~~~~~~~~~~~~

Export gate-level netlists and *Quality-of-Results* (QoR) reports in a package for external use.

.. note:: Must have a successful run on netlist development!

.. option:: --file <string>

  Specify the file path where the netlist package will be written to. Must end with ``.tar.gz``

.. option:: --run <string>

  Specify the run id for the netlist development. If not specified, consider the latest run.

.. option:: --force_overwrite

  Force to overwrite existing package if possible. Ensure to save your existing packages before enable this option. By default, it is off.

.. option:: --reduce_error_to_warning

  Reduce error to warning. When enabled, the output netlists may not be correct. Be cautious when enable the option!

.. option:: --verbosity <int>

  Control the verbosity of the messages. For debugging usage, recommend to set to ``1``. By default, it is ``0``, leading to minimum logging messages.

export_arch
~~~~~~~~~~~

Export architecture data in a package for external use.

.. note:: Must have a successful run on architecture development!

.. option:: --file <string>

  Specify the file path where the arch package will be written to. Must end with ``.tar.gz``

.. option:: --run <string>

  Specify the run id for the architecture development. If not specified, consider the latest run.

.. option:: --force_overwrite

  Force to overwrite existing package if possible. Ensure to save your existing packages before enable this option. By default, it is off.

.. option:: --verbosity <int>

  Control the verbosity of the messages. For debugging usage, recommend to set to ``1``. By default, it is ``0``, leading to minimum logging messages.

backannotate
~~~~~~~~~~~~

Back-annotate the post-synthesis QoR results to FPGA architecture. Once the back-annotation is done, the architecture development flow should be re-run to initialize the database and evaluation flow should be re-run to compare the difference before and after back-annotation

.. option:: --run <string>

  Specify the run id for the netlist development. If not specified, consider the latest run.

.. option:: --corner <string>

  Specify the corner name to be considered. If not specified, the default corner will be considered. Use the keyword ``all`` to sweep all the available corners. 

.. option:: --verbosity <int>

  Control the verbosity of the messages. For debugging usage, recommend to set to ``1``. By default, it is ``0``, leading to minimum logging messages.

analyze_qor
~~~~~~~~~~~

Analyze the Fmax from bitstream generation reports and generate a summary for all the benchmarks

.. option:: --run <string>

  Specify the run id for the netlist development. If not specified, consider the latest run.

.. option:: --corner <string>

  Specify the corner name to be considered. If not specified, the default corner will be considered. Use the keyword ``all`` to sweep all the available corners. 

.. option:: --verbosity <int>

  Control the verbosity of the messages. For debugging usage, recommend to set to ``1``. By default, it is ``0``, leading to minimum logging messages.


.. _arkangel_project_commands_disable_benchmark:

disable_benchmark
~~~~~~~~~~~~~~~~~

Disable a selected benchmark during pre-arch analyses, architecture evaluation and design verification.

.. option:: --name <string>

  Specify the name of the benchmark to be disabled during pre-arch analyses, architecture evaluation and design verification.

.. option:: --verbosity <int>

  Control the verbosity of the messages. For debugging usage, recommend to set to ``1``. By default, it is ``0``, leading to minimum logging messages.

