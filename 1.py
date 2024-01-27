import requests
from datetime import datetime, timedelta, timezone
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Replace with your Binance API key and secret
api_key = 'gldyKTFFWuZWXdQomriCbE25jnPhZEbRqUJj4ZmlHYxEBr8xRxzbtFjhr8s6OOi0'
api_secret = 'sr3U853ksYuxZWnyTBMwEAZVjzKMlcW2ohv2b3X0Bn88AYkSMdrG1gM8eDBuEjCD'

# Binance Futures API endpoint for klines (candlestick data)
endpoint = 'https://fapi.binance.com/fapi/v1/klines'

# List of pairs
pairs = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'UMAUSDT', 'ORDIUSDT', 'SUIUSDT', 'ARBUSDT', 'XRPUSDT', 'DOGEUSDT', 'AVAXUSDT']

# Get the current server time
server_time = requests.get('https://fapi.binance.com/fapi/v1/time').json()['serverTime']

# Print the timeframe being analyzed
print(f'Analyzing Data for 15-minute Candles on Binance Futures...\n')

# Dictionary to store pairs with multiples greater than 3x
result_dict = {}

# Set your Gmail credentials
email_user = 'ahsanzahid3@gmail.com'  # Replace with your Gmail address
email_password = 'knonxhfbmykhyeyu'  # Replace with your Gmail app password

# Function to send an email
def send_email(subject, body):
    from_email = email_user
    to_email = 'ahsanzahid3@gmail.com'
    
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_user, email_password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print(f'Email sent successfully to {to_email}')
    except Exception as e:
        print(f'Error sending email: {e}')

for symbol in pairs:
    print(f'Getting Data for {symbol}...')

    # Calculate the start time for the last 51 candles
    start_time = datetime.fromtimestamp(server_time / 1000, tz=timezone.utc) - timedelta(minutes=30 * 51)
    start_time_ms = int(start_time.timestamp() * 1000)

    # Parameters for the API request
    params = {
        'symbol': symbol,
        'interval': '15m',
        'startTime': start_time_ms,
        'endTime': server_time,
        'limit': 51  # Retrieve the last 51 candles
    }

    # Add API key to request headers
    headers = {'X-MBX-APIKEY': api_key}

    # Make the API request
    response = requests.get(endpoint, params=params, headers=headers)
    klines = response.json()

    # Extract and calculate the average volume for the first 50 candles
    total_volume = sum(float(kline[5]) for kline in klines[:-1])
    average_volume = total_volume / 50

    # Extract the volume of the 2nd last candle, last candle, and current candle
    second_last_candle_volume = float(klines[-2][5])
    last_candle_volume = float(klines[-1][5])
    current_candle_volume = float(klines[-1][9])  # Note: Adjust index for futures volume

    # Calculate the multiple of the last candle in comparison to the average
    multiple = last_candle_volume / average_volume

    # Check if the multiple is greater than 3x
    if multiple > 3:
        result_dict[symbol] = {
            'Average': f'{average_volume:,.0f}',
            'Second Last Candle Volume': f'{second_last_candle_volume:,.0f}',
            'Last Candle Volume': f'{last_candle_volume:,.0f}',
            'Current Candle Volume': f'{current_candle_volume:,.0f}',
            'Multiple': multiple
        }

# Print pairs with multiples greater than 3x or "No Trades Available"
if result_dict:
    print('\nPairs with multiples greater than 3x:')
    email_body = 'Pairs with multiples greater than 3x:\n\n'
    
    for symbol, data in result_dict.items():
        email_body += f'\nCurrency Name: {symbol}\n'
        email_body += f'Average: {data["Average"]}\n'
        email_body += f'2nd Last Candle Volume: {data["Second Last Candle Volume"]}\n'
        email_body += f'Last Candle Volume: {data["Last Candle Volume"]}\n'
        email_body += f'Current Candle Volume: {data["Current Candle Volume"]}\n'
        email_body += f'Multiple: {data["Multiple"]:.2f}x\n'
        email_body += '\n' + '-' * 40 + '\n'  # Add a gap between multiple currency pairs
    send_email('Trading Alert', email_body)
else:
    print('No Trades Available')
