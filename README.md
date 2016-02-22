Ansible Townhall
================

1. Before running this project for test/dev purpose, you need to add the root folder "`ansible_job`" to **PYTHONPATH**. Otherwise the python interpreter is unable to find the modules of this project.

    For example, suppose that you put the "`ansible_job`" under */root/python_app* folder on Linux like this: */root/python_app/ansible_job*.
    It's better to write "`export PYTHONPATH=$PYTHONPATH:/root/python_app/ansible_job`" into `.bashrc` file so that when you log in Linux everytime,
    that path could be added to **PYTHONPATH**.

2. Make sure you have installed required libraries.

    ```bash
    $ pip install -r requirements.txt
    ```

3. Make sure you have installed `Ansible` on the same server. Please refer to <http://docs.ansible.com/ansible/intro.html>.

4. After installing `Ansible`, run "`vi /etc/ansible/ansible.cfg`" to find what the path of callback plugins is.

    For example:

    > callback_plugins   = /usr/share/ansible_plugins/callback_plugins

5. Run "`cd <your_path>/ansible_job/job_service`", copy "`ansible_job_logger.py`" to above callback plugins' path.

6. Make sure you have installed **MongoDB**, version 3.0.x on the same server. After installation, please **check the port of MongoDB**, change them in
   the "`<your_path>/ansible_job/job_persistence/db_connection.py`" and "`<your_path>/ansible_job/job_persistence/ansible_job_logger.py`" if the port is not **27017**.
   Then, launch MongoDB.

7. Run "`python <your_path>/ansible_job/job_api/ansible_job_api.py`" to launch the dev/test server.

8. Use either command "curl" or firefox restclient plugin to call the REST apis of ansible_job_api.py.

9. This app's log file "**ansible_job.log**" will be generated under "`<your_path>/ansible_job/job_logging`".

10. If you want to test/call "`create_job`" REST api, you need to write your own playbooks.