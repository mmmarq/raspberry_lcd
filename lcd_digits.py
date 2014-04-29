#!/usr/bin/python
# -*- coding: utf-8 -*-

#Import needed libs
import thread
import threading
import lcddriver
import datetime
import urllib2
import httplib
import time
import sys
import subprocess
from subprocess import Popen, PIPE
from time import gmtime, strftime
from xml.dom.minidom import parseString
from urllib2 import URLError
from urllib2 import HTTPError

#Loop control
goodBye = False

#Weather translate table
weather = {}
weather["ec"] = "Encoberto com Chuvas Isoladas"
weather["ci"] = "Chuvas Isoladas"
weather["c"] = "Chuva"
weather["in"] = "Instavel"
weather["pp"] = "Poss. de Pancadas de Chuva"
weather["cm"] = "Chuva pela Manha"
weather["cn"] = "Chuva a Noite"
weather["pt"] = "Pancadas de Chuva a Tarde"
weather["pm"] = "Pancadas de Chuva pela Manha"
weather["np"] = "Nublado e Pancadas de Chuva"
weather["pc"] = "Pancadas de Chuva"
weather["pn"] = "Parcialmente Nublado"
weather["cv"] = "Chuvisco"
weather["ch"] = "Chuvoso"
weather["t"] = "Tempestade"
weather["ps"] = "Predominio de Sol"
weather["e"] = "Encoberto"
weather["n"] = "Nublado"
weather["cl"] = "Ceu Claro"
weather["nv"] = "Nevoeiro"
weather["g"] = "Geada"
weather["ne"] = "Neve"
weather["nd"] = "Nao Definido"
weather["pnt"] = "Pancadas de Chuva a Noite"
weather["psc"] = "Possibilidade de Chuva"
weather["pcm"] = "Possibilidade de Chuva pela Manha"
weather["pct"] = "Possibilidade de Chuva a Tarde"
weather["pcn"] = "Possibilidade de Chuva a Noite"
weather["npt"] = "Nublado com Pancadas a Tarde"
weather["npn"] = "Nublado com Pancadas a Noite"
weather["ncn"] = "Nublado com Poss. de Chuva a Noite"
weather["nct"] = "Nublado com Poss. de Chuva a Tarde"
weather["ncm"] = "Nubl. c/ Poss. de Chuva pela Manha"
weather["npm"] = "Nublado com Pancadas pela Manha"
weather["npp"] = "Nublado com Possibilidade de Chuva"
weather["vn"] = "Variacao de Nebulosidade"
weather["ct"] = "Chuva a Tarde"
weather["ppn"] = "Poss. de Panc. de Chuva a Noite"
weather["ppt"] = "Poss. de Panc. de Chuva a Tarde"
weather["ppm"] = "Poss. de Panc. de Chuva pela Manha"

# User-defined chars (binary)
cells = {}
cells['1'] = [0b00011,0b00011,0b00011,0b00000,0b00000,0b00000,0b00000,0b00000]
cells['2'] = [0b00111,0b00111,0b00111,0b00111,0b00111,0b00111,0b00111,0b00111]
cells['3'] = [0b11111,0b11111,0b11111,0b00111,0b00111,0b00111,0b00111,0b00111]
cells['4'] = [0b00011,0b00011,0b00011,0b00011,0b00011,0b00011,0b00011,0b00011]
cells['5'] = [0b11111,0b11111,0b11111,0b10000,0b10000,0b10000,0b10000,0b10000]
cells['6'] = [0b11100,0b11100,0b11100,0b11100,0b11100,0b11100,0b11100,0b11100]
cells['7'] = [0b11111,0b11111,0b11111,0b00000,0b00000,0b00000,0b00000,0b00000]
cells['8'] = [0b00111,0b00111,0b00111,0b00000,0b00000,0b00000,0b00000,0b00000]

