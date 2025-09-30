.. _manual_install:

How to Install
--------------

.. note:: Before start, please ensure all the dependencies are installed on your system. See details in :ref:`manual_dependency`

.. note:: Please prepare 6GB disk space to install ArkAngel Engineering Edition


Run Installer
~~~~~~~~~~~~~

Get your installer and place it to a location. For example, 

.. code-block:: shell

  ~/rapidflex_aaee/ArkAngel_Engineering-1.0.0-Linux.run

To start the installation process, you may choose to 

- double click the file
- or run the command 

.. code-block:: shell

  cd ~/rapidflex_aaee/
  ./ArkAngel_Engineering-1.0.0-Linux.run

.. warning:: You have to modify the installation folder as the default one contains a space

:numref:`fig_aaee_install_path` is an example how you can modify the installation folder

.. _fig_aaee_install_path:

.. figure:: ./figures/install_path.png
   :width: 100%
   :alt: aaee install path

Follow the installer guidelines to accomplish the installation process. 

Launch ArkAngel
~~~~~~~~~~~~~~~

To launch ArkAngel, the envoirnment variable should be properly set up.

.. code-block::

  # This is the example for bash
  export PATH=$PATH:/opt/ArkAngel_Engineering_1.0.0/bin

.. code-block::

  # This is the example for csh
  setenv PATH $PATH:/opt/ArkAngel_Engineering_1.0.0/bin


.. note:: You may add the setup to your shell init script. Such as ~/.bashrc and ~/.cshrc

.. warning:: Please do **NOT** switch to any shell or window after setup, unless add the env variable to your shell init script. 

After the setup, you can launch ArkAngel by 

.. code-block::

  # Enter interactive mode
  aaee -i

Or you can run batch mode by 

.. code-block::

  # Enter interactive mode
  aaee -f <your_aaee_script>


 
