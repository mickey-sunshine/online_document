.. _manual_project_tree_bitstream:

Bitstream
---------

.. _manual_project_tree_bitstream_run:

Runs
~~~~

The workspace may contains a number of runs for benchmarking, each of which is based on a different version of architecture.

For example, in the project ``alkaid_exto``, three runs ``iter0``, ``iter1`` and ``iter2`` are created by users.

.. code-block::

  alkaid_exto/alkaid_exto_bitstream/
  ├── iter0
  ├── iter1
  └── iter2

- Note that the name of run can be customized by user. In practice, various names may be expected.
- However, each sub-directory under the arch workspace represents an independent run.
- There are no data dependencies between runs

.. _manual_project_tree_bitstream_workspace:

Workspace
~~~~~~~~~

In each run, the workspace is organized as follows:

Here, take the example of run ``iter0`` of project ``alkaid_exto``

.. code-block::

  alkaid_exto/alkaid_ex_bitstream/
  └── iter0
      ├── arch -> ../../alkaid_ex_arch/iter0/arch/ultimate
      ├── bitstream
      ├── openfpga_tasks
      └── vpr_results


- ``arch`` is linked to a specific architecture run
- ``openfpga_tasks`` contains a number of runtime directories, where architecture data is generated and analyzed. This directory does not contain golden copies.
- ``bitstream`` is the golden copies of bitstreams, which is the data pack for the downstream development
- ``vpr_results`` is the golden copies of VPR intermediate results, which is the data pack for the downstream development

.. note:: Only ``ultimate`` fabric is considered to golden bitstream generation
