.. _manual_dependency:

Dependencies
~~~~~~~~~~~~

Dependencies can be installed upon the use of ArkAngel on different systems

For the GUI build on WSL, please use the following to resolve Qt lib issues:

.. code-block::
   
   # If you encounter issues like: 
   # ./build/gui/arkangel_engineering_kit: error while loading shared libraries: libQt5Core.so.5: cannot open shared object file: No such file or directory
   sudo strip --remove-section=.note.ABI-tag /usr/lib/x86_64-linux-gnu/libQt5Core.so.5 
   # If you encounter issues like: qt.qpa.xcb: could not connect to display
   # Ensure that you have installed X11 (Xlaunch on Win) and run the following if your shell is bash
   echo "export DISPLAY=:0.0" >> ~/.bashrc

Ubuntu
^^^^^^

Currently, the supported version of Ubuntu are 

- Ubuntu 22.04 LTS
- Ubuntu 20.04 LTS

- Dependencies required to build the code base

.. include:: ubuntu_dependencies.sh
  :code: shell

- Dependencies required to run regression tests

.. include:: regtest_dependencies.sh
  :code: shell
  
.. note:: Python packages are also required
  
.. code-block::

  python3 -m pip install -r requirements.txt

- Dependencies required to build documentation

.. include:: doc_dependencies.sh
  :code: shell

CentOS 9
^^^^^^^^

- Dependencies required to build the code base

.. include:: centos9_deps.sh
  :code: shell

- Dependencies required to run regression tests

.. include:: regtest_dependencies.sh
  :code: shell
  
.. note:: Python packages are also required
  
.. code-block::

  python3 -m pip install -r requirements.txt

- Dependencies required to build documentation

.. include:: doc_dependencies.sh
  :code: shell

CentOS 7.9
^^^^^^^^^^

- Dependencies required to build the code base

.. include:: centos7.9_deps.sh
  :code: shell

- Dependencies required to run regression tests

.. include:: regtest_dependencies.sh
  :code: shell
  
.. note:: Python packages are also required
  
.. code-block::

  python3 -m pip install -r requirements.txt

- Dependencies required to build documentation

.. include:: doc_dependencies.sh
  :code: shell
