from time import sleep
import imaplib
import email
import base64

mail = imaplib.IMAP4_SSL("imap.gmail.com") # Standard protocol, port defaults to 993
id_list = [] # Initiate variable

def init_mail():
    try:
        mail.login("test@gmail.com", "test") # Gmail address and application password
        mail.select("chia") # Select inbox, in my case label is "chia" rather than "INBOX"
        id_list = get_email_list() # Get newest index of inbox
    except:
        return("Failed to authenticate. Exiting...")
        quit()
    
def exit_mail():
    # Make sure we don't keep an open connection once we're done with business
    try:
        mail.close()
        mail.logout()
    except:
        return("Failed to close mailbox!")

def get_email_list():
    # Method to index the selected inbox
    # which in turns allows us to select
    # emails from ID 0 to the max index

    try:
        x, data = mail.search(None, "ALL") # Just read all mails in box.. why not? 
        mail_ids = data[0]
        list_ids = mail_ids.split()
        list_ids.reverse() # Reverse list to put most recent emails first in index
        return list_ids
    except:
        print("Failed to fetch email list. Exiting...")
        quit()

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
                return []

def getLifetimeEarnings():
    # Now we just loop through our beautiful getEarnings method
    # to calculate just how much we've received according to inbox

    # but first we declare some stuff outside the loop..
    prev_earnings = 0
    earnings = 0
    i = 0

    for emails in id_list:
        new_earnings = getEarnings(i)
        if not prev_earnings == new_earnings:
            earnings = earnings + new_earnings
            prev_earnings = new_earnings
            # Optional debug text, cutting down to 10 digits so we don't get random string errors
            # print("Adding " + str(prev_earnings) + " to total earnings of " + str(earnings)[:10] + " XCH") 
        i+=1

    # Debug printing
    # print("Total earnings: " +str(earnings)[:10])
    # print("Emails parsed: "+ str(i))

    return earnings

# Init mail to use program at all
init_mail()

# Main code
getLifetimeEarnings()       # And get the money loop going!

# Exit mailbox
exit_mail()