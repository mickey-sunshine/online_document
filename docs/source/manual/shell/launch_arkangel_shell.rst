.. _launch_arkangel_shell:

Launch ArkAngel Shell
---------------------

ArkAngel employs a shell-like user interface, in order to integrate all the tools in a well-modularized way.
To launch ArkAngel shell, users can choose two modes ``interactive`` or ``script``.

.. option::	--interactive or -i

  Launch ArkAngel in interactive mode where users type-in command by command and get runtime results

.. option::	--file or -f

  Launch ArkAngel in script mode where users write commands in scripts and FPGA will execute them

.. option::	--batch_execution or -batch

  Execute ArkAngel script in batch mode. This option is only valid for script mode.

  - If in batch mode, ArkAngel will abort immediately when fatal errors occurred.
  - If not in batch mode, ArkAngel will enter interactive mode when fatal errors occurred.

.. option:: --root_path

  Specify the root path where ArkAngel is installed. This is required.

.. option:: --boot_config

  Specify the file path to the boot configuration for ArkAngel. This is required. See details in :ref:`file_format_boot_config_file`

.. option::	--version or -v

  Print version information of ArkAngel

.. option::	--help or -h
	
  Show the help desk

