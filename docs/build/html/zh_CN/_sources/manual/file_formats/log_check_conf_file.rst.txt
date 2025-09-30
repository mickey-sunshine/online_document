.. _file_format_log_check_conf_file:

Log Check Config File (.xml)
============================

The log check config file contains the patterns which should be judged as error messages from OpenFPGA/VTR/Yosys log files.
The file is loaded when creating or load a tapeout project (See details in :ref:`file_format_project_file`)

An example of file is shown as follows.

.. literalinclude:: example_log_check_conf.xml
  :language: xml

Keyword
-------

A number of keywords can be defined the root node, each of which represents a key metric and the regular exprerssion to extract it from log files.

.. option:: name

  The unique name which represents the key metic. This is the name to be shown in any ArkAngel QoR report

.. option:: ignore_case="<bool>"

  Define if the regular expression should be case sensitive or not.

.. option:: regex="<string>"

  The regular expression to extract the data from any line of a log file. The regular expression should follow the syntax of >C++17 std::regex.

