import mysql.connector
import xmltodict
import os
import subprocess
import pydicom

#load database configuration from config.xml file
fin = open("/var/www/loris/project/config.xml", "r")

ret = xmltodict.parse( fin.read() )
host = ret['config']['database']['host']
username = ret['config']['database']['username']
password = ret['config']['database']['password']
database = ret['config']['database']['database']

mydb = mysql.connector.connect(
  host=host,
  user=username,
  passwd=password,
  database=database
)

mycursor = mydb.cursor()
#mycursor.execute("SELECT * FROM candidate")
#myresult = mycursor.fetchall()

#for x in myresult
#  print(x)

os.chdir( '/home/lorisadmin/Desktop/pre' )

def decode(x):
    return x.decode('UTF-8')

minuTR, maxuTR, minuTE, maxuTE, = None, None, None, None

def CandidateExist( patientID ):
    print( patientID )
    mycursor.execute("SELECT externalid FROM candidate WHERE externalid = %s LIMIT 1", (patientID,) )
    myresult = mycursor.fetchall()
    #True if externalid is in candidates
    return len(myresult) == 1

def GetMaximumCandID():
    #COALESCE treats null as 0
    mycursor.execute("SELECT COALESCE( max(candid), 0 ) FROM candidate")
    myresult = mycursor.fetchall()
    return myresult[0][0]

def GetNextPSCID():
    #COALESCE treats null as 0
    mycursor.execute("SELECT count(*)+1 FROM candidate")
    myresult = mycursor.fetchall()
    return myresult[0][0]

def GetNextCandID( num ):
    num = str(num+1)
    while len(num) < 6:
        num = "0" + num
    return num

def CreateCandidate( patientID, patientName, patientSex, patientBod ):
    #inserts candidate
    print( "Creating candidate")
    maximum_candid = GetMaximumCandID()
    if maximum_candid == 0:
        CandID = "0" * 6
    else:
        CandID = GetNextCandID( maximum_candid )
    print( 'CandID for new candidate:', CandID )
    PSCID = GetNextPSCID()
    print( 'PSCID for new candidate:', PSCID )



    pass

for folder in os.listdir():
    #files = subprocess.call(  )

    p = subprocess.Popen( [ "find", "./" + folder, "-name", "*dcm" ], stdout=subprocess.PIPE)
    files = list( map( decode, p.communicate()[0].split() ) )
    print( files[0] )

    #use First file to extract header-informations
    patient = pydicom.dcmread( files[0] )
    patientID = patient.PatientID
    patientName = patient.PatientName
    patientSex = patient.PatientSex
    patientBod = patient.PatientBirthDate
    patientTR = patient.RepetitionTime
    patientTE = patient.EchoTime

    #check if Patient exist
    if CandidateExist( patientID ) == False:
        CreateCandidate( patientID, patientName, patientSex, patientBod )

    #starting-values are equal to the values of first file
    if minuTR == None:
        minuTR = patientTR
        minuTE = patientTE
        maxuTR = patientTR
        maxuTE = patientTE

    print( patientName, patientTR, type(patientTR) )

    #process all files
    for file in files:
        tmp_patient = pydicom.dcmread( file )
        tmp_patientTR = patient.RepetitionTime
        tmp_patientTE = patient.EchoTime
        #dcmodify-header

        ####subprocess-call

        #update Max, Min ( which protocol? e.x. t1 )
        maxuTR = max( maxuTR, tmp_patientTR )
        maxuTE = max( maxuTE, tmp_patientTE )
        minuTR = max( minuTR, tmp_patientTR )
        minuTE = max( minuTE, tmp_patientTE )

    #print( files )

    print( patientTR )
    break

print( maxuTR )
exit(0)
