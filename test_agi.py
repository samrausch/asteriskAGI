#!/usr/bin/python3

# TO DO:
# Add handling for when a user isn't found in Redis, or when a user has a NULL trustscore
# Add handling for calls with successful PIN validation to pass back to Ast DP for outbound routing

from asterisk.agi import *
import redis
import sys

r1 = redis.Redis(host='localhost', port=6379, db=0, password='fraudhappens')
r2 = redis.Redis(host='localhost', port=6379, db=2, password='fraudhappens')

agi = AGI()

agi.verbose("fraud_ivr agi started")

contact = sys.argv[1]
contactIP = contact.split("@")[1]
contactIP = contactIP.split(":")[0]
contactUser = contact.split("@")[0]
contactUser = contactUser.split(" ")[1]
contactUser = contactUser.split(":")[1]
extension = agi.env['agi_callerid']

scorequery = str(extension) + ":trustscore"
pinquery = str(extension) + ":pin"
score = int(r1.get(scorequery))
pin = int(r1.get(pinquery))
agioutput1 = str(extension) + " trust score: " + str(score)
agioutput2 = str(extension) + " PIN: " + str(pin)
agi.verbose(agioutput1)
agi.verbose(agioutput2)

# agi.get_data timeout is in ms, not s as indicated in the documentation
userinput = agi.get_data('vm-password', 5000, 4)

agi.verbose(userinput)
if int(userinput) == pin:
        newscore = int(score) - 10
        if newscore < 0:
                newscore = 0
        agi.verbose(newscore)
        r1.set(scorequery, newscore)
        agi.stream_file('auth-thankyou')
        agioutput3 = str(extension) + " PIN verified"
        agi.verbose(agioutput3)
        agi.hangup()
        sys.exit()

if int(userinput) != pin:
        newscore = int(score) + 10
        if newscore > 100:
                newscore = 100
        agi.verbose(newscore)
        r1.set(scorequery, newscore)
        agi.stream_file('vm-invalidpassword')
        agioutput4 = str(extension) + " PIN verification failed!"
        agi.verbose(agioutput4)
        agi.hangup()
        sys.exit()

agioutput5 = str(extension) + " an error occured in AGI verifying the PIN"
agi.verbose(agioutput5)
agi.hangup()
sys.exit()
