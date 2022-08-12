import os

import logging
import sys

import smpplib.gsm
import smpplib.client
import smpplib.consts

from config import Config

# get credentials
credentials = Config ()
smpp_server = credentials.get ("smpp_server")
smpp_port = credentials.get ("smpp_port")
system_id = credentials.get ("system_id")
password = credentials.get ("password")
source_addr = credentials.get ("source_addr")
current_folder = os.path.dirname (__file__)

# Get message
message_path = os.path.join (current_folder, "message.txt")
with open (message_path) as file:
    message = file.read ()

# Get numbers
numbers_path = os.path.join (current_folder, "numbers.txt")
with open (numbers_path) as file:
    # Get and clean numbers
    numbers = file.read ().split("\n")
    numbers = list(map (lambda num : num.strip(), numbers))

# if you want to know what's happening
logging.basicConfig(level='DEBUG')

# Two parts, UCS2, SMS with UDH
parts, encoding_flag, msg_type_flag = smpplib.gsm.make_parts(message)

client = smpplib.client.Client(smpp_server, smpp_port, allow_unknown_opt_params=True)

# Print when obtain message_id
client.set_message_sent_handler(
    lambda pdu: sys.stdout.write('sent {} {}\n'.format(pdu.sequence, pdu.message_id)))
client.set_message_received_handler(
    lambda pdu: sys.stdout.write('delivered {}\n'.format(pdu.receipted_message_id)))

client.connect()
client.bind_transceiver(system_id=system_id, password=password)

# Send the message to each number
for number in numbers:

    for part in parts:
        pdu = client.send_message(
            source_addr_ton=smpplib.consts.SMPP_TON_INTL,
            #source_addr_npi=smpplib.consts.SMPP_NPI_ISDN,
            # Make sure it is a byte string, not unicode:
            source_addr=source_addr,

            dest_addr_ton=smpplib.consts.SMPP_TON_INTL,
            #dest_addr_npi=smpplib.consts.SMPP_NPI_ISDN,
            # Make sure thease two params are byte strings, not unicode:
            destination_addr=number,
            short_message=part,

            data_coding=encoding_flag,
            esm_class=msg_type_flag,
            registered_delivery=True,
        )
        print(pdu.sequence)
    
# Enters a loop, waiting for incoming PDUs
client.listen()