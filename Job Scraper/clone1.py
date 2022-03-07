import time
from tqdm import tqdm
import sys
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import *
from selenium.webdriver.support.ui import *
import re
import os
import requests
import pandas as pd
import math
from datetime import datetime
import random


class JobScraper:
	FirstLine = True
	ProvinceIndex = 0
	CityIndex = 0
	JobIndex = 0

	## Defining options for chrome browser
	options = webdriver.ChromeOptions()
	#ssl certificate error ignore
	options.add_argument("--ignore-certificate-errors")
	#Adding proxy
	#options.add_argument('--proxy-server=%s' % PROXY)


	Browser = webdriver.Chrome(executable_path = "chromedriver",options = options)

	MainUrl = 'https://www.jeancoutu.com/Carrieres/Recherche.aspx?langtype=3083'

	FileName = "QuebecCityFrenchScrapedData"+str(random.randint(1,9789))+"-"+str(datetime.today().date())+".csv"
	def GetMainData(self):

		#url = 'https://www.jeancoutu.com/Carrieres/RechercheDetail.aspx?posteID=25332'
		#self.Browser.get(url)
		time.sleep(4)


		try:
			ESD = WebDriverWait(self.Browser, 10).until(EC.presence_of_element_located((By.XPATH, "//span[@id='mainContentPlaceHolder_lblDatePrevueVal']"))).text
		except TimeoutException:
			ESD = ''

		try:
			NBH = WebDriverWait(self.Browser, 10).until(EC.presence_of_element_located((By.XPATH, "//span[@id='mainContentPlaceHolder_lblNbrHrsVal']"))).text 
		except TimeoutException:
			NBH = ''
		try:
			TOP = WebDriverWait(self.Browser, 10).until(EC.presence_of_element_located((By.XPATH, "//span[@id='mainContentPlaceHolder_lblTypePosteVal']"))).text 
		except TimeoutException:
			TOP = ''
		try:
			schedule = WebDriverWait(self.Browser, 10).until(EC.presence_of_element_located((By.XPATH, "//span[@id='mainContentPlaceHolder_lblHoraireVal']"))).text 
		except TimeoutException:
			schedule = ''
		try:
			branch = WebDriverWait(self.Browser, 10).until(EC.presence_of_element_located((By.XPATH, "//span[@id='mainContentPlaceHolder_lblPJCNoSucc']"))).text 
		except TimeoutException:
			branch = ''
		try:
			contactus = WebDriverWait(self.Browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='lbl-wrapper-carriere is-desktop-only']"))).text 
		except TimeoutException:
			contactus = ''
		description = ''


		try:
			descriptions = WebDriverWait(self.Browser, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//*[starts-with(@class, 'corpo-job-desc-section')]")))

			for d in descriptions:
				description  += d.text
				lis = d.find_elements_by_tag_name('li')
				for li in lis:
					description = re.sub(r""+li.text, "• "+li.text, description)
		except TimeoutException:
			pass
		try:
			street =  WebDriverWait(self.Browser, 10).until(EC.presence_of_element_located((By.XPATH, "//span[@id='mainContentPlaceHolder_lblSuccAddr']"))).text 
		except TimeoutException:
			street = ''
		try:
			CSZ =  WebDriverWait(self.Browser, 10).until(EC.presence_of_element_located((By.XPATH, "//span[@id='mainContentPlaceHolder_lblSuccCity']"))).text 
			CSZ = CSZ.split(',')
			City = CSZ[0]
			CSZ = CSZ[-1].lstrip().rstrip()
			State = CSZ[0:2]
			Zip = CSZ[2:].lstrip().rstrip()
		except TimeoutException:
			City = ''
			State = ''
			Zip = ''
		currenturl = self.Browser.current_url
		Data_Dict = {
			'Type of Position' : TOP,
			'Scehedule' : schedule,
			'Number of hours' : NBH,
			'Expected start date' : ESD,
			'Branch' : branch,
			'Street' : street,
			'City' : City,
			'State' : State,
			'Zip' : Zip,
			'CDATA' : description,
			'Contact Us' : contactus,
			'Link' : currenturl
		}

		if self.FirstLine == True:

			df = pd.DataFrame([Data_Dict])
			df.to_csv(self.FileName,index=False,encoding='utf-8-sig')
			self.FirstLine = False
		else:

			df = pd.DataFrame([Data_Dict])
			df.to_csv(self.FileName,index=False, mode='a',header=False,encoding='utf-8-sig')


		BackButton = WebDriverWait(self.Browser, 15).until(EC.element_to_be_clickable((By.XPATH, "//a[@class='btn-cta']")))

		BackButton.click()


	def GetCityDropDown(self):
		#Finding City drop down element
		CityDropDown = Select(WebDriverWait(self.Browser, 15).until(EC.element_to_be_clickable((By.ID, 'mainContentPlaceHolder_ddlCity'))))

		#All options present in city dropdown
		CityDropDownOptions = CityDropDown.options
		#it there are items
		if(len(CityDropDownOptions) == 1):
			#let page load
			time.sleep(3)
			#Finding city drop down element again to avoid stale element exception
			CityDropDown = Select(WebDriverWait(self.Browser, 15).until(EC.element_to_be_clickable((By.ID, 'mainContentPlaceHolder_ddlCity'))))


			CityDropDownOptions = CityDropDown.options

		for c in range(len(CityDropDownOptions)):
			if(self.CityIndex == c):

				CityDropDown = Select(WebDriverWait(self.Browser, 15).until(EC.element_to_be_clickable((By.ID, 'mainContentPlaceHolder_ddlCity'))))

				print("Search for City : "+CityDropDown.options[c].text)

				if(c > 0):

					try:
						CityDropDown.select_by_index(c)
					except NoSuchElementException:

						spinner = self.Browser.find_elements_by_xpath("//div[@class='overlay-mask']")
						if(spinner):
							spinner = spinner[-1].get_attribute('style')
							print(spinner)
							while spinner == "display: block; position: fixed;":
								time.sleep(5)
								spinner = self.Browser.find_elements_by_xpath("//div[@class='overlay-mask']")
								spinner = spinner[-1].get_attribute('style')

						time.sleep(2)
						CityDropDown = Select(WebDriverWait(self.Browser, 15).until(EC.element_to_be_clickable((By.ID, 'mainContentPlaceHolder_ddlCity'))))
						CityDropDown.select_by_index(c)

					time.sleep(4)																						
					#finding jobs after selecting city
					Jobs = WebDriverWait(self.Browser, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//*[contains(@id, 'mainContentPlaceHolder_repPostesOfferts_lnkPoste_')]")))
					JobLen = len(Jobs)
					#iterating through all the jobs
					for j in range(len(Jobs)):
						#finding job element again to avoid stale element exception
						Jobs = WebDriverWait(self.Browser, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//*[contains(@id, 'mainContentPlaceHolder_repPostesOfferts_lnkPoste_')]")))
						#if(self.JobIndex == i):
						#Click on job text 
						Jobs[j].click()
						#This function will scrape all the data we need
						self.GetMainData()
						time.sleep(2)
						#These two function will select item from dropdown again as the page resets
						self.SelectFromProvinceDropDown()
						self.SelectFromCityDropDown()
						
						self.JobIndex = j + 1
						print("Jobs Searched: "+str(j+1)+"Out of "+str(JobLen))
				self.CityIndex = c + 1


	def SelectFromCityDropDown(self):
		try:
			CityDropDown = Select(WebDriverWait(self.Browser, 15).until(EC.element_to_be_clickable((By.ID, 'mainContentPlaceHolder_ddlCity'))))	
			CityDropDown.select_by_index(self.CityIndex)
		except NoSuchElementException:
			spinner = self.Browser.find_elements_by_xpath("//div[@class='overlay-mask']")
			if(spinner):
				spinner = spinner[-1].get_attribute('style')
				print(spinner)
				while spinner == "display: block; position: fixed;":
					time.sleep(5)
					spinner = self.Browser.find_elements_by_xpath("//div[@class='overlay-mask']")
					spinner = spinner[-1].get_attribute('style')

			time.sleep(2)
			CityDropDown = Select(WebDriverWait(self.Browser, 15).until(EC.element_to_be_clickable((By.ID, 'mainContentPlaceHolder_ddlCity'))))	
			print(len(CityDropDown.options))
			CityDropDown.select_by_index(self.CityIndex)
		finally:
			time.sleep(4)					



	def SelectFromProvinceDropDown(self):
		try:
			ProvinceDropDown = Select(WebDriverWait(self.Browser, 15).until(EC.element_to_be_clickable((By.ID, 'mainContentPlaceHolder_ddlProvinces'))))
			ProvinceDropDown.select_by_index(self.ProvinceIndex)
		except NoSuchElementException:

			spinner = self.Browser.find_elements_by_xpath("//div[@class='overlay-mask']")
			if(spinner):
				spinner = spinner[-1].get_attribute('style')
				while spinner == "display: block; position: fixed;":
					time.sleep(5)
					spinner = self.Browser.find_elements_by_xpath("//div[@class='overlay-mask']")
					spinner = spinner[-1].get_attribute('style')


			ProvinceDropDown = Select(WebDriverWait(self.Browser, 15).until(EC.element_to_be_clickable((By.ID, 'mainContentPlaceHolder_ddlProvinces'))))
			ProvinceDropDown.select_by_index(self.ProvinceIndex)
		finally:
			time.sleep(4)
	def Search(self):
		self.Browser.get(self.MainUrl)
		time.sleep(3)

		#Searching for Province DropDown
		ProvinceDropDown = Select(WebDriverWait(self.Browser, 15).until(EC.element_to_be_clickable((By.ID, 'mainContentPlaceHolder_ddlProvinces'))))

		#all options present in Province DropDown
		ProvinceDropDownOptions = ProvinceDropDown.options


		#this will iterate all options of province dropdown
		for i in range(len(ProvinceDropDownOptions)):
			if(self.ProvinceIndex == i):

				ProvinceDropDown = Select(WebDriverWait(self.Browser, 15).until(EC.element_to_be_clickable((By.ID, 'mainContentPlaceHolder_ddlProvinces'))))
				print(ProvinceDropDown.options[i].text)
				if("Québec" in ProvinceDropDown.options[i].text):
					#log
					print("Search for Province : "+ProvinceDropDown.options[i].text)
					#if option is not 0 or 1 which is Default
					if(i > 0):

						try:
							#Select Province by its index number if error
							ProvinceDropDown.select_by_index(i)
						except NoSuchElementException:
							#exception 
							#spinner : loading div which will be in play if page is loading
							spinner = self.Browser.find_elements_by_xpath("//div[@class='overlay-mask']")
							#if there is spinner
							if(spinner):
								spinner = spinner[-1].get_attribute('style')
								#check if its style attribute has display none or block (If its block run while loop till its None Display : None)
								while spinner == "display: block; position: fixed;":
									time.sleep(5)
									spinner = self.Browser.find_elements_by_xpath("//div[@class='overlay-mask']")
									spinner = spinner[-1].get_attribute('style')
							#Check for province drop down element to avoid stale element exception 
							ProvinceDropDown = Select(WebDriverWait(self.Browser, 15).until(EC.element_to_be_clickable((By.ID, 'mainContentPlaceHolder_ddlProvinces'))))
							#selecting item by index
							ProvinceDropDown.select_by_index(i)

						time.sleep(4)
						self.GetCityDropDown()

				self.ProvinceIndex = i + 1


	
    



a = JobScraper()

a.Search()
#a.GetMainData()