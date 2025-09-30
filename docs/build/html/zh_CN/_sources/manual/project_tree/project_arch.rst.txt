.. _manual_project_tree_arch:

Arch Development
----------------

.. _manual_project_tree_arch_run:

Runs
~~~~

The workspace may contains a number of runs for architecture, each of which represents a different version of architecture.

For example, in the project ``alkaid_exto``, three runs ``iter0``, ``iter1`` and ``iter2`` are created by users.

.. code-block::

  alkaid_exto/alkaid_exto_arch/
  ├── iter0
  ├── iter1
  └── iter2

- Note that the name of run can be customized by user. In practice, various names may be expected.
- However, each sub-directory under the arch workspace represents an independent run.
- There are no data dependencies between runs

.. _manual_project_tree_arch_workspace:

Workspace
~~~~~~~~~

In each run, the workspace is organized as follows:

Here, take the example of run ``iter0`` of project ``alkaid_exto``

.. code-block::

  alkaid_exto/alkaid_ex_arch/
  └── iter0
      ├── arch
      │   ├── dp
      │   └── ultimate
      └── openfpga_tasks
          ├── dp
          └── ultimate


- ``arch`` contains all the architecture data for a given eFPGA. This is the data pack (golden copies of files) for any downstream development
- ``openfpga_tasks`` contains a number of runtime directories, where architecture data is generated and analyzed. This directory does not contain golden copies.

.. note:: currently, there are two fabrics, ``dp`` and ``ultimate``. The ``dp`` is a small fabric which is mainly used for design planning during physical design. The ``ultimate`` is the actual fabric of the eFPGA.
