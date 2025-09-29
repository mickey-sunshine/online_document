.. _manual_project_tree_overview:

Overview
--------

When an eFPGA tapeout project is created, a directory is created at designated location.

For example, when you name the project to be ``alkaid_exto``, a directory ``alkaid_exto`` will be created.
This is the workspace of the tapeout project.

A tapeout project consists a number of sub-projects, each of which is a workspace for a specific objective.
Note that the sub-projects are cross-linked to share data.

- ``arch``: workspace for architecture development. See details in :ref:`manual_project_tree_arch`
- ``bitstream``: workspace for golden bitstream and benchmarking results. See details in :ref:`manual_project_tree_bitstream`
- ``netlist``: workspace for golden netlists, netlist synthesis and gate-level QoR extraction. See details in :ref:`manual_project_tree_netlist`
- ``pd``: workspace for physical design, sign-off and layout-level QoR extraction. See details in :ref:`manual_project_tree_pd`
- ``dv``: workspace for design verification across RTL-level, gate-level and post-layout. See details in :ref:`manual_project_tree_dv`
- ``pre_arch_analysis``: workspace for running any analysis before selecting any architecture. See details in :ref:`manual_project_pre_arch`

Take the example the project name to be ``alkiad_exto``, the sub-projects are organized as follows:

.. code-block:: shell

  alkaid_exto/
  ├── alkaid_ex_arch
  ├── alkaid_ex_bitstream
  ├── alkaid_ex_netlist
  ├── alkaid_ex_pd
  ├── alkaid_ex_dv
  └── alkaid_ex_pre_arch_analysis
