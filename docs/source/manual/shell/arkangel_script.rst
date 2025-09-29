.. _arkangel_script_format:

ArkAngel Script Format
----------------------

ArkAngel accepts a simplified tcl-like script format.

.. option:: Comments
   
   Any content after a ``#`` will be treated as comments.
   Comments will not be executed.

  .. note:: comments can be added inline or as a new line. See the example below

.. option:: Continued line
  
   Lines to be continued should be finished with ``\``.
   Continued lines will be conjuncted and executed as one line
 
  .. note:: please ensure necessary spaces. Otherwise it may cause command parser fail.

The following is an example.

.. code-block:: python

  # Create a new project
  create_project --config_file example_prj.xml
  
  # Run synthesis
  synth --strategy_file my_synth_strategy.xml

  # Run implementation
  implement \
    --strategy_file my_impl_strategy.xml

  # Run bitstream generation
  bitgen --strategy_file my_bitgen_strategy.xml
  
  # Finish and exit
  exit
