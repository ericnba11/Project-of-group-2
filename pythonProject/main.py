from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time


driver = webdriver.chrome()

driver.get("https://www.google.com/maps/search/%E4%BF%A1%E7%BE%A9%E5%8D%80+%E9%85%92%E5%90%A7/@25.0346723,121.5573764,16z/data=!4m2!2m1!6e5?authuser=0&entry=ttu&g_ep=EgoyMDI0MTAyMS4xIKXMDSoASAFQAw%3D%3D")



driver.close()

