#!/usr/bin/python
# -*- coding: utf-8 -*-

#Import needed libs
import datetime
import time
import sys
import subprocess
from subprocess import Popen, PIPE
from time import localtime, strftime

def main():
  EXE = "sudo /media/2/code/raspberry_lcd/dht11"
  LOG = "/media/2/log/"+strftime("%Y-%m_local_data.log", localtime())

  while True:
    try:
      #Read sensor data twice to refresh data
      output=subprocess.check_output(EXE, shell=True)
      output=subprocess.check_output(EXE, shell=True)
      #Parse local data
      ldata = output.split()
      #Get date
      date = strftime("%d-%m-%Y %H:%M", localtime())
      #Open log file to write
      f = open(LOG,'a')
      #Save data into log file
      f.write(date + ' ' + ldata[1] + ' ' + ldata[0] + '\n')
      #Close log file
      f.close()
      #Stop loop
      break
    except:
      #If sensor reading fail, try again
      continue

if __name__ == '__main__':
   main()

