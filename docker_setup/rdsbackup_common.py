import os
import time
import datetime
import base64
import sys
from shutil import rmtree
from configparser import ConfigParser
# from yaml import dump
from azure.storage.blob import BlobServiceClient , BlobClient

parser = ConfigParser()
parser.read('database.config')
ts = time.gmtime()
print(time.strftime("%Y-%m-%d %H:%M:%S", ts))
 
ignore = ['.DS_Store']

# used for taking input from database_config file.
# hostEndpoint = str(parser.get('database_config', 'endpoint'))

# used for taking input from jekins 
hostEndpoint = os.getenv("DATABASE_HOST_PROD")
hostEndpoint = str(base64.b64decode(hostEndpoint))
hostEndpoint = hostEndpoint[2:]
hostEndpoint = hostEndpoint[:-1]

# used for taking input from database_config file.
# user= str(parser.get('database_config', 'username'))

# used for taking input from jekins 
user = os.getenv("DATABASE_USERNAME_PROD")
user = str(base64.b64decode(user))
user = user[2:]
user = user[:-1]

db_config = {
    'host': hostEndpoint,
    'user': user,
    'pwd': "",
}

# used for taking input from database_config file.
# password_db= str(parser.get('database_config', 'password'))

# used for taking input from jekins 
password_db = os.getenv("DATABASE_PASSWORD_PROD")
key = str(base64.b64decode(password_db))
key = key[2:]
key = key[:-1]

# Azure connection string 
# used for taking input from database_config file.
# connectionString = str(parser.get('azure_storage_config', 'azure_storage_connection_string'))

# used for taking input from jekins 
connectionString = os.getenv("AZURE_STORAGE_CONNECTION_STRING_PROD")
connectionString = str(base64.b64decode(connectionString))
connectionString = connectionString[2:]
connectionString = connectionString[:-1]
# print (connectionString)
  
# used for taking input from database_config file.
# storage_name = str(parser.get('azure_storage_config', 'container_name'))

# used for taking input from jekins 
storage_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME_PROD")
storage_name = str(base64.b64decode(storage_name))
storage_name = storage_name[2:]
storage_name = storage_name[:-1]
# print (storage_name)

list1= os.system("mysql -h %s -u %s -p%s -e 'SHOW DATABASES' > list" % (db_config['host'],db_config['user'],key))
# print("mysql -h %s -u %s -p%s -e 'SHOW DATABASES' > list" % (db_config['host'],db_config['user'],key))
myNames=[]
filters=['Database','mysql','sys','performance_schema','information_schema','p2p_service_db', 'third_party_services_db','ratings_service_db', 'remittance_service_db','withdraw_service_db', 'web_payment_service_db', 'add_money_service_db']
with open('list', 'r') as f:
    for line in f:
        myNames.append(line.strip())
print(myNames)
db_name=[]
for names in myNames:
    if names not in filters:
        db_name.append(names)
print(db_name)

# current date
date_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))
 
"""
 Method body
"""
 
 
def create_file(path):
    """
         Create folder function
         :param path: create a file path
    :return:
    """
         # Remove the first space
    path = path.strip()
         # Remove tail \ symbol
    path = path.rstrip("\\")
 
         # Determine if the path exists
    if not os.path.exists(path):
                 #Create a directory if it does not exist
        os.makedirs(path)
        return True
    else:
                 # Do not create if the directory exists
        return False
 
 
def export_backup(address,id):
     # () "call mysqldump -h address -u username -p password database name to be backed up > generated file name"
     os.system("mysqldump -h%s -u%s -p%s %s |gzip > %s" % (
      db_config['host'], db_config['user'],key,db_name[i], address))
 
 
def delete_zip(folder):
    """
         Delete file function
    """
    rmtree(folder)
    print("Removing " + folder + " from local system")

# Added function to get week of the month
def week_number_of_month(date_value):
     return (date_value.isocalendar()[1] - date_value.replace(day=1).isocalendar()[1] + 1)

 

if sys.argv[1] == 'hourly':
 
