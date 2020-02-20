"""
preprocess.py

University of New South Wales - Term 3, 2019
COMP9321 - Data Services Engineering
Assignment 2 - Team Degenerates

Load user credential and apply one-way hash to passwords.
"""
import pandas as pd
import hashlib
import binascii


def main():
    # Load users file
    users_df = pd.read_json('datasets/users.json', orient='records')

    # Encode passwords
    salt = b'\x02V\xfew\xc9\xaf\x18\x97U\x8d\x97\x19\x81X\xbfU\xab\xcb\x84=\x86\r{\xa2\xe6\x1cYS\xff*;M'
    users_df['password'] = users_df['password'].apply(lambda x: binascii.hexlify(hashlib.pbkdf2_hmac('sha256', x.encode('utf-8'), salt, 100000)).decode('utf-8'))

    # Rename and reset index
    users_df.index.rename('id', inplace=True)
    users_df.index += 10000

    # Save
    users_df.to_csv('users.csv')



if __name__ == '__main__':
    main()