# Numbers are printed based on cells
digits = {}
digits[1] = [0x00,0x05,0xFE,0x05,0x00,0x06]
digits[2] = [0x00,0x02,0x03,0x04,0x00,0x06]
digits[3] = [0x00,0x02,0x00,0x02,0x00,0x06]
digits[4] = [0x03,0x01,0x00,0x02,0xFE,0x07]
digits[5] = [0x03,0x04,0x00,0x02,0x00,0x06]
digits[6] = [0x03,0x06,0x03,0x02,0x00,0x06]
digits[7] = [0x00,0x02,0xFE,0x01,0xFE,0x07]
digits[8] = [0x03,0x02,0x03,0x02,0x00,0x06]
digits[9] = [0x03,0x02,0x00,0x02,0x00,0x06]
digits[0] = [0x03,0x02,0x03,0x01,0x00,0x06]

# Week day short name
weekday_name = {}
weekday_name[0] = "Seg"
weekday_name[1] = "Ter"
weekday_name[2] = "Qua"
weekday_name[3] = "Qui"
weekday_name[4] = "Sex"
weekday_name[5] = "Sab"
weekday_name[6] = "Dom"

#Function to print given clock digit
def print_digit(digit,pos,lcd,rs,lock):
   #Read digit from pre-defined var
   my_digit = digits[digit]

   #Lock display
   lock.acquire()
   try:
      #Print clock digit
      lcd.lcd_write(0x80 + pos)
      lcd.lcd_write(my_digit[0],rs)
      lcd.lcd_write(0x80 + pos + 0x01)
      lcd.lcd_write(my_digit[1],rs)
      lcd.lcd_write(0xC0 + pos)
      lcd.lcd_write(my_digit[2],rs)
      lcd.lcd_write(0xC0 + pos + 0x01)
      lcd.lcd_write(my_digit[3],rs)
      lcd.lcd_write(0x94 + pos)
      lcd.lcd_write(my_digit[4],rs)
      lcd.lcd_write(0x94 + pos + 0x01)
      lcd.lcd_write(my_digit[5],rs)
      #Release display
      lock.release()
   except:
      #In case of eception, release display anyway
      lock.release()

def print_dots(lcd,rs,lock):
   #Lock display
   lock.acquire()
   try:
      #Print clock double dots
      lcd.lcd_write(0xC4)
      lcd.lcd_write(0x3A,rs)
      lcd.lcd_write(0xC9)
      lcd.lcd_write(0x3A,rs)
      #Release display
      lock.release()
   except:
      #In case of eception, release display anyway
      lock.release()

def print_date(local_date,lcd,rs,lock):
    #Lock display
   lock.acquire()
   try:
      #print day / mounth
      lcd.lcd_write(0x8E)
      lcd.lcd_write(0xFE,rs)
      lcd.lcd_write(ord(local_date[0]),rs)
      lcd.lcd_write(ord(local_date[1]),rs)
      lcd.lcd_write(0x2F,rs)
      lcd.lcd_write(ord(local_date[3]),rs)
      lcd.lcd_write(ord(local_date[4]),rs)
      #print four digits year
      lcd.lcd_write(0xCE)
      lcd.lcd_write(0xFE,rs)
      lcd.lcd_write(0xFE,rs)
      lcd.lcd_write(ord(local_date[6]),rs)
      lcd.lcd_write(ord(local_date[7]),rs)
      lcd.lcd_write(ord(local_date[8]),rs)
      lcd.lcd_write(ord(local_date[9]),rs)
      #Clean line used by local data
      lcd.lcd_write(0xA2)
      lcd.lcd_write(0xFE,rs)
      lcd.lcd_write(0xFE,rs)
      lcd.lcd_write(0xFE,rs)
      lcd.lcd_write(0xFE,rs)
      lcd.lcd_write(0xFE,rs)
      lcd.lcd_write(0xFE,rs)
      #Relase display
      lock.release()
   except:
      #In case of eception, release display anyway
      lock.release()

