.. _file_format_project_file:

Project File (.xml)
===================

The project file aims to provide a standard way for users to create a project and include design files. 
It is an interchangeable file between *Graphical User Interface* (GUI) and EDA engines.
Users can use GUI to generate a project file or write their own project file.
EDA engine accepts only project files when create, load and save project-related information.

An example of file is shown as follows.

.. literalinclude:: example_project.xml
  :language: xml

Reserved Words
--------------

The reserved words can be used in defining file paths

.. option:: ${PWD}

  The current working directory when running ArkAngel. This keyword will be replaced during runtime

.. option:: ${ROOT_PATH}

  The root path which starting ArkAngel

General Syntax
--------------

.. option:: name="<string>"

  A unique name of the project, impacting the naming of files/directories in the assoicated workspace (See details in :ref:`manual_project_tree_overview`) 

.. option:: family="<string>"

  The family name of the architecture. This will impact the synthesis strategy, optimization strategies and EDA scripts during the EFPGA development

.. option:: path="<string>"

  Specify the root directory where the project directory will be created and runtime results will be placed.

  .. note:: Suggest to use the directory where the project file is placed!

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

PDK Configuration
-----------------

Specify the path to the PDK configuration file. See details in :ref:`file_format_pdk_file` 

Benchmark Sets
--------------

Specify the path to the benchmark configuration file. See details in :ref:`file_format_benchmark_file` 

.. note:: Multiple benchmark files can be defined.  

.. option:: default="<string>"

  The default benchmark to be applied when running benchmark-independent development process. Must be a valid name among the benchmarks. The selected benchmark must have a post-synthesis netlist

.. option:: disabled="<string>"

  Specify the list of benchmark names that should be disabled for architecture evaluation and design verification. Note that the benchmark names should be valid ones defined in the benchmark files.

.. note:: Use the syntax ``disabled`` in the project file results in the same impact as running command ``disable_benchmark`` (See details in :ref:`arkangel_project_commands_disable_benchmark`)

.. _file_format_project_file_corner_map:

Corner Map
----------

User-defined corners can be defined under the node ``corner_map``.

.. option:: default="<string>"

  Default name of the corner to be considered when not specified by user during the development flow. If not specified, the default corner will follow the default corner of built-in corners. See details in :ref:`file_format_arch_template_file_builtin_corner_map`

.. option:: name="<string>"

  The unique name of the corner. User can overwrite any built-in corner with the same name. 

.. option:: sclib="<string>"

  The corner name of a standard cell library. See details in :ref:`file_format_pdk_file` 

.. option:: spef="<string>"

  The corner name to be used when naming SPEF files

.. _file_format_project_file_arch_template:

Arch Template
-------------

Define the file path to the architecture template (See details in :ref:`file_format_arch_template_file`)

