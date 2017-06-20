from modules import cbpi
import os

def chown_unroot(path):
    """
    Changes owner of the path recursively from root:root to the user:group who installed craftbeerpi
        can be used to unroot plugins and craftbeerpi updates
    """    
    dir_stat = os.stat('.')
    uid = dir_stat.st_uid
    gid = dir_stat.st_gid

    cbpi.app.logger.info("Executing chown -R for: " + path)

    for root, dirs, files in os.walk(path):
        os.chown(root, uid, gid) 
        for name in dirs:  
            os.chown(os.path.join(root, name), uid, gid)
        for name in files:
            os.chown(os.path.join(root, name), uid, gid)