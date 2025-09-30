.. _arkangel_arch_dev_commands:

Arch Development Commands
-------------------------

create_arch
~~~~~~~~~~~

Create a new architecture as the starting point of architecture development. This is the first step for users to start with an architecture templates. Before running the ``setup_arch``, architecture configuration commands can be applied

.. option:: --run <string>

  Specify the run id. Each run is independent from each other. If not specified, a default name will be provided. 

  .. note:: If you specify an existing run, the data will be overwritten.

.. option:: --verbosity <int>

  Control the verbosity of the messages. For debugging usage, recommend to set to ``1``. By default, it is ``0``, leading to minimum logging messages.

.. _arkangel_arch_dev_commands_set_io_num:

set_io_num
~~~~~~~~~~

Specify the number of I/O, either input or output, on a given side of the eFPGA. 

.. note:: Due the architecture constraints, the actual number of I/O may be larger than the wanted. Use the command :ref:`arkangel_project_commands_report_io` to get the actual I/O arrangment

.. note:: This command cannot remove all the I/Os on a given side. Use command :ref:`arkangel_arch_dev_commands_remove_io`

.. option:: --run <string>

  Specify the run id. Each run is independent from each other. If not specified, a default name will be provided. 

  .. note:: If you specify an existing run, the data will be overwritten.

.. option:: --side <string>

  Specify the side where the I/O number constraints should be applied. Can be [ ``top`` | ``right`` | ``bottom`` | ``left`` ]

.. option:: --type <string>

  Specify the type of the I/Os where the I/O number constraints should be applied. Can be [ ``input`` | ``output`` ]

.. option:: --num <integer>

  Specify the number of I/Os on the selected side and type

.. option:: --verbosity <int>

  Control the verbosity of the messages. For debugging usage, recommend to set to ``1``. By default, it is ``0``, leading to minimum logging messages.

.. _arkangel_arch_dev_commands_remove_io:

remove_io
~~~~~~~~~

Remove all the I/Os in any available types on a given side of the eFPGA. 

.. option:: --run <string>

  Specify the run id. Each run is independent from each other. If not specified, a default name will be provided. 

  .. note:: If you specify an existing run, the data will be overwritten.

.. option:: --side <string>

  Specify the side where the I/O number constraints should be applied. Can be [ ``top`` | ``right`` | ``bottom`` | ``left`` ]

.. option:: --verbosity <int>

  Control the verbosity of the messages. For debugging usage, recommend to set to ``1``. By default, it is ``0``, leading to minimum logging messages.

set_core_dimension
~~~~~~~~~~~~~~~~~~

Specify the height and width of the core fabric on a given side of the eFPGA, excluding the I/O rows and columns

.. option:: --run <string>

  Specify the run id. Each run is independent from each other. If not specified, a default name will be provided. 

  .. note:: If you specify an existing run, the data will be overwritten.

.. option:: --height <int>

  Specify the number of rows in the core fabric, excluding I/Os

.. option:: --width <int>

  Specify the number of columns in the core fabric, excluding I/Os

.. option:: --verbosity <int>

  Control the verbosity of the messages. For debugging usage, recommend to set to ``1``. By default, it is ``0``, leading to minimum logging messages.

set_num_prog_clock
~~~~~~~~~~~~~~~~~~

Specify the number of programming clocks to be used in the eFPGA

.. option:: --run <string>

  Specify the run id. Each run is independent from each other. If not specified, a default name will be provided. 

  .. note:: If you specify an existing run, the data will be overwritten.

.. option:: --num <int>

  Specify the number of programming clocks in the core fabric

.. option:: --verbosity <int>

  Control the verbosity of the messages. For debugging usage, recommend to set to ``1``. By default, it is ``0``, leading to minimum logging messages.

set_num_config_region
~~~~~~~~~~~~~~~~~~~~~

Specify the number of configurable regions to be used in the eFPGA. The number of programming clocks will control a number of configurable regions. When the number of configurable regions is bigger than the number of programming clocks. Configurable regions will be evenly assigned to each programming clock

.. option:: --run <string>

  Specify the run id. Each run is independent from each other. If not specified, a default name will be provided. 

  .. note:: If you specify an existing run, the data will be overwritten.

.. option:: --num <int>

  Specify the number of configurable regions in the core fabric

.. option:: --verbosity <int>

  Control the verbosity of the messages. For debugging usage, recommend to set to ``1``. By default, it is ``0``, leading to minimum logging messages.


setup_arch
~~~~~~~~~~~

Setup a new architecture with detailed data modeling, being ready for downstream development.

.. option:: --run <string>

  Specify the run id. Each run is independent from each other. If not specified, a default name will be provided. 

  .. note:: If you specify an existing run, the data will be overwritten.

.. option:: --verbosity <int>

  Control the verbosity of the messages. For debugging usage, recommend to set to ``1``. By default, it is ``0``, leading to minimum logging messages.

show_arch
~~~~~~~~~

Show the details of a given aspect of an eFPGA architecture. Due to the large data, only the file location will be shown

.. option:: --type <string>

  Can be the following:
  
  - ``init_module_names`` : the initial names of each unique modules in the eFPGA architecture. This is the reference for users to customize module names
  - ``module_names``: check the final names for each unique modules in the eFPGA architecture
  - ``reference_fabric_key`` : the initial fabric key generated for the eFPGA architecture. This is the reference for users to customzie
  - ``crafted_fabric_key`` : the hand-crafted fabric key provided by user
  - ``fabric_key`` : the final fabric key file which is adapted from the hand-crafted fabric key, which will be applied to the eFPGA architecture
  - ``arch_floorplan`` : the illustrative figure showing an early-stage floorplanning for the eFPGA architecture. Detailed floorplanning is available after netlist development is completed

.. option:: --fabric <string>

  Specify the name of the eFPGA fabric, whose details will be shown. If not specified, the ``ultimate`` fabric will be considered. See details in :ref:`manual_project_tree_arch_workspace`` for defintion of fabrics.

.. option:: --run <string>

  Specify the run id. Each run is independent from each other. If not specified, a default name will be provided. 

  .. note:: If you specify an existing run, the data will be overwritten.

.. option:: --verbosity <int>

  Control the verbosity of the messages. For debugging usage, recommend to set to ``1``. By default, it is ``0``, leading to minimum logging messages.

set_arch
~~~~~~~~

 Add or update a customized file to the eFPGA architecture. The added file will be sanitized and applied to the architecture database.

.. option:: --type <string>

  Can be the following:
  
  - ``module_names``: check the final names for each unique modules in the eFPGA architecture
  - ``crafted_fabric_key`` : the hand-crafted fabric key provided by user
  - ``io_pin_table_naming_rules``: the naming rules for eFPGA I/O pins

.. option:: --fabric <string>

  Specify the name of the eFPGA fabric, whose details will be shown. If not specified, both ``dp`` and ``ultimate`` fabrics will be impacted. See details in :ref:`manual_project_tree_arch_workspace` for defintion of fabrics.

.. note:: When the type of ``io_pin_table_naming_rules``, user must specify the fabric name and ensure both ``dp`` and ``ultimate`` fabrics are covered.

.. option:: --run <string>

  Specify the run id. Each run is independent from each other. If not specified, a default name will be provided. 

  .. note:: If you specify an existing run, the data will be overwritten.

.. option:: --file <string>

  Specify the path to the handcrafted file. If not specifed, the default/reference file will be used. 

.. option:: --verbosity <int>

  Control the verbosity of the messages. For debugging usage, recommend to set to ``1``. By default, it is ``0``, leading to minimum logging messages.
