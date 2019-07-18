import mechanize, re
import os, json
import time
from random import uniform as rand_float

'''
	General methodology behind mechanize is that every browser.action returns an object
	-Response, HTTP of opening or following a submit, link, or open
	
	even though responses can be saved, each browser instance contains only the most Recent URL.
	so you can set values only in the CURRENT http page.
		- however, you can navigate using .back() and .reload()
'''
def HumanCondition(a,b):
	rand = rand_float(a,b)
	print('Human Condition, waiting: ' + str(rand) + ' sec')
	time.sleep(rand)

br = mechanize.Browser()

# HTTP response = Browser window.action
resp = br.open('https://us.etrade.com/e/t/etws/authorize?key=db1ae8b54eb51ea6dea72614a6a8cc4e&token=9WuVU07wu222sgvLj3PRD7v972JrHhPhpgFZstZ2rBE=')

# 'Tab_Window' like attributes
assert br.viewing_html()
print br.title()

# HTTP response attributes
print resp.info()
print resp.read()
print resp.get_data()

str_resp = resp.get_data()

print str_resp[0]

# Human Condition
HumanCondition(7,10)

# Tunnel through html to desired forms
br.select_form(name='log-on-form')
br['USER'] = 'flamingpope'
br['PASSWORD'] = '785754Jf15!'

# Submit login
print br.form
resp2 = br.submit()
print 'submited'

# Lets see where we are now, did the login work?
print resp2.read()
# Cool it did!

# Human Condition
HumanCondition(4,7)

# Now lets press the accept button
# , with eTrade looks like they have two submit buttons
# <form name="CustInfo" method="post" action="/e/t/etws/TradingAPICustomerInfo">
# 1-<input NAME="submit" TYPE="submit" VALUE="Accept">
# 2-<input NAME="submit" TYPE="submit" VALUE="Decline">

br.select_form(name='CustInfo')
resp3 = br.submit(name='submit', label='Accept')

# Read page
print resp3.read()

# Human Condition
HumanCondition(4,7)

# Grab Verification Code, uses regular expressions(re)
str_resp3 = resp3.get_data()

with open('python_data/test_mechanize2.txt','w') as outfile:
	outfile.write(str_resp3)

''' Regular expression for '<input TYPE="text" VALUE="H7ASF' and some random white space character at the end
	<input TYPE="text" VALUE="
	\w{5,5} match exactly 5 alphanumeric 
'''
pattern = re.compile('TYPE="text" VALUE="\w{5,5}')
match = re.findall(pattern, str_resp3)

if not len(match) ==1:
	print'Something wrong occured during Regular Expression parse'

str_code = match[0]
str_code = str_code[-5:]
print str_code


def authorizeToken(requestTokenResponse):
	"""
	Given a dict requestTokenResponse with the temporary oauth_token and oauth_token_secret,
	we generate a login link that a user should interact with to obtain an authCode <str>
	This process is automated with Splinter and pyvirtualdisplay
	"""

	resource_owner_key = requestTokenResponse['oauth_token']
	resource_owner_secret = requestTokenResponse['oauth_token_secret']
	redirect_response = 'https://us.etrade.com/e/t/etws/authorize?key={}&token={}'.format(client_Consumer_Key,resource_owner_key)
	

	# print 'go to this link for authorization:', redirect_response

	# cannot parse redirect_response without a browser because the response is not pure json
	# oauth_response = oauth.parse_authorization_response(redirect_response)

	# Open URL in a new tab, if a browser window is already open.
	# webbrowser.open_new_tab(redirect_response)

	# Display allows the script to run in a linux cloud without a screen
	display = Display(visible=0, size=(1024, 768))
	display.start()


	# create a browser using Splinter library and simulate the workflow of a user logging in
	# various time.sleep(n) is inserted here to make sure login is successful even on slower connections
	with Browser() as browser:
		# Visit URL
		url = redirect_response
		browser.visit(url)
		
		if browser.is_element_present_by_name('txtPassword', wait_time=0):
			
			browser.fill('USER', etrade_settings.username)
			time.sleep(3)


			browser.find_by_name('txtPassword').click()
			
			time.sleep(3)
			# pprint(browser.html)

			browser.fill('PASSWORD', etrade_settings.userpass)
			# Find and click the 'logon' button
			browser.find_by_name('Logon').click()
			time.sleep(3)
			if browser.is_element_present_by_name('continueButton', wait_time=2):
				browser.find_by_name('continueButton').click()

			browser.find_by_value('Accept').click()
			time.sleep(3)
			# authCode = browser.find_by_xpath("//@type='text'").first.value
			authCode = browser.find_by_tag("input").first.value
			time.sleep(3)


	display.stop()
	
	return authCode
