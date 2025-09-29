.. _manual_project_tree_pd:

Bitstream
---------

.. _manual_project_tree_pd_run:

Runs
~~~~

The workspace may contains a number of runs for benchmarking, each of which is based on a different version of architecture.

For example, in the project ``alkaid_exto``, three runs ``iter0``, ``iter1`` and ``iter2`` are created by users.

.. code-block::

  alkaid_exto/alkaid_exto_pd/
  ├── iter0
  ├── iter1
  └── iter2

- Note that the name of run can be customized by user. In practice, various names may be expected.
- However, each sub-directory under the arch workspace represents an independent run.
- There are no data dependencies between runs

.. _manual_project_tree_pd_workspace:

Workspace
~~~~~~~~~

TBD
