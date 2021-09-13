from time import sleep
import imaplib
import email
import base64

mail = imaplib.IMAP4_SSL("imap.gmail.com") # Standard protocol, port defaults to 993
id_list = [] # Initiate variable
mail_init = 0

def init_mail():
    global id_list
    global mail_init
    try:
        mail.login("x@gmail.com", "x") # Gmail address and application password
        mail.select("chia") # Select inbox, in my case label is "chia" rather than "INBOX"
        id_list = get_email_list() # Get newest index of inbox
        mail_init = 1
    except:
        print("Failed to authenticate. Exiting..")
        quit()
    
def exit_mail():
    global id_list
    global mail_init
    # Make sure we don't keep an open connection once we're done with business
    try:
        mail.close()
        mail.logout()
        mail_init = 0
        id_list = []
    except:
        print("Failed to close mailbox!")

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
        return("Failed to fetch email list. Exiting..")
        quit()

def getEarnings(email_index):
    # Method to fetch hpool earnings in 
    # the format 0.XXXXXXXX from chia inbox

    if mail_init == 0: # Initiate mail if not already done
        init_mail()

    x, msg = mail.fetch(str(int(id_list[email_index])), "(RFC822)") # Fetch the whole damn email

    for response_part in msg:
        if isinstance(response_part, tuple):
            try:
                msg = email.message_from_bytes(response_part[1]).get_payload(decode=True).decode() # Decrypt text from bytes
                chia_earnings = str(msg.split(":")[1]).split("C")[0] # Split earnings from message body

                # Try to return a float, if we have emails that also work in the split, we'll avoid sending back random text..
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

    init_mail()

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

    exit_mail()
    return earnings

print(str(getLifetimeEarnings()))