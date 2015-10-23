def sync_lists(activedirectory,keystone):
    added = [x for x in activedirectory if x not in keystone]
    removed = [x for x in keystone if x not in activedirectory
    return {'added' : added , 'removed' : removed }



### algo
# 1. get list of users from ad
# 2. get list of users from ks
# 3. sync_lists
# 4. disable removed accounts
# 5. create new accounts and send email
# 5a. add them to researchgroup
# 5b. add them to hpc users
# 6. cleanup old accounts (disabled for 30 days)
# 7. update flavor access
