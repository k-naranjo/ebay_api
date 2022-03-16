#!/usr/bin/env python
# coding: utf-8

# ### **Getting Data from eBay**  <a class="anchor" id="chapter3"></a>
# 
# #### **Introduction to the eBay Data Pipeline** <a class="anchor" id="section_3_1"></a>
# 
# In this chapter, we will provide a detailed overview of the implementation of a data pipeline. This process begins by collecting keys from eBay’s Developer Program, and ends in a cleaned data frame that is connected to a SQLite database.  Figure 3 provides a holistic overview of our data pipeline process. Orange elements within the inner rectangle are applied to each category in our predefined <code>categories_list</code>. The looping structure of the flowchart represents the automated nature of this entire process, which runs once every 24 hours. We start by loading in the developer keys provided by eBay and connecting to their API system. These keys are unique to each user and should be stored in a hidden .env file as a prerequisite of the loading process. The .env file resides in the same directory as our main code files. It is important to not share your keys with anyone!
#  
# Once we gain access to eBay’s API system, we define the <code>geteBay</code> function. This function intakes a category number as an input, and subsequently connects to and makes GET request calls to the Finding API. This function must be defined before the iterative process described below can be completed.
#  
# Once the  <code>geteBay</code> function  has been defined, we iteratively loop over each of the categories in <code>categories_list</code>, and each element is passed through the <code>geteBay</code> function. The <code>geteBay</code> function contains loops that extracts each of the desired features and cleans the associated data for each listing. The cleaned data is then stored in a new data frame.
#  
# After the cleaned data frame is generated, we extract the <code>Item_ID</code> for each listing and use the resulting list as an input parameter to our second API connection with the Shopping API. The subsequent GET request calls allows us to mine further features of interest for each of the listings:
# 
# - <code>category_id</code>
# - <code>item_specs</code>
# - <code>item_idlist</code>
# - <code>seller_id</code>
# - <code>Item_sku</code> 
# - <code>image_url</code>
# 
# Next, we merge the processed data from the Finding and Shopping APIs into a single data frame called <code>item_specs</code>.
#  
# We then connect to our SQL database, ebay.db, and listings in the newly merged <code>item_specs</code> data frame are appended to the item_specs table. Once the new data has successfully been appended to the database table, all changes are saved and the connection to the database is closed. This process then repeats the following day at 12.05am.
# 
# *figure 3.*
# 
# <img src="2_flowchart.jpg" width=1000 height=1200 />
# 
# **Caption:** This flowchart represents the overall automated data collection process that we built. The inner box indicates a comprehensive process to collect for each category. Then, the data is concatenated and the collection process is automated each 24 hours

# ##### **Flask App** <a class="anchor" id="section_3_2_1"></a>
# 
# **Building a Simple App**
# 
# Getting access to eBay’s developer’s program requires users to build their own application. This requirement is a result of eBay’s marketplace account <a href="https://developer.ebay.com/marketplace-account-deletion"> deletion notification update </a>. The resulting application provides eBay with a communication channel to notify developers of marketplace deletion notifications. The architecture the application requires is relatively simple – it needs to receive eBay challenge code and respond with an output that hashes together the challenge code, the user’s eBay verification token, and the application’s endpoint. A 200 response should be produced in an output field in JSON format. An application that meets these requirements can be constructed in python using the flask package.
# 
# It should be reiterated that creating an application that can successfully receive challenge code is essential to accessing eBay’s production data. Production data consists of real listings from live marketplaces. Users can also develop test code to interact with eBay’s API system through their Sandbox environment.
# 
# ```python
# ```
# 
# The Flask application must be able to manage Hyper Text Transfer Protocol Secure (HTTPS) requests. HTTPS is the secure version of HTTP, the protocol over which data is sent between two applications. The method we used to get an https connection was through letsencrypt.com, which is a third-party website that provides a certificate to most hosted websites. The user needs to purchase a domain name in order to obtain an SSL certificate. Domains can be purchased through godaddy, Google domains, or other websites. There is no restriction on extensions. For example, we used a .club extension due to its low set up cost. After securing an SSL hosted domain for the application, login to eBay’s developer’s program and apply for Production Keys. Once Production Keys are obtained, you are ready to start building your data pipeline.
# 
# For help on troubleshooting setting up a Flask app, look into UVA IT and various online resources including  <a href="https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-20-04">this tutorial</a>. The flask package also has documentation that can be accessed at <a href="https://flask.palletsprojects.com/en/2.0.x/">this link</a>.
# 

