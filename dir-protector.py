#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import argparse
import time
import logging
import hashlib
import subprocess

from os.path import join as pjoin

LOG=logging.getLogger()
ORIG_MD5_DICT={}
ORIG_DIRL=[]
TIMEF='%H_%M_%S'

RECORD=False

def scan(tdir,bdir):
	checked_files=[]
	checked_dirs=[]
	for path,dirs,files in os.walk(tdir):
		# check new added directory
		for dir in dirs:
			dpath=pjoin(path,dir)
			LOG.debug('[*] scan directory:'+dpath)
			relpath=os.path.relpath(dpath,tdir)
			if relpath not in ORIG_DIRL:
				rlog=''
				rname=dir+'_'+time.strftime(TIMEF,time.localtime())
				if RECORD:
					# record this new directory 
					rpath=pjoin(bdir,'record_files',rname)
					if os.path.exists(rpath):
						shutil.rmtree(rpath)	
					shutil.copytree(dpath,rpath)
					rlog='  Record with name: '+rname
				LOG.warning('[+] Added direcory: '+relpath+rlog)

				# report files info in this new directory
				for ipath,idirs,ifiles in os.walk(dpath):
					for ifile in ifiles:
						LOG.warning('[+] File in added directory: '+
							pjoin(ipath,ifile))
				
				shutil.rmtree(dpath)
			else:
				checked_dirs.append(relpath)

		for file in files:
			# check new added file
			fpath=pjoin(path,file)
			LOG.debug('[*] scan file:'+fpath)
			relpath=os.path.relpath(fpath,tdir)
			if relpath not in ORIG_MD5_DICT:
				rlog=''
				rname=file+'_'+time.strftime(TIMEF,time.localtime())
				if RECORD:
					shutil.copy2(pjoin(fpath,bdir,'record_files',rname))
					rlog='  Record with name: '+rname
				LOG.warning('[+] Added file: '+relpath+rlog)
				os.remove(fpath)
				continue

			# check modified file
			fmd5=calc_md5(fpath)
			if fmd5!=ORIG_MD5_DICT[relpath]:
				rlog=''
				rname=file+'_'+time.strftime(TIMEF,time.localtime())
				if RECORD:
					shutil.copy2(fpath,pjoin(bdir,'record_files',rname))
					rlog='  Record with name: '+rname
				LOG.warning('[!] Modified file: '+relpath+rlog)
				shutil.copy2(pjoin(bdir,relpath),fpath)
			# set checked flag
			checked_files.append(relpath)

	# restore directory
	for x in ORIG_DIRL:
		if x not in checked_dirs:
			if os.path.exists(pjoin(tdir,x)):
				continue

			LOG.warning('[-] Deleted directory: '+x)
			shutil.copytree(pjoin(bdir,x),pjoin(tdir,x))
			# set checked flag
			for ipath,idirs,ifiles in os.walk(pjoin(tdir,x)):
				for ifile in ifiles:
					LOG.warning('[-] File in deleted directory: '+
						os.path.relpath(pjoin(ipath,ifile),tdir))
					checked_files.append(os.path.relpath(pjoin(ipath,ifile),tdir))

	# check wether there is any file has been dleted
	for k in ORIG_MD5_DICT:
		if k not in checked_files:
			LOG.warning('[-] Deleted file: '+k)
			shutil.copy2(pjoin(bdir,k),pjoin(tdir,k))

def calc_md5(filepath,block_size=64 * 1024):
	with open(filepath, 'rb') as f:
		md5 = hashlib.md5()
		while True:
			data = f.read(block_size)
			if not data:
				break
			md5.update(data)
		return md5.hexdigest()

def init_logger():
	cli_logger = logging.StreamHandler(sys.stdout)
	cli_formatter = logging.Formatter('[%(asctime)s] %(message)s',
		datefmt='%H:%M:%S')
	cli_logger.setFormatter(cli_formatter)
	LOG.addHandler(cli_logger)
	LOG.setLevel(logging.INFO)
	
def prepare(tdir,bdir):
	init_logger()
	# back up entire dirctory
	try:
		shutil.copytree(tdir,bdir)
	except Exception as e:
		print('\n[*] error: '+str(e)+'\n')
		return
	LOG.info('[*] protecting directory: '+tdir)
	LOG.info('[*] backup path: '+bdir)
	# calculate md5 value of each file
	for path,dirs,files in os.walk(tdir):
		for dir in dirs:
			relpath=os.path.relpath(pjoin(path,dir),tdir)
			ORIG_DIRL.append(relpath)
		for file in files:
			fpath=pjoin(path,file)
			relpath=os.path.relpath(fpath,tdir)
			fmd5=calc_md5(fpath)
			ORIG_MD5_DICT[relpath]=fmd5
			LOG.debug('[*] '+relpath+' : '+fmd5)
	
	ORIG_DIRL.sort()
	# create directory for storing new added or modified files
	if RECORD:
		os.mkdir(pjoin(bdir,'record_files'),0o755)

def parse_args():
	parser=argparse.ArgumentParser()
	parser.add_argument('tdir',metavar='target_dir',
		help='directory you want to protect')
	parser.add_argument('bdir',metavar='backup_dir',
		help='content in target_dir will be copied into this directory for '
			'restoring origin directory and backup. this directory must '
			'not already exist')
	parser.add_argument('-r',dest='record',action='store_true',default=False,
		help="record new added and modified files in a new directory"
			" 'record_files' which will be created in 'backup_dir'")
	parser.add_argument('-t',dest='itime',metavar='TIME',type=float,default=0,
		help='interval time between scans')

	args=parser.parse_args()
	global RECORD
	RECORD=args.record
	return args.tdir,args.bdir,args.itime

def main():
	# get args first	
	tdir,bdir,itime=parse_args()
	if not os.path.isdir(tdir):
		print('\n[*] error: '+tdir+' is not directory'+'\n')
		return 
	if os.path.exists(bdir):
		print('\n[*] error: '+bdir+' has already exist'+'\n')
		return

	prepare(tdir,bdir)
	while True:
		scan(tdir,bdir)
		time.sleep(itime)

if __name__=='__main__':
	main()