#Function to print local data 
def print_localdata(local_temp,local_ur,lcd,rs,lock):
   #Lock display
   lock.acquire()
   try:
      #print string "Agora"
      lcd.lcd_write(0x8E)
      lcd.lcd_write(0xFE,rs)
      lcd.lcd_write(0x41,rs)
      lcd.lcd_write(0x67,rs)
      lcd.lcd_write(0x6F,rs)
      lcd.lcd_write(0x72,rs)
      lcd.lcd_write(0x61,rs)

      #Print string "T:" plus local temperature plus "o"
      lcd.lcd_write(0xCE)
      lcd.lcd_write(0xFE,rs)
      lcd.lcd_write(0x54,rs)
      lcd.lcd_write(0x3A,rs)
      lcd.lcd_write(ord(local_temp[0]),rs)
      lcd.lcd_write(ord(local_temp[1]),rs)
      lcd.lcd_write(0xDF,rs)

      #Print string "U:" plus local air humidity plus "%"
      lcd.lcd_write(0xA2)
      lcd.lcd_write(0xFE,rs)
      lcd.lcd_write(0x55,rs)
      lcd.lcd_write(0x3A,rs)
      lcd.lcd_write(ord(local_ur[0]),rs)
      lcd.lcd_write(ord(local_ur[1]),rs)
      lcd.lcd_write(0x25,rs)
      #Release display lock
      lock.release()
   except:
      #In case of eception, release display anyway
      lock.release()

#Function to translate given date into week day
def week_day(d):
   if ( strftime("%Y-%m-%d", gmtime()) == d ): return "Hoje"
   temp = datetime.date(int(d.split('-')[0]),int(d.split('-')[1]),int(d.split('-')[2])).weekday()
   return weekday_name[temp]

#Function to translate UV level
def iuv_translator(iuv):
   if (( float(iuv) >= 1 ) and ( float(iuv) <= 2 )): return "Baixo"
   if (( float(iuv) >= 3 ) and ( float(iuv) <= 5 )): return "Moderado"
   if (( float(iuv) >= 6 ) and ( float(iuv) <= 7 )): return "Alto"
   if (( float(iuv) >= 8 ) and ( float(iuv) <= 10 )): return "Muito alto"
   return "Extremo"

#Function to read weather data from CPTEC web site
def parse_xml(location_code):
   #Open HTTP connection
   file = urllib2.urlopen('http://servicos.cptec.inpe.br/XML/cidade/'+location_code+'/previsao.xml')
   #Read xml data from web site
   data = file.read()
   #Close file (connection)
   file.close()
   #Return XML
   return parseString(data)

#Function to read weather data from parsed XML
def get_weather_data(dom,position):
   #Check if position is not grater and 3
   if ( position >= 4 ): return []

   #Read date
   xmlTag = dom.getElementsByTagName('dia')[position].toxml()
   dia=xmlTag.replace('<dia>','').replace('</dia>','')

   #Read weather condition data
   xmlTag = dom.getElementsByTagName('tempo')[position].toxml()
   tempo=xmlTag.replace('<tempo>','').replace('</tempo>','')

   #Read higher expected temperature
   xmlTag = dom.getElementsByTagName('maxima')[position].toxml()
   max=xmlTag.replace('<maxima>','').replace('</maxima>','')

   #Read minor expected temperature
   xmlTag = dom.getElementsByTagName('minima')[position].toxml()
   min=xmlTag.replace('<minima>','').replace('</minima>','')

   #Read UV level
   xmlTag = dom.getElementsByTagName('iuv')[position].toxml()
   iuv=xmlTag.replace('<iuv>','').replace('</iuv>','')

   #Return weather data from given position
   return [dia,tempo,max,min,iuv]

#Function to show current system date
def run_date(lcd,mRs,lock,proc_lock):
   #Create global var entry
   global goodBye
   #Get proclock to prevent local data take display control
   proc_lock.acquire()
   #Get current date from system
   curr_date = strftime("%d/%m/%Y", gmtime())
   #print current date
   print_date(curr_date,lcd,mRs,lock)
   #Release proc lock to make local data display possible
   proc_lock.release()
   # run time until main thread ask to die
   while ( not goodBye ):
      #Release proc lock to make local data display possible
      proc_lock.acquire()
      #Get current date from system
      curr_date = strftime("%d/%m/%Y", gmtime())
      #print current date
      print_date(curr_date,lcd,mRs,lock)
      #Release proc lock to make local data display possible
      proc_lock.release()
      #Wait a while for next iteration
      time.sleep(3)

