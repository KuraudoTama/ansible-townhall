Ansible Townhall
================

1. Before running this project for test/dev purpose, you need to add the root folder "`ansible-townhall`" to **PYTHONPATH**. Otherwise the python interpreter is unable to find the modules of this project.

    For example, suppose that you put the "`ansible-townhall`" under */root/python_app* folder on Linux like this: */root/python_app/ansible-townhall*.
    It's better to write "`export PYTHONPATH=$PYTHONPATH:/root/python_app/ansible-townhall`" into `.bashrc` file so that when you log in Linux everytime,
    that path could be added to **PYTHONPATH**.

2. Make sure you have installed required libraries.

    ```bash
    $ pip install -r requirements.txt
    ```

3. Make sure you have installed `Ansible` on the same server. Please refer to <http://docs.ansible.com/ansible/intro.html>.

4. Make sure you have installed `Git` client on the same server.
   
   ```bash
   $sudo apt-get install git
   ``` 

5. After installing `Ansible`, run "`vi /etc/ansible/ansible.cfg`" to find what the path of callback plugins is.

    For example:

    > callback_plugins   = /usr/share/ansible_plugins/callback_plugins

6. Run "`cd <your_path>/ansible-townhall/job_service`", copy "`ansible_logger_plugin.py`" to above callback plugins' path.

7. Make sure you have installed **MongoDB**, version 3.0.x on the same server.Then, launch it.

8. Run "`python <your_path>/ansible-townhall/runserver.py`" to launch the dev/test server.

9. Use either command "curl" or firefox restclient plugin to call the REST apis of job_api/ansible_job_api.py or code_repo_api/ansible_repo_api.py.

10. This app's log file "**ansible_job.log**" will be generated under "`/etc/ansible/job_logging/`".

11. If you want to test/call "`create_job`" REST api, you need to write your own playbooks.