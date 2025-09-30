.. _file_format_clock_location_map_file:

Ckbuf Location Map File (.xml)
==============================

The Ckbuf location map file is formatted in XML and details the names of global pins along with the physical locations of clock buffers on the chip. This enables the engine to quickly identify clock resources and efficiently perform clock allocation and placement. It is especially useful for generating the VPR constraint file.

An example file is shown as follows.

.. literalinclude:: ckbuf_loc_map.xml
   :language: xml

ckbuf location map
^^^^^^^^^^^^^^^^^^

Each ``ckbuf`` block is defined as a key.

.. option:: <ckbuf pin="<string>" x="<int>" y="<int>" z="<int>" type="<string>"/>

  - ``pin`` indicates the pin name of a global port of the eFPGA which will drive the ckbuf at the specified location (x, y, z).

  - ``x`` indicates the x location of the ckbuf. 

  - ``y`` indicates the y location of the ckbuf. 

  - ``z`` indicates the subtile of the ckbuf. 

  - ``type`` indicates the type of the ckbuf. The type matches the type of ckbuf in the ckbuf_cell_map file :ref:`file_format_ckbuf_cell_map_file`.

    .. note:: The pin name of ckbuf should be consistent with the pin name in pcf :ref:`file_format_pin_constraints_file`. 
      