# #### **Navigating through the Code** <a class="anchor" id="section_3_2"></a>
# 
# This section is meant to provide a general overview of the code in our main data mining and processing script. To help reinforce user understanding, we have included images of code blocks, which we reference throughout this tutorial.
# 
# As with any python script, we will begin by importing the necessary packages and loading the API keys into our environment. Notice that <code>categories_of_interest</code> is imported from another .py file, <code>CategoryList_Input</code>. This file resides in the same directory as our main .py file, and provides a method for our sponsors to freely modify categories of interest without interfacing with the main script. We will directly reference where some specific packages are used in the script. After loading in our account-specific keys, an initial connection is made to the eBay API system. This establishes a general connection to eBay’s APIs. When accessing specific APIs to extract features of interest, we will have to establish other connections.  
# 
# We also define a datetime object to collect data from a timeframe of interest. For our project, we want to collect data from the last 24 hours, so the datetime function sets a timeframe for the previous day.
# 
# ```python
# import pandas as pd
# import numpy as np
# import os
# import requests
# import dotenv
# import json
# import base64
# from matplotlib import pyplot as plt
# import seaborn as sns
# from datetime import datetime, date, timedelta
# import xmltodict
# from collections import OrderedDict
# import hashlib
# import traceback
# 
# import sqlite3
# import os
# import time 
# 
# #import categories list, make sure file is in same directory
# from CategoryList_Input import categories_of_interest
# 
# #set up API
# dotenv.load_dotenv('keys.env')
# 
# AppID = os.getenv('AppID')
# DevID = os.getenv('DevID')
# CertID = os.getenv('CertID')
# 
# s = AppID + ':' +CertID
# encoded = base64.b64encode(s.encode('UTF-8'))
# 
# url = 'https://api.ebay.com/identity/v1/oauth2/token'
# 
# headers = {'Authorization': 'Basic ' + str(encoded.decode("utf-8")),
#           'Content-Type': 'application/x-www-form-urlencoded'}
# 
# params = {'grant_type':'client_credentials',
#          'scope': 'https://api.ebay.com/oauth/api_scope'}
# 
# r = requests.post(url, headers=headers, params=params)
# r
# ```
# 
# The architecture of our extraction and processing pipeline is encapsulated in a try block. We implement a try-except block in case the pipeline runs into any errors. At the end of this script, we discuss what the except blocks we implement catch. The try block runs the code, and execution only jumps to the except block if there are any errors.
# 
# We collect the corresponding data through a function we defined as <code>geteBay</code>. This function uses the Finding API to collect our initial set of features discussed in chapter 2. The automated nature of our data collection also stems from this section as we collect data from the past day of listings. The <code>geteBay</code> function parses through a list of predefined categories. This function also takes a <code>starttime</code> parameter that specifies the earliest time to collect listings from.
#  
# The url and headers objects are used to authenticate the connection to the Finding API and its <code>findItemsByCategory</code> function. We also initialize <code>categorydf</code> dataframe that will append data to <code>item</code>. Next, we create a <code>params</code> object that defines the output of the API call. This includes the category ID,  entries per page, number of pages, and listing time. Finally, we call the API with the constructed parameters. 
# 
# ```python
# 
# try:
# 
#     #Functions that collect data
#     def geteBay(categoryid, starttime):
# 
#         url = 'https://svcs.ebay.com/services/search/FindingService/v1'
#         headers = {'X-EBAY-SOA-SECURITY-APPNAME': AppID,
#                    'X-EBAY-SOA-OPERATION-NAME': 'findItemsByCategory'}
# 
#         categorydf = pd.DataFrame()
# 
#         for i in range(1,2):
#             params = {'categoryId': categoryid,
#                      'RESPONSE-DATA-FORMAT':'JSON',
#                      'paginationInput.entriesPerPage':100, #100 entries per page
#                      'paginationInput.pageNumber':i,
#                      'findItemsByCategoryRequest.sortOrder':'StartTimeNewest',
#                       'itemFilter(0).name': 'StartTimeFrom',
#                       'itemFilter(0).value': starttime}
#             r = requests.get(url, headers=headers, params=params)
# 
# ```
# 
# If the call to the API returns empty, the for loop will skip over the page of listings it is currently iterating over without throwing an error. Data collected from the API call is then converted to tabular format and appended to a data frame. 
# 
# ```python
#             if 'item' not in pd.json_normalize(json.loads(r.text)['findItemsByCategoryResponse'][0]['searchResult'][0]):
#                 continue 
#             categorydf = categorydf.append(pd.json_normalize(json.loads(r.text)['findItemsByCategoryResponse'][0]['searchResult'][0]['item']))
# 
#         categorydf = categorydf.reset_index()
# 
# ```
# 
# The data contained within <code>categorydf</code> is not uniform and still needs to be processed. To tackle this issue, we implement the following algorithmic method for each feature: initialize an empty list, iterate over the length of the dataframe, verify that the feature exists, extract key elements of the uncleaned data, and append processed results to the empty list. Each of the lists will later be combined into a cleaned dataframe. If a row has a missing value, we assign <code>nan</code> to indicate this. This is to ensure that all features have the same number of elements.
# 
# ```python 
#      itemlist = []
#         for i in range(0, len(categorydf)): #loop over range of categorydf
#             if 'itemId' in categorydf:
#                 item = categorydf.itemId[i][0]
#             else:
#                 item = 'nan'
#             itemlist.append(item)
# 
#         #title
#         titlelist = []
#         for i in range(0, len(categorydf)):
#             if 'title' in categorydf:
#                 title = categorydf.title[i][0]
#             else: 
#                 title = 'nan'
#             titlelist.append(title)
# 
#         #viewitemurl
#         urllist = []
#         for i in range(0, len(categorydf)):
#             if 'viewItemURL' in categorydf:
#                 url = categorydf.viewItemURL[i][0]
#             else: 
#                 url = 'nan'
#             urllist.append(url)
# 
#         #postalcode
#         postallist = []
#         for i in range(0, len(categorydf)):
#             if 'postalCode' in categorydf:
#                  code = categorydf.postalCode[i]
#             else:
#                  code = 'nan'
#             postallist.append(code)
# 
#         postal = []
#         for i in postallist:
#             if type(i) == list:
#                 postal.append(i[0])
#             else:
#                 postal.append("nan")
# 
# 
#         #country
#         countrylist = []
#         for i in range(0, len(categorydf)):
#             if 'country' in categorydf:
#                 a = categorydf['country'][i][0]
#             #print(a)
#             else:
#                 a = 'nan'
#             countrylist.append(a)
# 
#         #priceselling
#         pricelist = []
#         for i in range(0, len(categorydf)):
#             if 'sellingStatus' in categorydf:
#                 price = categorydf.sellingStatus[i][0]['convertedCurrentPrice'][0]['__value__']
#             else:
#                 price = 'nan'
#             pricelist.append(price)
# 
#         #condition
#         conditionlist = []
#         for i in range(0, len(categorydf)):
#             if 'condition' in categorydf:
#                 a = categorydf['condition'][i]
#             else: 
#                 a = 'nan'
#             conditionlist.append(a)
# 
#         #listingtime
#         listingtime = []
#         for i in range(0, len(categorydf)):
#             if 'listingInfo' in categorydf:
#                 a = categorydf['listingInfo'][i][0]['startTime'][0]
#             else:
#                 a = 'nan'
#             listingtime.append(a)
# 
# ```
# 
# **Note:** Extracting the postal code for each listing presents a special case for the methodology described in the previous paragraph. Specifically, the output of <code>postallist</code> contains a mix of sub lists and placeholders for empty values. Heterogeneous data types are an issue, so we implement an additional processing step – if the data type of the extracted element is a list, we take the first element. This corresponds to the desired postal code value. Otherwise, we replace the placeholder value with “nan” in string format.
# 
# ```python 
#         postal = []
#         for i in postallist:
#             if type(i) == list:
#                 postal.append(i[0])
#             else:
#                 postal.append("nan")
# 
# ```
# 
# After processing all features of interest, we create <code>categorydf_clean</code> data frame from a dictionary of lists. This data frame contains the processed data for each feature. The function outputs the cleaned data frame. 
# 
# ```python
#         categorydf_clean = pd.DataFrame({'Item_ID': itemlist,
#                                          'Product_Title':titlelist,
#                                          'URL_image':urllist,
#                                          'Country':countrylist,
#                                          'Price_USD':pricelist,
#                                          'Postal_Code': postal,
#                                          'Item_Condition':
#                                          conditionlist,
#                                          'Listing_Time':listingtime})
# 
#         return categorydf_clean
# 
# ```
# 
# The <a href="https://stackoverflow.com/questions/56494304/how-can-i-do-to-convert-ordereddict-to-dict "> <code>OrderedDict_to_dict()</code> </a>  function is defined to help change the data type for inputs that happened to be an ordered dictionary. Converting an ordered dictionary to a dictionary allows us to parse through data in the same method discussed above. 
# 
# ```python
# 
#  def OrderedDict_to_dict(arg):
#         if isinstance(arg, (tuple, list)): 
#             return [OrderedDict_to_dict(item) for item in arg]
# 
#         if isinstance(arg, OrderedDict): 
#             arg = dict(arg)
# 
#         if isinstance(arg, dict): 
#             for key, value in arg.items():
#                 arg[key] = OrderedDict_to_dict(value)
# 
#         return arg
# ```
# 
# This code block changes the directory of the collected data to the location of the database subdirectory and connects to it, using the SQLite library.
# 
# ```python 
# 
#     os.chdir('/gpfs/gpfs0/project/sdscap-kropko/sdscap-kropko-network')
#     ebay_db = sqlite3.connect("ebay.db")
# ```
# 
# Here we loop through the list of categories. It starts by calling the <code>geteBay</code> function and passing the current category. This will collect the results from the last 24 hours and save them to a dataframe, <code>finding_df</code>.
#  
# We also initialize an empty list and loop through the <code>finding_df</code> to extract the item IDs.
# 
# ```python
# 
#     categories_list = categories_of_interest
#     
#     for cat in categories_list:
#         finding_df = geteBay(cat, oneday)
# 
#         itemlist = []
#         for i in range(0, len(finding_df['Item_ID'])):
#             item = finding_df['Item_ID'][i]
#             itemlist.append(item)
# 
# ```
# 
# We create a <code>new_list</code> that segments elements in the item ID list into groups of 20. Generating a list of lists in this format allows us to maximize the number of possible calls  we can make to the Shopping API - in this case, it’s 5,000 API calls per day.  Next, we set up the parameters to connect to the Shopping API and initialize an empty data frame; this process mirrors connecting to the Finding API.
#  
# In a <code>for loop</code> we iterate through each sublist in  <code>new_list</code> and reduce the sub list’s elements into one string that contains all of the listing IDs. We pass this string to the <code>GetMultipleItems</code> and explicitly state that we want features from the following call-specific output fields: <code>Variations, Details, ItemSpecifics</code>.
#  
# We complete the call to the API and convert XML output into a dictionary, and save it in a data frame.
# 
# ```python
# 
#         new_list = [itemlist[i:i + 20] for i in range(0, len(itemlist), 20)]
# 
#         root = 'https://open.api.ebay.com'
#         endpoint = '/shopping'
#         headers = {'X-EBAY-API-IAF-TOKEN': 'Bearer ' + OAuth,
#                   'Content-Type': 'application/x-www-form-urlencoded',
#                   'Version': '1199'}
# 
#         getmultipledf = pd.DataFrame()
#         for eachlist in new_list:
#             string_listingids = ','.join(eachlist)
#             params = {'callname':'GetMultipleItems',
#                     'ItemID': string_listingids,
#                     'IncludeSelector':'Variations,Details,ItemSpecifics'}
#             r = requests.get(root+endpoint, headers=headers, params=params)
#             xml_format = xmltodict.parse(r.text)
#             getmultipledf =getmultipledf.append(pd.json_normalize(OrderedDict_to_dict(xml_format)))
# 
# ```
# 
# 
# For each iteration, we check to see if <code>GetMultipleItemsResponse.Item</code> is a valid feature in <code>getmultipledf</code>. If the feature does not exist, we skip that iteration and continue the for-loop. Then, we initialize empty lists for features of items collected by the Shopping API. All variables of interest are stored in the single column <code> GetMultipleItemsResponse.Item</code >, so we make a copy of this feature and assign it to <code>convert_list</code>. We then convert any instances of float values in <code>convert_list</code> into lists. This is a necessary processing step because we are going to iterate across the length of convert_list, and len() cannot be applied to objects with a float data type. 
# 
# Once every float instance has successfully been converted to a list, <code>convert_list</code> is handed off to another recursive loop that will extract additional item-related features. Each of these values is saved to the corresponding lists:
# 
# - item_specs
# - item_idlist
# - seller_id
# - item_sku
# - image_url
# - category_id
# 
# 
# ```python
# 
#             for j in range(0, len(convert_list)): #loop over length of convert_list
#             
#             #skip empty elements
#             if type(convert_list[j]) == float:
#                 continue
#             
#             for i in range(0, len(convert_list[j])):
#                 a = getmultipledf['GetMultipleItemsResponse.Item'][j][i]['PrimaryCategoryID'] 
#                 category_id.append(a)
# 
#             for i in range(0, len(convert_list[j])):
#                 a = getmultipledf['GetMultipleItemsResponse.Item'][j][i]['ItemSpecifics']['NameValueList']
#                 item_specs.append(a)
# 
#             for i in range(0, len(convert_list[j])):
#                 a = getmultipledf['GetMultipleItemsResponse.Item'][j][i]['ItemID']
#                 item_idlist.append(a)
# 
#             for i in range(0, len(convert_list[j])):
#                 a = getmultipledf['GetMultipleItemsResponse.Item'][j][i]['Seller']['UserID']
#                 m = hashlib.sha256(a.encode('utf8'));
#                 seller_id.append(m.hexdigest())
# 
#             for i in range(0, len(convert_list[j])):
#                 a  = getmultipledf['GetMultipleItemsResponse.Item'][j][i].get('SKU')
#                 item_sku.append(a)
# 
#             #images 
#             all_picture_urls = []
#             for i in range(0, len(convert_list[j])):
#                 if isinstance(getmultipledf['GetMultipleItemsResponse.Item'][j][i]['PictureURL'], list):
#                     all_picture_urls.append(getmultipledf['GetMultipleItemsResponse.Item'][j][i]['PictureURL'])
#                 else:
#                     converted_to_list = [getmultipledf['GetMultipleItemsResponse.Item'][j][i]['PictureURL']]
#                     all_picture_urls.append(converted_to_list)
# 
#             for i in range(0, len(all_picture_urls)):
#                 a = all_picture_urls[i][0]
#                 image_url.append(a)
#                 
# ```
# We combine the two cleaned data frames generated from making calls to the Finding and Shopping APIs.  Moreover, we convert the data type of  <code>Item_Condition</code>,<code>Listing_Time</code>, and <code>itemspeclist</code> to strings in order to save these columns and their corresponding values to our SQLite database. SQLite databases cannot handle datetime data types and dictionaries within a specific cell.  
# 
# 
# ```python
#         shopping_df = pd.DataFrame({'itemspeclist': item_specs,
#                                'itemid': item_idlist,
#                                'sellerid':seller_id,
#                               'sku':item_sku,
#                               'image_url':image_url,
#                                    'categoryid': category_id})
# 
#         item_specs = pd.DataFrame({'ItemID':finding_df['Item_ID'],
#                                   'Product_Title':finding_df['Product_Title'],
#                                   'CategoryID':shopping_df['categoryid'],
#                                   'Price':finding_df['Price_USD'],
#                                   'Item_Condition': finding_df['Item_Condition'].astype('str'),
#                                   'Listing_Time':finding_df['Listing_Time'].astype('str'),
#                                   'Item_Specifics':shopping_df['itemspeclist'].astype('str'),
#                                   'Seller_ID':shopping_df['sellerid'],
#                                   'Country':finding_df['Country'],
#                                   'Zip_Code':finding_df['Postal_Code'],
#                                   'Image_URL':shopping_df['image_url'],
#                                   'SKU':shopping_df['sku']})
# ```
# 
# In this code block, we add the current data to the SQLite database, commit the changes, and close the connection.
# 
# 
# ```python
# 
#     item_specs.to_sql("item_specs", ebay_db, index=False, chunksize=1000, if_exists="append")
#     ebay_db.commit()
#     ebay_db.close()
# 
# 
# ```
# 
# 
# These are the except blocks that we implement to account for any errors in our script. The first except block catches any instance of a connection error. The second block is a catch-all for any other errors our script may generate. The code block will generate a log file that stores the name of the error, the traceback message and the current category ID iteration that caused the error. Finally, as a fail-safe, we commit and close the database in these blocks, so any successfully cleaned rows prior to the error are saved.
# 
# 
# ```python
# 
# except ConnectionError:
#     print("A connection error occurred!")
#     
#     
# except Exception as e:
#     categoryerror = item_specs.CategoryID.iloc[-1] #extracts most recent CategoryID
#     
#     with open('Ebay_Script_Log.txt', 'w') as f: #w will overwrite existing content in the log.txt file
#         f.write(str(e))
#         f.write(traceback.format_exc())
#         f.close()
#     print("Something other than a ConnectionError happened")
#     print("Error occured at category " + str(categoryerror))
#     #Troubleshooting:
#     #Check result.out file first, see if something happened 
#     #If something happened, check Ebay_Script_Log.txt file to see traceback message 
#     
#     ebay_db.commit()
#     ebay_db.close()
#     
# 
# ```

