from web3 import Web3
import json, requests, time, random
from datetime import datetime

c = requests.Session()
w3 = Web3(Web3.HTTPProvider('https://rpc.mainnet.taiko.xyz'))

with open("abi.json", "r") as f:
    abi = json.load(f)

privatekey = "ISI PRIVATE KEY KALIAN"  
address = w3.eth.account.from_key(privatekey).address

if w3.is_connected():
    print("Connected to the network")
else:
    print("Failed to connect to the network")

def userdata(address, totalvotes):
    users = c.get(
        f"https://trailblazer.mainnet.taiko.xyz/s3/user/rank?address={address}",
        headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"}
    ).json()
    output = (
        f"Rank >> {users['rank']}\n"
        f"Score >> {users['totalScore']}\n"
        f"Blacklisted >> {'Yes' if users['blacklisted'] else 'No'}\n"
        f"Multiplier >> {users['multiplier']}\n"
        f"Total Users >> {users['total']}\n"
        f"Top >> {((users['total'] - users['rank']) / users['total'] * 100):.2f}%\n"
        f"Total Votes >> {totalvotes}\n"
        f"Current Time >> {datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')}"
    )
    print(output)
    c.post(
        url='https://api.telegram.org/bot7549668811:AAEkfnmaiWTzd1P2eQnOeRMA965EzIlHXB8/sendMessage',
        data={'chat_id': 5462185992, 'text': output} #GANTI CHAT ID DENGAN ID TELEGRAM KALIAN 
    ).json()

def vote_tx():
    try:
        contract = w3.eth.contract(address=w3.to_checksum_address('0x4D1E2145082d0AB0fDa4a973dC4887C7295e21aB'), abi=abi)
        tx = contract.functions.vote().build_transaction(
            {
                "from": w3.to_checksum_address(address),
                "value": 0,
                "gasPrice": w3.to_wei(0.234, 'gwei'),
                "gas": 0,
                "nonce": w3.eth.get_transaction_count(address)
            }
        )
        tx.update({'gas': w3.eth.estimate_gas(tx)})
        signed_txns = w3.eth.account.sign_transaction(tx, private_key=privatekey)
        tx_hash = w3.eth.send_raw_transaction(signed_txns.raw_transaction)
        print("Recipt >> " + w3.to_hex(tx_hash))
        print("Waiting For Confirmation")
        try:
            w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            print("Confirmed on Block >> " + str(w3.eth.get_block('latest').number))
            print("Successfully Voted")
        except Exception:
            print("Tx Dropped/Failed")
    except Exception:
        vote_tx()

i = 0
last_executed = None
max = random.randint(72, 75)

while True:
    if max >= i:
        vote_tx()
    else:
        time.sleep(60)
    times = random.randint(5, 10)
    i += 1
    print("Vote " + str(i) + " Done")
    print("Waiting For Next Vote on >> " + str(times) + " Seconds")
    print("Current Time >> " + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
    print("--------------------------------")
    time.sleep(times)
    current_time = datetime.fromtimestamp(time.time())
    if current_time.hour == 7 and (last_executed is None or last_executed != current_time.date()):
        userdata(address, i)
        print("Daily Userdata Sent at >> " + datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
        print("Daily Tx Reset at >> " + datetime.fromtimestamp(time.time() + 86400).strftime('%Y-%m-%d %H:%M:%S'))
        print("--------------------------------")
        last_executed = current_time.date()  # Perbarui dengan tanggal hari ini
        max = random.randint(72, 75)
        i = 0