#Function to show local Temperature and Air Humidity data 
def run_localdata(lcd,mRs,lock,proc_lock):
   #Create global var entry
   global goodBye
   #Initialize local data var
   output = "0 0"
   # run time until main thread ask to die
   while ( not goodBye ):
      #Make that this info will be showed each 15 seconds
      time.sleep(15)
      try:
         #Read sensor data
         output=subprocess.check_output("dht11/dht11", shell=True)
      except:
         #If sensor reading fail, set default local data if it is first thread run
         if ( output == "" ): output = "0 0"
      #Parse local data
      ldata = output.split()
      # get lock to avoid local date take display control
      proc_lock.acquire()
      #Print local data info
      print_localdata(ldata[1],ldata[0],lcd,mRs,lock)
      #Make this info available for 15 seconds
      time.sleep(15)
      #Release display to local date
      proc_lock.release()

#Function to show time
def run_clock(lcd,mRs,lock):
   #Create global var entry
   global goodBye
   #Keep lcd position address to show digits
   cell = {}
   cell[0] = 0x00 #Adress for 1st hour digit
   cell[1] = 0x02 #Adress for 2nd hour digit
   cell[3] = 0x05 #Adress for 1st minute digit
   cell[4] = 0x07 #Adress for 2nd minute digit
   cell[6] = 0x0A #Adress for 1st second digit
   cell[7] = 0x0C #adress for 2nd second digit

   #Set invalid time to force refresh
   prev_time = "AA:AA:AA"

   # run time until main thread ask to die
   while ( not goodBye ):
      #Get current time
      curr_time = strftime("%H:%M:%S", gmtime())
      #Print each time digit (excluding dots) into LCD 
      for pos in [0,1,3,4,6,7]:
         #Check if digit changes since last iteration
         if ( curr_time[pos] != prev_time[pos] ):
            #If digit changes since last refresh, print it again
            print_digit(int(curr_time[pos]),cell[pos],lcd,mRs,lock)
      #update refresh control var
      prev_time = curr_time
      #print dots (grant that it will alway be there)
      print_dots(lcd,mRs,lock)
      #wait for next refresh
      time.sleep(1)

#Function to show weather data
def run_banner(lcd,lock):
   #Create global var entry
   global goodBye
   #Start weather data read control (just to dont read weather data all the time)
   loop_count = 0
   #Initialize xml parse var
   dom = None
   try:
      #Read weather data
      dom = parse_xml("2586")
   #If weather data read fail show error message
   except (urllib2.HTTPError, urllib2.URLError, httplib.HTTPException), e:
      lock.acquire()
      try:
         #Display error message
         lcd.lcd_display_string(("Network Error!").center(20), 4)
         lock.release()
      except Exception, e:
         #grant that lock will be released in case of error
         lock.release()
      #just wait for next read try
      time.sleep(10)
   #Alway run code bellow even exception was found
   finally:
      # run weather data until main thread ask to die
      while ( not goodBye ):
         #Update forecast data only after 150th turn 
         if ( loop_count > 150 ):
            try:
               #Read weather data
               dom = parse_xml("2586")
            #If weather data read fail show error message 
            except (urllib2.HTTPError, urllib2.URLError, httplib.HTTPException), e:
               lock.acquire()
               try:
                  #Display error message
                  lcd.lcd_display_string(("Network Error!").center(20), 4)
                  lock.release()
               except Exception, e:
                  #grant that lock will be released in case of error
                  lock.release()
               #just wait for next read try
               time.sleep(10)
               continue
            #Reset weather data read control
            loop_count = 0
         #Increase weather data read control
         loop_count += 1
         #Parse XML to get weather data
         for position in [0,1,2,3]:
            #Store weather week day
            weather_data = get_weather_data(dom,position)
            text = week_day(weather_data[0]) + ":"
            #Append max and min into week day
            output = (text + "Max " + weather_data[2] + unichr(223) + " Min " + weather_data[3] + unichr(223)).ljust(20)
            #Display min and max data
            lock.acquire()
            try:
               lcd.lcd_display_string(output, 4)
               lock.release()
            except:
               #grant that lock will be released in case of error
               lock.release()
            #wait to show next info
            time.sleep(3)
            #Append UV data into week day
            output = (text + ("UV " + iuv_translator(weather_data[4])).center(20-len(text))).ljust(20)
            #Display UV data
            lock.acquire()
            try:
               lcd.lcd_display_string(output, 4)
               lock.release()            
            except:
               lock.release()
            #wait to show next info
            time.sleep(3)
            #Prepare weather condition data
            start = 0
            end = 20 - len(text)
            weather_now = " " + weather[weather_data[1]]
            #Append weather contition into week day
            output = (text + weather_now[start:(start + end)]).ljust(20)
            #Start weather condition scroll
            lock.acquire()
            try:
               lcd.lcd_display_string(output, 4)
               lock.release()            
            except:
               lock.release()
            time.sleep(1)
            start += 1
            while ( start + end < len(weather_now)+1 ):
               output = (text + weather_now[start:(start + end)]).ljust(20)
               lock.acquire()
               try:
                  lcd.lcd_display_string(output, 4)
                  lock.release()            
               except:
                  lock.release()
               start += 1
               time.sleep(0.2)
            #Wait for show next day info
            time.sleep(0.8)

