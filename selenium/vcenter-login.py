import sys, os, time
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

sys.stdout.flush()

# Path to Chrome webdriver
dir = os.path.dirname(__file__)
chrome_driver_path = dir + "\chromedriver29.exe"

# Cleanup function
def cleanup():
	driver.close()
	driver.quit()

# Return 0 if elem is fond and 1 if not
def check_element_is_present(elem):
	try:
		driver.find_element_by_tag_name(elem)
	except NoSuchElementException:
		return 1
	return 0

# Return 0 if elem is fond and 1 if not
def check_text_is_present(text):
	try:
		driver.find_element_by_link_text(text)
	except NoSuchElementException:
		return 1
	return 0

#***** START *****

# Starting Chrome browser
#driver = webdriver.firefox()
driver = webdriver.Chrome(chrome_driver_path)
#driver.implicitly_wait(30)
driver.maximize_window()

print ("Starting TEST: Login ...")
time.sleep(5)

# Opening 10.3.199.100 in browser
print ("Loading page https://10.3.199.100 ...")
driver.get("https://10.3.199.100")
print ("Waiting 30 seconds for page to load ...")
time.sleep(30)

# Loop until return is 0
# If "Log in to vSphere Web Client" is found assuming login page is loaded successfully
n = 0
while check_text_is_present(text = "Log in to vSphere Web Client") == 1 and n > 10:
	print ("ERROR: Element is NOT FOUND! Reloading page ...")
	driver.get('https://10.3.199.100')
	print ("Looping around in 30 seconds ...")
	time.sleep(30)
	n+=1

if n == 10:
	print ("FAILED and QUIT")
	cleanup()

#print ("Assuming vSphere Web Client link is present ...")
time.sleep(5)

# Clicking on link
print ("Clicking on vSphere Web Client ...")
link = driver.find_element_by_link_text('Log in to vSphere Web Client')
link.click()
print ("Wating 1 minute for page to load ...")
time.sleep(30)

# Loop until return is 0
# If "iframe" is found assuming login page is loaded successfully
m = 0
while check_element_is_present(elem = "iframe") == 1 and m > 10:
	print ("ERROR: Element is NOT FOUND! Reloading page ...")
	driver.get("https://10.3.199.100/vsphere-client/")
	print ("Looping around in 30 seconds ...")
	time.sleep(30)
	m+=1
print ("Assuming login page is loaded ...")
time.sleep(5)

if m == 10:
	print ("FAILED and QUIT")
	cleanup()

print ("Looking for credential elements ...")
try:
	driver.switch_to_frame(driver.find_element_by_tag_name("iframe"))
	elem1 = driver.find_element_by_xpath("/html/body")
	elem2 = elem1.find_element_by_id("loginForm")
	username = elem2.find_element_by_id("username")
	password = elem2.find_element_by_id("password")
except NoSuchElementException:
	cleanup()

print ("Found login form and now will fill in credentials")
time.sleep(5)

username.send_keys("administrator")
print ("Entered User Name ...")
time.sleep(5)

password.send_keys("administratorPassword")
print ("Entered User Password ...")
time.sleep(5)

# Clicking login and waiting 5 min
clickLogin = elem2.find_element_by_id("submit")
print ("Clicking login button ...")
clickLogin.click()
print ("Waiting 2 minutes for page to load ...")
time.sleep(120)

print ("Redirecting to google.com and preparing to quit")
driver.get("https://www.google.com/")
time.sleep(120)

print ("SUCCESS and QUIT")
cleanup()

#***** END *****
