#!/usr/bin/env python3
import requests

def get_current_epoch():
    try:
        # Solana APIエンドポイントを使用して現在のエポックを取得
        url = "https://api.mainnet-beta.solana.com"
        headers = {"Content-Type": "application/json"}
        data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getEpochInfo"
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        if 'result' in result and 'epoch' in result['result']:
            current_epoch = result['result']['epoch']
            print(f"Current Solana epoch: {current_epoch}")
            print(f"\nTry using an epoch number less than the current epoch.")
            return current_epoch
        else:
            print("Error: Unexpected API response format")
            return None
            
    except Exception as e:
        print(f"Error fetching current epoch: {str(e)}")
        return None

if __name__ == "__main__":
    get_current_epoch() 