def main():
   #Constant needed by lcd driver
   mRs = 0b00000001
   #Initialize var to check if threads were initialized
   running = False
   #Array to keep thread process
   my_threads = []
   #Global var to make threads exit
   global goodBye

   #Semaphore to control display usage
   lock = threading.Lock()
   #Semaphore to control display usage between run_localdata and run_date
   proc_lock = threading.Lock()

   #Keep it running forever
   while True:
      #Verify whether i2c display can be detected or not
      p1 = Popen(["/usr/sbin/i2cdetect","-y","1"], stdout=PIPE)
      p2 = Popen(["grep", "20:"], stdin=p1.stdout, stdout=PIPE)
      p1.stdout.close()
      output = p2.communicate()[0]
      p2.stdout.close()
      #Keep display i2c address
      devAddr = output.split()[8]

      #If i2c display was found and threads were not running, start them
      if ((devAddr == "27")  and  (not running)):
         print "Starting threads..."

         try:
            #Load LCD driver
            lcd = lcddriver.lcd()
            #Load user-defined graphs
            lcd.lcd_write(0x40)
            for mycells in ['1','2','3','4','5','6','7','8']:
               for cell in cells[mycells]:
                  lcd.lcd_write(cell,mRs)
            #Clear LCD
            lcd.lcd_clear()
         except:
            #If LCD initialization fails, try again in next loop iteration
            time.sleep(1)
            continue

         #Build thread parameters array
         my_thread_args = {}
         my_thread_args["run_clock"] = (lcd,mRs,lock)
         my_thread_args["run_banner"] = (lcd,lock)
         my_thread_args["run_date"] = (lcd,mRs,lock,proc_lock)
         my_thread_args["run_localdata"] = (lcd,mRs,lock,proc_lock)
         #Build array with functions that threads should run
         my_thread_targets = [run_clock,run_banner,run_date,run_localdata]
         #Builds array with initialized (not running) threads
         my_threads = [threading.Thread(target=my_thread_targets[0], args=my_thread_args["run_clock"]),
                       threading.Thread(target=my_thread_targets[1], args=my_thread_args["run_banner"]),
                       threading.Thread(target=my_thread_targets[2], args=my_thread_args["run_date"]),
                       threading.Thread(target=my_thread_targets[3], args=my_thread_args["run_localdata"])]

         #Start threads
         for th in my_threads:
            th.start()

         #Set running as True
         running = True

      #If i2c display was not found and threads are running, kill them
      if ((devAddr != "27") and (running)):
         #Set global var to make threads die
         goodBye = True
         #Wait until all threads die
         while (my_threads[0].isAlive() or my_threads[1].isAlive() or my_threads[2].isAlive() or my_threads[3].isAlive()):
            for th in [0,1,2,3]:
               if (my_threads[th].isAlive()):
                  print "Thread " + my_thread_targets[th].__name__  + " still alive"
            time.sleep(3)
            print ""
         #When all threads dies, set control var and jump to next loop iteration
         print "All tasks killed!!! lets restart..."
         running = False
         goodBye = False
         continue

      #Just wait a while before start next loop iteration
      time.sleep(5)


if __name__ == '__main__':
   main()

