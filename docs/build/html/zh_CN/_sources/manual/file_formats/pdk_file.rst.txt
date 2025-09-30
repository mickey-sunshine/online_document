.. _file_format_pdk_file:

PDK File (.xml)
===============

The PDK file aims to provide a standard way for users to define the required PDK files for eFPGA development
It is an interchangeable file between *Graphical User Interface* (GUI) and EDA engines.
Users can use GUI to generate a PDK file or write their own PDK file.
PDK files are loaded when creating or load a tapeout project (See details in :ref:`file_format_project_file`)

An example of file is shown as follows.

.. literalinclude:: example_pdk.xml
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


General
-------

For each pdk, these are the general syntax 

.. option:: name="<string>"

  A unique name of the PDK

.. option:: root

  Specify the root path of the PDK files

.. option:: shrink_factor=<float>

  Specify the shrink factor, which is the scaling factor applied on eFPGA layout against the area number provided by the standard cells. The number can be found in the datasheet provided by the PDK vendor. If not provided, assume the post shrink factor is 1, indicating no scaling will be applied.

.. note:: The shrink factor is applied to both height and width. For example, if a shrink factor of 0.9 is considered, the post-shrink layout will be 81% of the original one.

.. _file_format_pdk_file_stdcell:

Standard Cells
--------------

Standard cell library files can be defined under the node ``sclibs``.
Each type of standard cell library has a dedicated node ``sclib``.

.. option:: name="<string>"

  The unique name of the standard cell library. Used in the netlist synthesis, QoR extraction, *etc*.

.. option:: height="<float>"

  The height of the standard cells in the library. The number can be found in the datasheet provided by the standard cell vendor. For example, a 7t standard cell is different in height than a 9t standard cell. Default unit is micrometer (:math:`{\mu}m`). 

.. option:: cpp="<float>"

  The *Contact Poly Pitch* (CPP) of the standard cells in the library. The number can be found in the datasheet provided by the standard cell vendor. Note that standard cells in different channel length may differ in CPP. Default unit is micrometer (:math:`{\mu}m`). 

.. option:: file

  Define the path to specific type of file

.. option:: type="<string>"

  Can be one of the following:

  - ``lib``: Liberty file for timing models
  - ``gds``: Layout file in GDS format
  - ``cdl``: SPICE file in CDL format
  - ``lef``: Cell information
  - ``verilog``: Verilog netlists

.. option:: process="<string>"

  The process corner of the standard cell. Applicable to liberty files

.. option:: vdd="<string>"

  Nominal VDD of the standard cells. Applicable to liberty files

.. option:: temp="<string>"

  Operating temperature of the standar cell. Applicable to liberty files

.. option:: model="<string>" 

  Type of timing model used in the liberty file. Can be one of the following:

  - ``nldm``: The Non-Linear Delay Model
  - ``ccs``: Composite Current Source

Tech files
----------

Technology files can be defined under the node ``techfile``.

.. option:: file

  Define the path to specific type of file

.. option:: type="<string>"

  Can be one of the following:

  - ``tluplus``: TLU+ file
  - ``nxtgrd``: NXTGRD database for process RC characterization
  - ``empty_spice_subckt``: The empty spice models for GDS merge
  - ``innovus_lef``: The LEF file for innovus usage
  - ``redhawk_tech_file``: The tech file required for EM analysis
  - ``layer_map``: Metal layer map file required by physical design
  - ``gds_layer_map``: Metal layer map file required by physical design

.. option:: metal_stack="<string>"

  The metal stack associated to the tech file

.. option:: corner="<string>"

   RC corner associated to the tech file


