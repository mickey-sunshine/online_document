.. _manual_hdl_code:

HDL Coding Guidelines
---------------------

Standards
`````````

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

Initial State
`````````````

.. warning:: Fail to specify initial states will cause 'X' signals when running post-synthesis simulations (see guidelines in :ref:`datasheet_post_synth_sim`).

Please define initial states of registers in your HDL, for example.

.. code-block::

  reg [7:0] result;

  initial begin
    result <= 0;
  end

Always
``````

Avoid use ``always @(*)`` blocks. Instead, provide specific signals to the sensitivity list of always blocks. For example,

.. code-block::

  # Avoid to use always @(*) even for combinatorial blocks
  always @(posedge clk or negedge rst) begin
    if (rst == 1'b0) begin
      result <= 0;
    else begin
      result <= result + 1;
    end
  end
