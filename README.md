# Dir-protector

Dir-protector is a directory protector tool used in CTF which will keep all content in target directory constant. It report any modification in this directory and record these in backup directory.


## Install
Zipball can be download [here](https://github.com/Arvin-X/dir-protector/archive/master.zip) or use git to get this tool:

```
git clone git@github.com:Arvin-X/dir-protector.git
```
It can work with Python 2.X or Python 3.X. But if you are using Python 2.6.X, you may need to install python lib *argparse*.


## Usage
```
usage: dir-protector.py [-h] [-r] [-t TIME] target_dir backup_dirpositional arguments:  target_dir  directory you want to protect  backup_dir  content in target_dir will be copied into this directory for              restoring origin directory and backup. this directory must not              already existoptional arguments:  -h, --help  show this help message and exit  -r          record new added and modified files in a new directory              'record_files' which will be created in 'backup_dir'  -t TIME     interval time between scans
```

## Li