from time import sleep
import imaplib
import email
import base64

mail = imaplib.IMAP4_SSL("imap.gmail.com") # Standard protocol, port defaults to 993
mail.login("email@gmail.com", "APP PASSWORD") # Gmail address and application password
mail.select("chia") # Select inbox, in my case label is "chia" rather than "INBOX"

id_list = 0 # Initialise global list for all methods to access

def get_email_list():
    # Method to index the selected inbox
    # which in turns allows us to select
    # emails from ID 0 to the max index
    
    global id_list # Tell the method id_list is a global var so new data is available to all methods

    print("Fetching emails...") # Let us know what we're doing
    type, data = mail.search(None, "ALL") # Just read all mails in box.. why not? 
    mail_ids = data[0]
    id_list = mail_ids.split()
    id_list.reverse() # Reverse list to put most recent emails first in index

def getEarnings(emailid):
    # Method to fetch hpool earnings in 
    # the format 0.XXXXXXXX from chia inbox

    x, msg = mail.fetch(str(int(id_list[emailid])), "(RFC822)") # fetch the whole damn email

    for response_part in msg:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1]).get_payload(decode=True).decode() # Decrypt text from bytes
            chia_earnings = str(msg.split(":")[1]).split("C")[0] # Split earnings from message body

            # Try to return a float, if we have emails that also work in the split, we'll avoid sending back random text..
            try:
                return float(chia_earnings)
            except:
                return 0

def getLifetimeEarnings():
    # Now we just loop through our beautiful getEarnings method
    # to calculate just how much we've received according to inbox

    # but first we declare some stuff outside the loop..
    prev_earnings = 0
    earnings = 0
    i = 0

    get_email_list() # Get newest index of inbox

    for emails in id_list:
        new_earnings = getEarnings(i)
        if not prev_earnings == new_earnings:
            earnings = earnings + new_earnings
            prev_earnings = new_earnings
            print("Adding " + str(prev_earnings) + " to total earnings of " + str(earnings)[:10] + " XCH") # Optional debug text
        i+=1
    print("Total earnings: " +str(earnings)[:10])
    print("Emails parsed: "+ str(i))

getLifetimeEarnings()       # And get the money loop going!