# #### **Slurm File** <a class="anchor" id="section_3_3"></a>
# 
# We use a batch script to automate the data collection process. Sbatch submits a batch script to Slurm where we can run the file name of interest that contains our script to collect data. This slurm file should have the extension slurm_file_name.slurm. Setting up the slurm script to run on a daily basis requires several parameters listed below. These options and their use cases that can be added to the body of the slurm file in order to customize its functionality. 
# 
# <code>#SBATCH --begin=00:05</code>
# The --begin parameter sets the start time you want the job to run. In this example, this initiates the job at 12.05am 
# 
# 
# <code>BATCH --output=result.out</code>
# This is the file you specify in which to store the job output.
# 
# <code>#SBATCH -p standard</code>
# This parameter specifies the partition/queue in which to run the job.
# 
# <code>#SBATCH -A "<account>"</code>
#     
# Since we are running this slurm job on a high performance computing system, this specifies the account to be charged when submitting the job. 
#     
# <code>#SBATCH -t 03:00:00</code>    
# The -t parameter sets the time limit for which the job will stop running. For this wall clock time limit, the job will run for a maximum of 3 hours. 
#     
# <code>#SBATCH --mail-type=fail</code>
# This parameter notifies the associated mail-user by email when a failed event type occurs.
#     
# <code>#SBATCH --mail-user= <user "email address"></code>
# This specifies the user’s associated email address to be notified when a failed event type occurs.
# 
# *Figure 3.*
# 
# <img src="fig3.jpg" width=1000 height=1200 />
#     
# 
#     
# Once the parameters of the slurm script is set, the next step is to set up the job to run. To set this up, navigate to the folder/directory that contains the slurm script. This can be accomplished by opening a terminal (via file > new > terminal on Rivanna) and checking to see if the <code>pwd</code> (present working directory) matches the location of interest. To navigate to the correct directory use type in cd followed by the location of interest. After making sure you are in the correct directory, type the function “sbatch slurm_file_name.slurm”. Hit enter, and if successful, the following message should appear “submitted batch job [number]”. 
# 
# There are several terminal commands that can check the status of a slurm job. These commands are listed below:
# 
# <code>scontrol show [job number]</code>
# - Lists detailed information for a job (useful for troubleshooting)
# - The job number will change every 24 hours 
#     
# <code>squeue –start</code> List all current jobs
#     
# <code>squeue -u <username> </code> List all running jobs for a user
# 
# <code>scancel <jobid></code> Cancel a single job 
# 
# For more information about slurm files and scheduling these jobs, check out these following websites <a href=" https://slurm.schedmd.com/pdfs/summary.pdf"> Cheat sheet Slurm Workload Manager </a> , <a href=" https://docs.rc.fas.harvard.edu/kb/convenient-slurm-commands/">Convenient SLURM Commands</a>, and  <a href=" https://slurm.schedmd.com/sbatch.html "> Slurm Documentation </a>
# 
# 

# In[ ]:




