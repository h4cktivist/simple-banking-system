import sys
import random
import sqlite3


conn = sqlite3.connect('card.s3db')
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS card;')
cur.execute('CREATE TABLE IF NOT EXISTS card ('
            'id INTEGER PRIMARY KEY,'
            'number TEXT,'
            'pin TEXT,'
            'balance INTEGER DEFAULT 0);')

first_6 = 400000


def luhn_checksum(card_number):
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = 0
    checksum += sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d*2))
    return checksum % 10


def is_luhn_valid(card_number):
    return luhn_checksum(card_number) == 0


def luhn():
    global first_6
    card_no = [int(i) for i in str(first_6)]
    card_num = [int(i) for i in str(first_6)]
    seventh_15 = random.sample(range(9), 9)
    for i in seventh_15:
        card_no.append(i)
        card_num.append(i)
    for t in range(0, 15, 2):
        card_no[t] = card_no[t] * 2
    for i in range(len(card_no)):
        if card_no[i] > 9:
            card_no[i] -= 9
    s = sum(card_no)
    mod = s % 10
    check_sum = 0 if mod == 0 else (10 - mod)
    card_num.append(check_sum)
    card_num = [str(i) for i in card_num]
    return ''.join(card_num)


while True:
    print('1. Create an account')
    print('2. Log into account')
    print('0. Exit')

    act = input('> ')


    if act == '1':
        card = luhn()
        pin = random.randint(1000, 9999)
        cur.execute('INSERT INTO card(number, pin) VALUES(?, ?)', (card, pin))
        conn.commit()

        print('Your card has been created')
        print('Your card number:')
        print(card)
        print('Your card PIN:')
        print(pin)


    elif act == '2':
        print('')
        print('Enter your card number:')
        entered_card = input()
        print('Enter your PIN:')
        entered_pin = input()

        cards = cur.execute('SELECT number FROM card').fetchall()
        pins = cur.execute('SELECT pin FROM card').fetchall()

        if entered_card in cards[0] and entered_pin in pins[0]:
            print('You have successfully logged in!')
            logged_in = True
        else:
            print('Wrong card number or PIN!')
            logged_in = False


        while logged_in:
            print('')
            print('1. Balance')
            print('2. Add income')
            print('3. Do transfer')
            print('4. Close account')
            print('5. Log out')
            print('0. Exit')

            act = input('> ')
            if act == '1':
                print('')
                balance = cur.execute(f'SELECT balance FROM card WHERE number = {entered_card}').fetchall()
                print('Balance: ', balance[0][0])

            elif act == '2':
                print('')
                print('Income')
                print('Enter income')

                income = int(input('> '))
                balance = cur.execute(f'SELECT balance FROM card WHERE number = {entered_card}').fetchall()
                new_balance = balance[0][0] + income
                cur.execute(f'UPDATE card SET balance = {new_balance} WHERE number = {entered_card}')
                conn.commit()

                print('Income was added!')

            elif act == '3':
                print('')
                print('Transfer')
                print('Enter card number:')

                number = input('> ')
                if is_luhn_valid(number):
                    transfer_num = cur.execute(f'SELECT number FROM card WHERE number = {number}').fetchall()

                    if len(transfer_num):
                        print('Enter how much money you want to transfer:')
                        transfer = int(input('> '))
                        transfer_num = transfer_num[0][0]
                        balance = cur.execute(f'SELECT balance FROM card WHERE number = {entered_card}').fetchall()

                        if transfer <= balance[0][0]:
                            my_new_balance = balance[0][0] - transfer
                            transfer_bal = cur.execute(f'SELECT balance FROM card WHERE number = {transfer_num}').fetchall()
                            tr_new_bal = transfer_bal[0][0] + transfer
                            cur.execute(f'UPDATE card SET balance = {my_new_balance} WHERE number = {entered_card}')
                            cur.execute(f'UPDATE card SET balance = {tr_new_bal} WHERE number = {transfer_num}')
                            conn.commit()
                            print('Success!')
                        else:
                            print('Not enough money!')

                    else:
                        print('Such a card does not exist.')

                else:
                    print('Probably you made a mistake in the card number. Please try again!')

            elif act == '4':
                cur.execute(f'DELETE FROM card WHERE number = {entered_card}')
                conn.commit()
                logged_in = False
                print('')
                print('The account has been closed!')

            elif act == '5':
                logged_in = False
                print('')
                print('You have successfully logged out!')

            elif act == '0':
                print('')
                print('Bye!')
                sys.exit()


    elif act == '0':
        print('')
        print('Bye!')
        sys.exit()
