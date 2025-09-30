.. _manual_project_tree_dv:

Design Verification
-------------------

.. _manual_project_tree_dv_run:

Runs
~~~~

The workspace may contains a number of runs for design verification, each of which is based on a different version of bitstream and netlists.

For example, in the project ``alkaid_exto``, three runs ``iter0``, ``iter1`` and ``iter2`` are created by users.

.. code-block::

  alkaid_exto/alkaid_exto_dv/
  ├── iter0
  ├── iter1
  └── iter2

- Note that the name of run can be customized by user. In practice, various names may be expected.
- However, each sub-directory under the arch workspace represents an independent run.
- There are no data dependencies between runs

.. _manual_project_tree_dv_workspace:

Workspace
~~~~~~~~~

In each run, the workspace is organized as follows:

Here, take the example of run ``iter0`` of project ``alkaid_exto``

.. code-block::

  alkaid_exto/alkaid_ex_dv/
  └── iter0
      ├── arch -> ../../alkaid_ex_bitstream/iter0/arch
      ├── dv
      │   ├── bitstream -> ../../alkaid_ex_bitstream/iter0/bitstream
      │   └── preconfig_testbench
      ├── netlist
      │   ├── gl -> ../../alkaid_ex_netlist/iter0/netlist/gl/ultimate
      │   ├── pl
      │   └── rtl -> ../../alkaid_ex_netlist/iter0/netlist/rtl/ultimate
      ├── openfpga_tasks
      └── vpr_results -> ../../alkaid_ex_bitstream/iter0/vpr_results

- ``arch`` is linked to a specific architecture run
- ``openfpga_tasks`` contains a number of runtime directories, where testbenches are generated and analyzed. This directory does not contain golden copies.
- ``dv`` is the runtime directory for running various design verification
  - ``bitstream`` is linked to a specific run of bitstream
  - ``preconfig_testbench`` is the runtime directory for preconfigured simulation
- ``vpr_results`` is linked to a specific run of bitstream

.. note:: Only ``ultimate`` fabric is considered to golden bitstream generation
