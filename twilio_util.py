import twilio
from twilio.rest import Client
from twilio_config import *

# Replace this with your Twilio phone number
from_number = '+16787125007'

# Replace this with the phone number you want to send the text message to
to_number = '+12134004041'

# Create a Twilio client
client = Client(account_sid, auth_token)

def clear_messages():
  messages = client.messages.list()
  for message in messages:
    message.delete()

def send_message(msg):
  # Send the text message
  message = client.messages.create(
    body=msg,
    from_=from_number,
    to=to_number
  )

def listen():
  # Initialize a set to store the message sid's of processed messages
  processed_messages = set()

  # Start listening for new messages
  while True:
    # Get the list of messages
    messages = client.messages.list()
    # Iterate through the messages
    for message in messages:
      # If the message is from the recipient and has not been processed yet
      if message.from_ == to_number and message.sid not in processed_messages:
        # Add the message sid to the set of processed messages
        processed_messages.add(message.sid)

        # Get the response
        response = message.body
        if response == 'cancel':
          raise ValueError
        # Print the response
        print(f'Response received: {response}')
        return response

