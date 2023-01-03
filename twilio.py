import twilio
from twilio.rest import Client
from twilio_config import *

# Replace this with your Twilio phone number
from_number = '+16787125007'

# Replace this with the phone number you want to send the text message to
to_number = '2134004041'

# Create a Twilio client
client = Client(account_sid, auth_token)


def send_message():
  # Send the text message
  message = client.messages.create(
    body='Please respond with a number from 1 to 10.',
    from_=from_number,
    to=to_number
  )

  print(f'Text message sent to {to_number}')

  # Initialize a variable to store the response
  response = None

  # Keep listening for a response until we receive one
  while response is None:
    # Get the list of messages
    messages = client.messages.list()

    # Iterate through the messages
    for message in messages:
      # If the message is from the recipient and has not been processed yet
      if message.from_ == to_number and message.status != 'processed':
        # Mark the message as processed
        message.update(status='processed')

        # Get the response
        response = message.body

        # Exit the loop
        break

  # Print the response
  print(f'Response received: {response}')
