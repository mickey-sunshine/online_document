.. _manual_project_tree_pre_arch:

Bitstream
---------

.. _manual_project_tree_pre_arch_run:

Runs
~~~~

The workspace may contains a number of runs for benchmarking, each of which is based on a different version of architecture.

For example, in the project ``alkaid_exto``, three runs ``iter0``, ``iter1`` and ``iter2`` are created by users.

.. code-block::

  alkaid_exto/alkaid_exto_pre_arch_analysis/
  ├── iter0
  ├── iter1
  └── iter2

- Note that the name of run can be customized by user. In practice, various names may be expected.
- However, each sub-directory under the arch workspace represents an independent run.
- There are no data dependencies between runs

.. _manual_project_tree_pre_arch_workspace:

Workspace
~~~~~~~~~

In each run, the workspace is organized as follows:

Here, take the example of run ``iter0`` of project ``alkaid_exto``

.. code-block::

  alkaid_exto/alkaid_ex_pre_arch_analysis/
  └── iter0
      ├── and2
      │   ├── sweep_k4
      │   ├── sweep_k5
      │   └── sweep_k6
      ├── and2_latch
      │   ├── sweep_k4
      │   ├── sweep_k5
      │   └── sweep_k6
      └── counterdown16_1clk_negedge_async_resetp
          ├── sweep_k4
          ├── sweep_k5
          └── sweep_k6


- Each benchmark has a dedicated directory as its runtime directory for various anlaysis. For example, ``and2``
- ``sweep_k<int>`` is the runtime directory for LUT size analysis, where the integer represent the selected number of inputs for the LUTs
