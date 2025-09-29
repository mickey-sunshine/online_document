.. _tutorial_pdk_import:

Import a PDK
------------

ArkAngel require a number of PDK files when building an eFPGA IP.
Therefore, the required PDK files are registered through a PDK configuration file (See details in :ref:`file_format_pdk_file`)
Even though that ArkAngel has provided examples of PDK configuration files, the way to install any PDK may be different for each user.
This tutorial helps users, who cannot use existing examples, create their PDK configuration file with detailed steps
In this tutorial, a 40nm PDK is considered as an example

Basic Info
``````````

Choose a prefer location in project directory and create a new XML file, e.g., ``my_pdk/pdk_config.xml``
This file will the pdk configuration file used in your tapeout project.

- Give a meaningful name to the PDK, e.g., ``name="s40ulp``, which denotes SMIC 40nm Ultra-Low-Power
- Fill the author information and time stamps. These are for your own records. No rules and sanity checks are applied.
- Specify the root directory where your PDK is installed. The root directory is used to search all the PDK files in later step. Recommand to use an absolute path.

By the end of the step, your XML file may look like

.. code-block:: xml

  <pdk name="s40ulp">
    <stamp>
      <author>RapidFlex</author>
      <dates>
        <created>Sat Dec 31 03:14:41 PM PST 2024</created>
        <last_modified>Sat Dec 31 03:14:41 PM PST 2024</last_modified>
      </dates>
      <tool_version>0.0.15-dev+023fa82</tool_version>
    </stamp>
    <root>/eda/pdk/s40/s40ulp</root>
  </pdk>

