Sync Users and groups with AD
===============

This project creates and syncs Groups and Users from AD to Openstack.

Requirements
------------

Set some stuff in `config.ini`. There is a template `config.ini.tpl`

What does it
------------
1. Checks if User is in 'Team - Openstack' and in one of the 'Openstack - <groupname>' and then creates the user in Openstack and adds them to the '_ad_sync_users' group in openstack.
2. If Openstack user is in '_ad_sync_users' but not in AD, the user is disabled
3. Created a new Openstack group if a new AD group with 'Openstack - exists'
4. Removes group if it doesn't exists anymore
5. Syncs group memberships
6. Sends mail to configured mailaddress with the new users creds.


How to use
------------
set your config in config.ini and then run
`./adsync.py`
