from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests
import re

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.exchange-rates.org/history/IDR/USD/T')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find_all('div',attrs={'class':'table-responsive'})

#I scrape the table with HTML code table[0]
table1 = table[0]
#the head will form our column names
body = table1.find_all('tr')
#Head values (Column Names) are the first items of the body list
head = body[0] #row 0th will be our header row
body_rows = body[1:] #all other items becomes the rest of the rows
#Now I'm about to iterate through the head HTML code and make list of clean headings

#-Define an empty list to keep column names
headings = []
for item in head.find_all('td'): #loop through all table data 
	#convert the td elements to text and strip "\n"
	item = (item.text).rstrip("\n")
	#append the clean column names to headings
	headings.append(item)
print(headings)

#print (body_rows[0])
all_rows = [] #will be a list for all rows
for row_num in range(len(body_rows)): #a row at a time
	row = [] # this will old entries for one row
    for row_item in body_rows[row_num].find_all("td"): #loop through all row entries
        # row_item.text removes the tags from the entries
        # the following regex is to remove \xa0 and \n and comma from row_item.text
        # \n is the newline and comma separates thousands in numbers
        aa = re.sub("(\n)|,","",row_item.text)
        #append aa to row - note one row entry is being appended
        row.append(aa)
    # append one row to all_rows
    all_rows.append(row)
all_rows

#rearranging the data in orderly manner
all_rows = all_rows[::-1]
all_rows

#change into dataframe
df = pd.DataFrame(data=all_rows, columns = ('Tanggal','Hari','Harga_Harian','Keterangan'))

#insert data wrangling here
df['Harga_Harian1'] = df['Harga_Harian'].str.replace("IDR","")
df['Harga_Harian1'] = df['Harga_Harian1'].astype('float64')
df['Tanggal1'] = df['Tanggal'].astype('datetime64')
df['Hari1'] = df['Hari'].astype('category')
df.drop(columns='Keterangan')
df['Hari1'].cat.categories #turns out days are not ordered properly
ordered_day = ['Monday','Tuesday','Wednesday','Thursday','Friday']
df['Hari1'] = df['Hari1'].cat.reorder_categories(ordered_day)
df['Hari1'].cat.categories #<-the data has been arranged in order

#data visualization
df=df.set_index('Tanggal1')
df.plot()


#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{df["Harga_Harian1"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = df.plot(figsize = (20,9)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)