Std Cells
`````````

Standard cells are mostly used during netlist optimization.
Recommend to register all the standard cells which your consider to be used in the eFPGA layout, in order to open up the design space in optimization
You can select the preferred standard cells in ArkAngel when applying netlist optimization.

For each standard cell library, an unique name should be given.
The unique name will be used by applying netlist synthesis strategy (see details in :ref:`file_format_synth_strategy_file`) 
Recommend to name with technical features, such as ``uhdc40_rvt_v0.2``, where ``uhdc40`` represents *Ultra-High-Density 40nm*, ``rvt`` stands for *Regular Voltage Threshold* and ``v0.2`` is the version number.

For each standard cell library, the following types of files should be registered

- liberty timing files. For each *Process-Voltage-Temperature* (PVT) corner, the path to a liberty timing file should be provided. Used mainly by netlist optimization and physical design flows.
- gds file, which contains the GDS layouts corresponding to the standard cells. Used mainly by physical design flow
- cdl file, which contains the SPICE netlists corresponding to the standard cells. Used mainly by physical design flow
- lef file, which contains the LEF information corresponding to the standard cells. Used mainly by physical design flow
- verilog file, which contains behavorial models corresponding to the standard cells. Used mainly by design verification flows

.. note:: The file paths are always based on the root path. There is no need to assign absolute paths

These files should be easily found in your PDK. If not, please contact your PDK vendor.

.. note:: For evaluation without physical design, the liberty time files and verilog files areq required.

By the end of the step, your XML file may look like (In this example, there are 3 standard cell libraries defined)

.. code-block:: xml

  <pdk name="s40ulp">
    <stamp>
      <author>RapidFlex</author>
      <dates>
        <created>Sat Dec 31 03:14:41 PM PST 2024</created>
        <last_modified>Sat Dec 31 03:14:41 PM PST 2024</last_modified>
      </dates>
      <tool_version>0.0.15-dev+023fa82</tool_version>
    </stamp>
    <root>/eda/pdk/s40/s40ulp</root>
    <sclibs>
      <sclib name="uhdc40_hvt_v0.2">
        <file tag="tt" type="lib" process="tt" vdd="0.9" temp="25" model="nldm">std_cell/SCC40ULP_UHDC40_HVT/V0p2/liberty/0.9v/scc40ulp_uhdc40_hvt_tt_v0p9_25c_basic.db</file>
        <file tag="ffg" type="lib" process="ffg" vdd="0.99" temp="125" model="nldm">std_cell/SCC40ULP_UHDC40_HVT/V0p2/liberty/0.99v/scc40ulp_uhdc40_hvt_ffg_v0p99_125c_basic.db</file>
        <file tag="ffg_ccs" type="lib" process="ffg" vdd="0.99" temp="125" model="ccs">std_cell/SCC40ULP_UHDC40_HVT/V0p2/liberty/0.99v/scc40ulp_uhdc40_hvt_ffg_v0p99_125c_ccs.db</file>
        <file tag="tt_v1p0" type="lib" process="tt" vdd="1.0" temp="25" model="nldm">std_cell/SCC40ULP_UHDC40_HVT/V0p2/liberty/1.0v/scc40ulp_uhdc40_hvt_tt_v1p0_25c_basic.db</file>
        <file tag="tt_v1p1" type="lib" process="tt" vdd="1.1" temp="25" model="nldm">std_cell/SCC40ULP_UHDC40_HVT/V0p2/liberty/1.1v/scc40ulp_uhdc40_hvt_tt_v1p1_25c_basic.db</file>
        <file type="gds">std_cell/SCC40ULP_UHDC40_HVT/V0p2/gds/scc40ulp_uhdc40_hvt.gds</file>
        <file type="cdl">std_cell/SCC40ULP_UHDC40_HVT/V0p2/cdl/scc40ulp_uhdc40_hvt.cdl</file>
        <file type="lef">std_cell/SCC40ULP_UHDC40_HVT/V0p2/lef/scc40ulp_uhdc40_hvt.lef</file>
        <file type="verilog">std_cell/SCC40ULP_UHDC40_HVT/V0p2/verilog/scc40ulp_uhdc40_hvt.v</file>
      </sclib>
      <sclib name="uhdc40_lvt_v0.2">
        <file tag="tt" type="lib" process="tt" vdd="0.9" temp="25" model="nldm">std_cell/SCC40ULP_UHDC40_LVT/V0p2/liberty/0.9v/scc40ulp_uhdc40_lvt_tt_v0p9_25c_basic.db</file>
        <file tag="tt_v1p0" type="lib" process="tt" vdd="1.0" temp="25" model="nldm">std_cell/SCC40ULP_UHDC40_LVT/V0p2/liberty/1.0v/scc40ulp_uhdc40_lvt_tt_v1p0_25c_basic.db</file>
        <file tag="tt_v1p1" type="lib" process="tt" vdd="1.1" temp="25" model="nldm">std_cell/SCC40ULP_UHDC40_LVT/V0p2/liberty/1.1v/scc40ulp_uhdc40_lvt_tt_v1p1_25c_basic.db</file>
        <file type="gds">std_cell/SCC40ULP_UHDC40_LVT/V0p2/gds/scc40ulp_uhdc40_lvt.gds</file>
        <file type="cdl">std_cell/SCC40ULP_UHDC40_LVT/V0p2/cdl/scc40ulp_uhdc40_lvt.cdl</file>
        <file type="lef">std_cell/SCC40ULP_UHDC40_LVT/V0p2/lef/scc40ulp_uhdc40_lvt.lef</file>
        <file type="verilog">std_cell/SCC40ULP_UHDC40_LVT/V0p2/verilog/scc40ulp_uhdc40_lvt.v</file>
      </sclib>
      <sclib name="uhdc40_rvt_v0.2">
        <file tag="tt" type="lib" process="tt" vdd="0.9" temp="25" model="nldm">std_cell/SCC40ULP_UHDC40_RVT_V0p2/liberty/0.9v/scc40ulp_uhdc40_rvt_tt_v0p9_25c_basic.db</file>
        <file tag="ffg" type="lib" process="ffg" vdd="0.99" temp="125" model="nldm">std_cell/SCC40ULP_UHDC40_RVT_V0p2/liberty/0.99v/scc40ulp_uhdc40_rvt_ffg_v0p99_125c_basic.db</file>
        <file tag="ffg_ccs" type="lib" process="ffg" vdd="0.99" temp="125" model="ccs">std_cell/SCC40ULP_UHDC40_RVT_V0p2/liberty/0.99v/scc40ulp_uhdc40_rvt_ffg_v0p99_125c_ccs.db</file>
        <file tag="tt_v1p0" type="lib" process="tt" vdd="1.0" temp="25" model="nldm">std_cell/SCC40ULP_UHDC40_RVT_V0p2/liberty/1.0v/scc40ulp_uhdc40_rvt_tt_v1p0_25c_basic.db</file>
        <file tag="tt_v1p1" type="lib" process="tt" vdd="1.1" temp="25" model="nldm">std_cell/SCC40ULP_UHDC40_RVT_V0p2/liberty/1.1v/scc40ulp_uhdc40_rvt_tt_v1p1_25c_basic.db</file>
        <file type="gds">std_cell/SCC40ULP_UHDC40_RVT_V0p2/gds/scc40ulp_uhdc40_rvt.gds</file>
        <file type="cdl">std_cell/SCC40ULP_UHDC40_RVT_V0p2/cdl/scc40ulp_uhdc40_rvt.cdl</file>
        <file type="lef">std_cell/SCC40ULP_UHDC40_RVT_V0p2/lef/scc40ulp_uhdc40_rvt.lef</file>
        <file type="verilog">std_cell/SCC40ULP_UHDC40_RVT_V0p2/verilog/scc40ulp_uhdc40_rvt.v</file>
      </sclib>
    </sclibs>
  </pdk>

Tech Files
``````````

.. warning:: You may set dummy files in the section if physical design flow will not be executed

The technology files are required by physical design flows. For those who perform evaluation, these files are not required

There are the following types of files

- TLU+ files for the selected metal stack and corner. For multi-corner analysis, all the selected corners should be defined. Used by physical design flow
- NXTGRD files for the selected metal stack and corner. For multi-corner analysis, all the selected corners should be defined. Used by sign-off flow
- Empty SPICE sub-circuit neltist, which is used by sign-off flow for *Logic Versus Schematic* (LVS)
- LEF file for metal layers, which is required by physical design flow. The selected metal stack should be defined.
- The tech file required by Synopsys RedHawk for EM analysis. The selected metal stack and corner should be defined
- The metal layer map file required by physical design flow
- The GDS layer map file which is built for Synopsys ICC2

By the end of the step, your XML file may look like (In this example, there are 3 standard cell libraries defined)

.. code-block:: xml

  <pdk name="s40ulp">
    <stamp>
      <author>RapidFlex</author>
      <dates>
        <created>Sat Dec 31 03:14:41 PM PST 2024</created>
        <last_modified>Sat Dec 31 03:14:41 PM PST 2024</last_modified>
      </dates>
      <tool_version>0.0.15-dev+023fa82</tool_version>
    </stamp>
    <root>/eda/pdk/s40/s40ulp</root>
    <sclibs>
      <sclib name="uhdc40_hvt_v0.2">
        <file tag="tt" type="lib" process="tt" vdd="0.9" temp="25" model="nldm">std_cell/SCC40ULP_UHDC40_HVT/V0p2/liberty/0.9v/scc40ulp_uhdc40_hvt_tt_v0p9_25c_basic.db</file>
        <file tag="ffg" type="lib" process="ffg" vdd="0.99" temp="125" model="nldm">std_cell/SCC40ULP_UHDC40_HVT/V0p2/liberty/0.99v/scc40ulp_uhdc40_hvt_ffg_v0p99_125c_basic.db</file>
        <file tag="ffg_ccs" type="lib" process="ffg" vdd="0.99" temp="125" model="ccs">std_cell/SCC40ULP_UHDC40_HVT/V0p2/liberty/0.99v/scc40ulp_uhdc40_hvt_ffg_v0p99_125c_ccs.db</file>
        <file tag="tt_v1p0" type="lib" process="tt" vdd="1.0" temp="25" model="nldm">std_cell/SCC40ULP_UHDC40_HVT/V0p2/liberty/1.0v/scc40ulp_uhdc40_hvt_tt_v1p0_25c_basic.db</file>
        <file tag="tt_v1p1" type="lib" process="tt" vdd="1.1" temp="25" model="nldm">std_cell/SCC40ULP_UHDC40_HVT/V0p2/liberty/1.1v/scc40ulp_uhdc40_hvt_tt_v1p1_25c_basic.db</file>
        <file type="gds">std_cell/SCC40ULP_UHDC40_HVT/V0p2/gds/scc40ulp_uhdc40_hvt.gds</file>
        <file type="cdl">std_cell/SCC40ULP_UHDC40_HVT/V0p2/cdl/scc40ulp_uhdc40_hvt.cdl</file>
        <file type="lef">std_cell/SCC40ULP_UHDC40_HVT/V0p2/lef/scc40ulp_uhdc40_hvt.lef</file>
        <file type="verilog">std_cell/SCC40ULP_UHDC40_HVT/V0p2/verilog/scc40ulp_uhdc40_hvt.v</file>
      </sclib>
      <sclib name="uhdc40_lvt_v0.2">
        <file tag="tt" type="lib" process="tt" vdd="0.9" temp="25" model="nldm">std_cell/SCC40ULP_UHDC40_LVT/V0p2/liberty/0.9v/scc40ulp_uhdc40_lvt_tt_v0p9_25c_basic.db</file>
        <file tag="tt_v1p0" type="lib" process="tt" vdd="1.0" temp="25" model="nldm">std_cell/SCC40ULP_UHDC40_LVT/V0p2/liberty/1.0v/scc40ulp_uhdc40_lvt_tt_v1p0_25c_basic.db</file>
        <file tag="tt_v1p1" type="lib" process="tt" vdd="1.1" temp="25" model="nldm">std_cell/SCC40ULP_UHDC40_LVT/V0p2/liberty/1.1v/scc40ulp_uhdc40_lvt_tt_v1p1_25c_basic.db</file>
        <file type="gds">std_cell/SCC40ULP_UHDC40_LVT/V0p2/gds/scc40ulp_uhdc40_lvt.gds</file>
        <file type="cdl">std_cell/SCC40ULP_UHDC40_LVT/V0p2/cdl/scc40ulp_uhdc40_lvt.cdl</file>
        <file type="lef">std_cell/SCC40ULP_UHDC40_LVT/V0p2/lef/scc40ulp_uhdc40_lvt.lef</file>
        <file type="verilog">std_cell/SCC40ULP_UHDC40_LVT/V0p2/verilog/scc40ulp_uhdc40_lvt.v</file>
      </sclib>
      <sclib name="uhdc40_rvt_v0.2">
        <file tag="tt" type="lib" process="tt" vdd="0.9" temp="25" model="nldm">std_cell/SCC40ULP_UHDC40_RVT_V0p2/liberty/0.9v/scc40ulp_uhdc40_rvt_tt_v0p9_25c_basic.db</file>
        <file tag="ffg" type="lib" process="ffg" vdd="0.99" temp="125" model="nldm">std_cell/SCC40ULP_UHDC40_RVT_V0p2/liberty/0.99v/scc40ulp_uhdc40_rvt_ffg_v0p99_125c_basic.db</file>
        <file tag="ffg_ccs" type="lib" process="ffg" vdd="0.99" temp="125" model="ccs">std_cell/SCC40ULP_UHDC40_RVT_V0p2/liberty/0.99v/scc40ulp_uhdc40_rvt_ffg_v0p99_125c_ccs.db</file>
        <file tag="tt_v1p0" type="lib" process="tt" vdd="1.0" temp="25" model="nldm">std_cell/SCC40ULP_UHDC40_RVT_V0p2/liberty/1.0v/scc40ulp_uhdc40_rvt_tt_v1p0_25c_basic.db</file>
        <file tag="tt_v1p1" type="lib" process="tt" vdd="1.1" temp="25" model="nldm">std_cell/SCC40ULP_UHDC40_RVT_V0p2/liberty/1.1v/scc40ulp_uhdc40_rvt_tt_v1p1_25c_basic.db</file>
        <file type="gds">std_cell/SCC40ULP_UHDC40_RVT_V0p2/gds/scc40ulp_uhdc40_rvt.gds</file>
        <file type="cdl">std_cell/SCC40ULP_UHDC40_RVT_V0p2/cdl/scc40ulp_uhdc40_rvt.cdl</file>
        <file type="lef">std_cell/SCC40ULP_UHDC40_RVT_V0p2/lef/scc40ulp_uhdc40_rvt.lef</file>
        <file type="verilog">std_cell/SCC40ULP_UHDC40_RVT_V0p2/verilog/scc40ulp_uhdc40_rvt.v</file>
      </sclib>
    </sclibs>
    <techfile>
      <!-- TLU+ file require metal stack and corner -->
      <file type="tluplus" metal_stack="1p7m_6ic" corner="typical">std_cell/SCC40ULP_TF/V0p2/icc/tluplus/StarRC_40ULP_091125_1P7M_6Ic_1TMc_ALPA1/StarRC_40ULP_091125_1P7M_6Ic_1TMc_ALPA1_TYPICAL.tluplus</file>
      <file type="tluplus" metal_stack="1p7m_6ic" corner="cbest">std_cell/SCC40ULP_TF/V0p2/icc/tluplus/StarRC_40ULP_091125_1P7M_6Ic_1TMc_ALPA1/StarRC_40ULP_091125_1P7M_6Ic_1TMc_ALPA1_CMIN.tluplus</file>
      <file type="tluplus" metal_stack="1p7m_6ic" corner="cworst">std_cell/SCC40ULP_TF/V0p2/icc/tluplus/StarRC_40ULP_091125_1P7M_6Ic_1TMc_ALPA1/StarRC_40ULP_091125_1P7M_6Ic_1TMc_ALPA1_CMAX.tluplus</file>
      <file type="tluplus" metal_stack="1p7m_6ic" corner="rcbest">std_cell/SCC40ULP_TF/V0p2/icc/tluplus/StarRC_40ULP_091125_1P7M_6Ic_1TMc_ALPA1/StarRC_40ULP_091125_1P7M_6Ic_1TMc_ALPA1_RCMIN.tluplus</file>
      <file type="tluplus" metal_stack="1p7m_6ic" corner="rcworst">std_cell/SCC40ULP_TF/V0p2/icc/tluplus/StarRC_40ULP_091125_1P7M_6Ic_1TMc_ALPA1/StarRC_40ULP_091125_1P7M_6Ic_1TMc_ALPA1_RCMAX.tluplus</file>
      <!-- NXGRD file require metal stack and corner -->
      <file type="nxtgrd" metal_stack="1p7m_6ic" corner="typical">starRC/TD-LO40-XS-2091v0/SMIC_CCIStarRC_40ULP_091125_1P7M_6Ic_1TMc_ALPA1_V1.12_REV3_0/StarRC_40ULP_091125_1P7M_6Ic_1TMc_ALPA1/NXTGRD/StarRC_40ULP_091125_1P7M_6Ic_1TMc_ALPA1_TYPICAL.nxtgrd</file>
      <file type="empty_spice_subckt" metal_stack="1p7m_6ic">SPDK40LGULP_091125_OA_CDS_V1.12_REV4_0/smic40lgulp_091125_1P7M_6Ic_1TMc_ALPA1_oa_cds_v1.12_REV4_0/Calibre/LVS/empty_subckt.sp</file>
      <file type="innovus_lef" metal_stack="1p7m_6ic">std_cell/SCC40ULP_TF/V0p2/innovus/uhd/scc40n_1p7m_6ic_1mttc_alpa1.lef</file>
      <file type="redhawk_tech_file" metal_stack="1p7m_6ic" corner="typical">SPDK40LGULP_091125_OA_CDS_V1.12_REV4_0/SMIC_Redhawk_PA_40ULP_091125_1P7M_6Ic_1TMc_ALPA1_V1.10_REV1_0/Totem_40ULP_091125_1P7M_5Ic_1TMc_ALPA1_TYPICAL.tech</file>
      <file type="layer_map" metal_stack="1p7m_6ic" corner="typical">std_cell/SCC40ULP_TF/V0p2/icc/tluplus/StarRC_40ULP_091125_1P7M_6Ic_1TMc_ALPA1/StarRC_40ULP_091125_1P7M_6Ic_1TMc_ALPA1_cell.map</file>
      <!-- The gds_layer_map file is generated from an EDA tool. Not an original file from PDK -->
      <file type="gds_layer_map" metal_stack="1p7m_6ic" corner="typical">std_cell/SCC40ULP_TF/V0p2/icc/gdsInOutLayer.map</file>
    </techfile>
  </pdk>
