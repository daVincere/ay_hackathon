from flask import Flask, render_template, request, url_for, jsonify, make_response, session, redirect
import docx2txt
import os
import re
import pandas as pd
import csv

app = Flask(__name__, static_url_path='/static')

# @app.route('/')
# def index():
# 	return("GG")

#Upload 1 Route GET
@app.route('/', methods=['GET'])
def uploadform():
	return render_template("uploadform.html")

#Upload 1 Route POST
@app.route('/postform', methods=['POST'])
def postform():
	if request.method == 'POST':
		files_list = request.files.getlist("file[]")
		if(files_list):
			print(files_list)
			#1.
			rawfiles_form16a = form16a_raw(files_list)
			#2.
			rawfiles_16a = rawfiles_to_dict_16a(rawfiles_form16a)
			#3.
			final_dict = create_data(rawfiles_16a)

			print(final_dict)

			# return(to_csv(final_dict))

			return(as_csv("form16a.csv"))

@app.route('/as_csv')    
def as_csv(csvfile):    
    table = pd.DataFrame.from_csv(csvfile)
    return render_template("as_csv.html", data=table.to_html())

def name_of_deductor(s):
	print("1")
	# print("name : ", s.lower().split("name and address of the deductor")[1].split("\n\n")[1])
	# s = s.replace('\n\n', '_')
	# return(s.split('_')[1])
	return((s.lower().split("name and address of the deductor")[1].split("\n\n")[1]))

def amount_on_which_tax_deducted_and_nature_of_payement(s):
	print("2")
	lines = s.split("\n\n")
	tax_line = 0
	total_line = ""
	for i in range(len(lines)):
		if("total (rs.)" in lines[i].lower()):
			total_line = (lines[i].lower().split("total (rs.)")[1])
			tax_line = i
			break
			
	#remove irrelevant characters
	total_line = total_line.replace(' ', '')
	total_line = total_line.replace(',', '')
	
	
	#nature of payement
	nature_of_payement = ""
	
	reference = {}
	reference['193'] = "Interest on Securities"
	reference['194'] = "Dividends"
	reference['194A'] = "Interest other than 'Interest on securities'"
	reference['194D'] = "Insurance commission"
	reference['194DA'] = "Payment in respect of life insurance policy"
	reference['194F'] = "Payments on account of repurchase of units by Mutual Fund or Unit Trust of India"
	reference['194H'] = "Commission or brokerage"
	reference['194I'] = "Rent"
	reference['194K'] = "Income payable to a resident assessee in respect of units of a specified mutual fund or of the units of the Unit Trust of India"
	reference['194LD'] = "TDS on interest on bonds / government securities"
	
	nature_line = lines[tax_line-1]
	nature_key = nature_line.split(' ')[2].upper()
	
	if(nature_key in reference):
		nature_of_payement = (reference[nature_key])
	else:
		nature_of_payement = "Reason not listed"
	
	tax_deducted = float(total_line)
	return(tax_deducted, nature_of_payement)
	
def TAN_of_deductor(s):
	print("3")
	lines = s.split("\n\n")
	TAN = None
	total_line = ""
	n = len(lines)
	_TAN = False
	for i in range(len(lines)):
		if("tan" in lines[i].lower() or  "tan of the deductor" in lines[i].lower()):
			#if TAN in same line
			words = (lines[i].lower().split('tan')[1].split(' '))
			for word in words:
				if(re.match('^(?=.*[a-zA-Z])(?=.*[0-9])', word)): 
#                     print("same line")
					TAN = word
					_TAN = True
					return(TAN.upper())
					
		#if TAN in next line
		elif(TAN is None):
			if("tan" in lines[i].lower() or "tan of the deductor" in lines[i].lower()):
#                 print("next line")
				TAN = (lines[i+1].upper())
				total_line = (line.lower().split("total (rs.)")[1])
				return(TAN.upper())
		else:
			pass

def amount_of_tax_deducted(s):
	print("4")
	
	lines = s.split("\n\n")
	for i in range(len(lines)):
		if("tax deposited / remitted " in lines[i].lower()):
			tax = ((lines[i+2]).split(' ')[2])
			tax = tax.replace(' ', '')
			tax = tax.replace(',', '')
			print("tax : " + str(tax))
			return(float(tax))
		elif("amount of tax deposited/" in lines[i].lower()):
			tax = ((lines[i+3]).split(' ')[2])
			tax = tax.replace(' ', '')
			tax = tax.replace(',', '')
			print("tax : " + str(tax))
			return(float(tax))

def create_data(rawfiles_16a):
	print("5")
	cleaned_list = []
	for file in rawfiles_16a:
		temp_dict = {}

		temp_dict['name_of_deductor'] = name_of_deductor(file['raw_text'])
		temp_dict['TAN_of_deductor'] = (TAN_of_deductor(file['raw_text']))
		temp_dict['amount_of_tax_deducted'] = (amount_of_tax_deducted(file['raw_text']))
		
		
		tax_deducted, nature_of_payment = amount_on_which_tax_deducted_and_nature_of_payement(file['raw_text'])
		temp_dict['amount_on_which_tax_deducted'] = tax_deducted
		temp_dict['nature_of_payment'] = nature_of_payment
		
		
		cleaned_list.append(temp_dict)

	return(cleaned_list)

def form16a_raw(files):
	print("6")
	files_raw = []
	for file in files:
		print(file, " Done")
		if(file.filename.split('.')[1] == "docx"):
			raw_text = docx2txt.process(file)
			files_raw.append(raw_text)

	return(files_raw)

def rawfiles_to_dict_16a(files_raw):
	print("7")
	headers16a = []
	headers16a.append("name and address of the deductor")
	headers16a.append("pan")

	headers = headers16a

	raw_dict_files = []

	for t in files_raw:
		raw_to_dict = {}
		temp = t
		raw_to_dict['raw_text'] = t

		for i in range(len(headers)):
			temp = ""
			if(len(t.split(headers[i])) > 1):
				temp = t.split(headers[i])[1]
				# print((temp))

			if(i < len(headers)-1):
				raw_to_dict[str(headers[i])] = temp.split(headers[i+1])[0]
			else:
				pass
			
		raw_dict_files.append(raw_to_dict)
				
	return(raw_dict_files)

def to_csv(list_of_dict):
	print("8")
	# my data rows as dictionary objects
	mydict = list_of_dict
	 
	# field names
	fields = ['name_of_deductor', 'TAN_of_deductor', 'amount_of_tax_deducted', 'amount_on_which_tax_deducted', 'nature_of_payment']
	 
	# name of csv file
	filename = "/Users/admin/Desktop/form16a.csv"

	# writing to csv file
	with open(filename, 'w', encoding='utf-8') as csvfile:
	    # creating a csv dict writer object
	    writer = csv.DictWriter(csvfile, fieldnames = fields, lineterminator='\n')
	 
	    # writing headers (field names)
	    writer.writeheader()
	 
	    # writing data rows
	    writer.writerows(mydict)

	return("GG")
	 


if __name__ == "__main__":
	app.run(debug=True)