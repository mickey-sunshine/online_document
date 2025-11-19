.. _manual_hdl_code:

HDL Coding Guidelines
=====================

Standards
---------

.. list-table:: HDL Support
  :widths: 20 20 20 20
  :header-rows: 1

  * - Language
    - Verilog
    - VHDL
    - SystemVerilog
  * - Standard
    - IEEE Std 1364-2005
    - N/A
    - N/A


Basic Coding Rules
------------------

Explicit Register Declaration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Registers must be explicitly declared.

.. code-block::

  // reg must be explicitly defined 
  module test (
      input  wire a,  // wire can be explicitly defined
      input       b,  // wire can be implicitly defined
      output reg  c,  // reg must be explicitly defined
      output reg  d   // reg must be explicitly defined
  );

alternatively,

.. code-block::

  // the following also works 
  module test (
      a,
      b,
      c,
      d
  );
      input wire a;   // wire can be explicitly defined
      input      b;   // wire can be implicitly defined
      output reg c;   // reg must be explicitly defined
      output reg d;   // reg must be explicitly defined

Register Assignments
~~~~~~~~~~~~~~~~~~~~

Use Non-Blocking Assignment
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Always use non-blocking assignment (``<=``) for register assignments.

.. code-block::

  reg state_c, state_n;
  always @(posedge clk or negedge rst_n) begin
      if (!rst_n) begin
          state_c <= 1'b0;
      end else begin
          state_c <= state_n;     // use non-blocking assignment
          // state_c = state_n;   // blocking assignment , not recommended
      end
  end

Reset Requirement
^^^^^^^^^^^^^^^^^
Registers **must have a reset signal**.

.. warning::  
   Failing to specify initial states will cause 'X' signals when running post-synthesis simulations (see guidelines in :ref:`datasheet_post_synth_sim`).

.. code-block:: 

    // registers must have a reset signal 
    reg state_c, state_n;

    // correct case: include reset
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state_c <= 1'b0;
        end else begin
            state_c <= state_n;
        end
    end

    // wrong case: no reset
    // always @(posedge clk) begin
    //     state_c <= state_n;
    // end


Assignments in Combinational Logic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use ``assign`` for Combinational Logic
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: 

    wire a, b, c;
    assign c = a & b;

Blocking Assignments
^^^^^^^^^^^^^^^^^^^^
Blocking assignments (``=``) are only allowed in combinational logic.

.. code-block::   

  wire a, b, c;
  reg d;
  assign c = a & b;
  always @(posedge clk_i or negedge rst_ni) begin
      if (!rst_ni) begin
          d <= 1'b0;
      end else begin
          d <= c;
          // d = c; // blocking assignments are only allowed in combinational logic
      end
  end


Conditional Statements
~~~~~~~~~~~~~~~~~~~~~~

Complete Case/If Statements
^^^^^^^^^^^^^^^^^^^^^^^^^^^
``case`` and ``if`` must cover **all conditions**. Otherwise, a ``default`` branch is required.

.. code-block::

  always @(posedge clk_i or negedge rst_ni) begin
      if (!rst_ni) begin
          d <= 2'd0;
      end else begin
          case (state)
              2'b01: d <= 2'd1;
              2'b10: d <= 2'd2;
              2'b11: d <= 2'd2;
              2'b00: d <= 2'd0;   // must cover all conditions
              // default: d <= 2'd0; // or use default
          endcase
      end
  end

Prohibit Implicit Latches
^^^^^^^^^^^^^^^^^^^^^^^^^
All outputs must be assigned values in **all branches** within any logic block.

.. code-block:: 

  // Wrong case
  reg a, b;
  always @(posedge clk or negedge rstn) begin
      if (!rstn) begin
          b <= 1'b0;
      end else begin
          if (a == 1'b0) begin
              b <= 1'b1;
          end
      end
  end

  // Correct case
  reg a, b;
  always @(posedge clk or negedge rstn) begin
      if (!rstn) begin
          b <= 1'b0;
      end else begin
          if (a == 1'b0) begin
              b <= 1'b1;
          end else begin
              b <= 1'b0;  // all outputs must be assigned values
          end
      end
  end


Assignment Consistency
~~~~~~~~~~~~~~~~~~~~~~

Do Not Mix ``=`` and ``<=``
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Do not mix blocking (``=``) and non-blocking (``<=``) assignments in the same ``always`` block.

.. code-block:: 

    reg a, b, c;
    always @(posedge clk or negedge rstn) begin
        if (!rstn) begin
            b <= 1'b0;
        end else begin
            c <= a;
            b <= c;
            // b = c;  // Do not mix <= and =
        end
    end


Data Structures
---------------

Avoid Complex Arrays
~~~~~~~~~~~~~~~~~~~~
Avoid using multidimensional arrays and dynamic arrays. Use only fixed-length vectors.

.. code-block::

    // reg [7:0] memory [0:7];    // not recommended
    reg [63:0] memory;            // recommended


Always Blocks
-------------

Avoid ``always @(*)``
~~~~~~~~~~~~~~~~~~~~~
Avoid using ``always @(*)`` blocks. Instead, provide explicit sensitivity lists.

.. code-block::

  // Avoid to use always @(*) even for combinatorial blocks
  always @(posedge clk or negedge rst) begin
    if (rst == 1'b0) begin
      result <= 0;
    end else begin
      result <= result + 1;
    end
  end

Location Constraints
--------------------

User can define location constraints through the following parameters when instanciate primitives:

- ``FPGA_LOC_X`` define the x coordinate. Please ensure the number is in the range of the FPGA fabric width. Otherwise, placement may fail. Refer to your device datasheet to valid range.
- ``FPGA_LOC_Y`` define the y coordinate. Please ensure the number is in the range of the FPGA fabric height. Otherwise, placement may fail. Refer to your device datasheet to valid range.
- ``FPGA_LOC_Z`` define the z coordinate. Please ensure the number is in the range of the capacity of (x, y) defined through ``FPGA_LOC_X`` and ``FPGA_LOC_Y``. Otherwise, placement may fail. Refer to your device datasheet to valid range.

.. warning:: Use real number. Integer will not work!

.. code-block::

  // Constrain the primitive to be mapped to (x=3, y=2, z=1)
  pcounter32 pcnt #(
    .FPGA_LOC_X(3.0), 
    .FPGA_LOC_Y(2.0), 
    .FPGA_LOC_Z(1.0)
  ) ( 
    .clk_i(ck),
    .rst_i(rst),
    .q_o(out)
  );

Other Rules
-----------

- ``define`` macros should only be used for parameterization.  
  ``Parameters`` are recommended as the first choice.  
- Avoid using ``inout``.  
- Do not rely on ``#delay`` and avoid behavioral-level syntax such as ``fork...join``.  
- Separate synthesizable code from testbench code.  
- The use of system tasks such as ``$display`` and ``$finish`` is prohibited in synthesizable code.  