# Export database backup
    for i in range(len(db_name)):

        # folder address
        ts = time.gmtime()
        time_list=time.strftime("%Y-%m-%d %H:%M:%S", ts).split(" ")
        mkpath = "./%s/%s" % ('hourly', time_list[0])
        mkpathblob = "%s/%s" % ('hourly', time_list[0])
        # backup file address
     
        create_file(mkpath+"/"+db_name[i])
        print(mkpath+"/"+db_name[i])
        print("folder creation completed")
        address = "%s/%s/%s/%s.sql.gz" % ('hourly',time_list[0],db_name[i],time_list[1])
     
        # backup database 
        export_backup(address,i) 
        filename = address
        dump_name = filename.split('/')
      #   print (dump_name[3])
     
        blobName = mkpathblob+"/"+db_name[i]+"/"+dump_name[3]
        blob_service_client = BlobServiceClient.from_connection_string(connectionString)
        blob_client = blob_service_client.get_blob_client(container=storage_name, blob=blobName)
      #   blob_client = BlobClient.from_blob_url(sas_url)
      #   print (mkpath)
      #   print (mkpathblob)
      #   print (db_name[i])
      #   print (address)

        with open(address, "rb") as data:
          blob_client.upload_blob(data, blob_type="BlockBlob")

        print("Uploaded")
        print("Backup database completed: %s" % address)
     
        # Delete documents other than the number of days reserved
     
        print("Delete retention days beyond file completed: %s" % db_name[i])

        delete_zip(sys.argv[1])

    

elif sys.argv[1] == 'weekly':

    for i in range(len(db_name)):
 
        # folder address
        ts = time.gmtime()
        time_list=time.strftime("%Y-%m-%d-%H:%M:%S", ts)
        year=time.strftime("%Y-%m")
        date_given = datetime.datetime.today().date()
        week_number=week_number_of_month(date_given)
        week_folder = ('week-' + str(week_number))
        mkpath = "./%s/%s/%s"  % ('weekly',year,week_folder)
        mkpathblob = "%s/%s/%s" % ('weekly', year,week_folder)
        # backup file address
     
 
     
        create_file(mkpath+"/"+db_name[i])
        print(mkpath+"/"+db_name[i])
        print("folder creation completed")
        address = "%s/%s/%s/%s/%s.sql.gz" % ('weekly',year,week_folder,db_name[i],time_list)
     
        # backup database 
        export_backup(address,i) 
        filename = address
        dump_name = filename.split('/')
      #   print (dump_name[4])
     
      #   accountEndpoint = storage_account
      #   container = storage_name
        blobName = mkpathblob+"/"+db_name[i]+"/"+dump_name[4]
        blob_service_client = BlobServiceClient.from_connection_string(connectionString)
        blob_client = blob_service_client.get_blob_client(container=storage_name, blob=blobName)
      #   blob_client = BlobClient.from_blob_url(sas_url)
      #   print (mkpath)
      #   print (db_name[i])
      #   print (address)

        with open(address, "rb") as data:
          blob_client.upload_blob(data, blob_type="BlockBlob")     

        print("Uploaded")
        print("Backup database completed: %s" % address)
     
       # Delete documents other than the number of days reserved
     
        print("Delete retention days beyond file completed: %s" % db_name[i]) 

        delete_zip(sys.argv[1])

elif sys.argv[1] == 'monthly':

    for i in range(len(db_name)):
 
        # folder address
        ts = time.gmtime()
        time_list=time.strftime("%Y-%m-%d-%H:%M:%S", ts)
        year=time.strftime("%Y")
        month_name=time.strftime("%B")
        mkpath = "./%s/%s/%s" % ('monthly',year,month_name)
        mkpathblob = "%s/%s/%s" % ('monthly',year,month_name)
        # backup file address
       
        create_file(mkpath+"/"+db_name[i])
        print(mkpath+"/"+db_name[i])
        print("folder creation completed")
        address = "%s/%s/%s/%s/%s.sql.gz" % ('monthly',year,month_name,db_name[i],time_list)
     
      # backup database 
        export_backup(address,i) 
        filename = address
        dump_name = filename.split('/')
      #   print (dump_name)
     
      #   accountEndpoint = storage_account
      #   container = storage_name

        blobName = mkpathblob+"/"+db_name[i]+"/"+dump_name[4]
        blob_service_client = BlobServiceClient.from_connection_string(connectionString)
        blob_client = blob_service_client.get_blob_client(container=storage_name, blob=blobName)
      #   blob_client = BlobClient.from_blob_url(sas_url)
      #   print (mkpath)
      #   print (db_name[i])
      #   print (address)

        with open(address, "rb") as data:
          blob_client.upload_blob(data, blob_type="BlockBlob")     

        print("Uploaded")
        print("Backup database completed: %s" % address)
     
      # Delete documents other than the number of days reserved
     
        print("Delete retention days beyond file completed: %s" % db_name[i])
        delete_zip('monthly')

else:        
        print("Please Give Valid Argument like hourly or weekly or monthly.")



