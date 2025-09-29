.. _file_format_openfpga_stats_conf_file:

Stats Config File (.xml)
========================

The stats config file contains the key metrics which should be extracted from OpenFPGA/VTR log files.
The file is loaded when creating or load a tapeout project (See details in :ref:`file_format_project_file`)

An example of file is shown as follows.

.. literalinclude:: example_openfpga_stats_conf.xml
  :language: xml

Keyword
-------

A number of keywords can be defined the root node, each of which represents a key metric and the regular exprerssion to extract it from log files.

.. option:: name

  The unique name which represents the key metic. This is the name to be shown in any ArkAngel QoR report

.. option:: type="<string>"
  
  Denote the type of data which will be extracted from log. Can be one of the following:

  - ``int``: integer.
  - ``float``: Float number.
  - ``scientific``: Scientific number. For example, ``1.2n`` which is ``1.2e-9``

.. option:: regex="<string>"

  The regular expression to extract the data from any line of a log file. For scientific number, two matching cases must be defined. Otherwise, only expect 1 matching case. 

