# README

Welcome to the GitHub page for MCTin Server. MCTin is a solder alternative that provides easy modpack creation and distribution using a Django server and a Python client.

### Requirements:
* Python (v3)
    * With the 'uwsgi' and 'Django' modules installed.


### Installation and Usage:
1. Clone the repository.
    - `git clone https://github.com/EyeDevelop/MCTin`

* (Optional) create a virtualenv to keep Python packages separated.
    - `virtualenv <env_name>`
    - `source <env_name>/bin/activate`

2. Install the required Python packages.
    - `pip install uwsgi Django`
2. Run MCTin Server.
    - `uwsgi --http=<your_local_ip_address>:<preferred_port> --module=Server.wsgi`
    - (With the virtualenv use this) `uwsgi --http=<your_local_ip_address>:<preferred_port> --module=Server.wsgi --home=<env_name>`
    
Send your clients to http://\<your_local_ip_address\>:\<preferred_port\>


### Modpack Creation
1. Duplicate the 'examplepack' in the data/modpacks folder.
1. Edit the modpack.json to your liking.
1. Add the required jars to data/modpacks/\<yourmodpack\>/mods/
1. Add the mods to the modpack.json
