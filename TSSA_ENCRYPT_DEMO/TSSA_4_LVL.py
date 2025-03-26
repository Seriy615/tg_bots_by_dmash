import random
import pyaes
import pbkdf2
import binascii
import os
import hashlib
import hmac

class TSSA:
    @staticmethod
    def generate_key_from_password_and_salt(password, salt):
        # Derive a key from the password and salt using a hash function
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return key

    @staticmethod
    def pad(message):
        # PKCS7 padding
        pad_length = 16 - (len(message) % 16)
        return message + bytes([pad_length] * pad_length)

    @staticmethod
    def unpad(message):
        # Remove PKCS7 padding
        pad_length = message[-1]
        return message[:-pad_length]

    @staticmethod
    def encrypt_AES(message, password, salt):
        # Generate key from password and salt
        key = TSSA.generate_key_from_password_and_salt(password, salt)

        # Pad the message
        padded_message = TSSA.pad(message)

        # Use AES for encryption
        aes = pyaes.AESModeOfOperationCTR(key)
        ciphertext = aes.encrypt(padded_message)

        return ciphertext

    @staticmethod
    def decrypt_AES(ciphertext, password, salt):
        # Generate key from password and salt
        key = TSSA.generate_key_from_password_and_salt(password, salt)

        # Use AES for decryption
        aes = pyaes.AESModeOfOperationCTR(key)
        padded_plaintext = aes.decrypt(ciphertext)

        # Remove padding
        plaintext = TSSA.unpad(padded_plaintext)

        return plaintext

    @staticmethod
    def encrypt_element(element, key):
        # Use AES for encrypting element
        aes = pyaes.AESModeOfOperationCTR(key)
        encrypted_element = aes.encrypt(element.encode())
        return encrypted_element

    @staticmethod
    def decrypt_element(encrypted_element, key):
        # Use AES for decrypting element
        aes = pyaes.AESModeOfOperationCTR(key)
        decrypted_element = aes.decrypt(encrypted_element).decode()
        return decrypted_element

    @staticmethod
    def chip_massive(massive):
        result = ''
        for i in massive:
            result += i + '$/$'
        return result

    @staticmethod
    def dechip_massive(chip_massive):
        massive = list(chip_massive.split('$/$'))
        a = massive.pop()
        return massive

    @staticmethod
    def massive_to_str(massive):
        result = ''
        for i in massive:
            result += i
        return result

    @staticmethod
    def generate_SEQ(message):
        SEQ_1 = [str(i) for i in range(len(message))]
        random.shuffle(SEQ_1)

        salt = os.urandom(16)  # Generating a random 16-byte salt
        salt_hex = binascii.hexlify(salt).decode('utf-8')  # Converting salt to a hexadecimal string

        SEQ_2 = [str(i) for i in range(len(salt_hex))]
        random.shuffle(SEQ_2)

        SEQ_3 = [str(i) for i in range(len(message + salt_hex))]
        random.shuffle(SEQ_3)

        return [SEQ_1, SEQ_2, SEQ_3, salt_hex]

    @staticmethod
    def mix_SEQ(stra, SEQ):
        result = [0] * len(stra)
        for i in range(len(stra)):
            result[int(SEQ[i])] = str(stra[i])
        result = TSSA.massive_to_str(result)
        return result

    @staticmethod
    def dechip_SEQ(chip, SEQ):
        result = [0] * len(chip)
        for i in range(len(chip)):
            result[i] = chip[int(SEQ[i])]
        result = TSSA.massive_to_str(result)
        return result

    @staticmethod
    def encrypt(message, password, receiver_id):
        PIN_1 = password[:int(len(password)/2)]
        PIN_2 = password[int(len(password)/2):]
        PIN_3 = password
        SEQ_1, SEQ_2, SEQ_3, salt = TSSA.generate_SEQ(message)
        mixed_message = TSSA.mix_SEQ(message, SEQ_1)
        mixed_salt = TSSA.mix_SEQ(salt, SEQ_2)
        pre_mixed = mixed_message + mixed_salt
        mixed = TSSA.mix_SEQ(pre_mixed, SEQ_3)
        key_SEQ = TSSA.generate_key_from_password_and_salt(PIN_1, receiver_id)

        # Encrypting each element in SEQ
        SEQ_1c = []
        for element in SEQ_1:
            SEQ_1c.append(binascii.hexlify(TSSA.encrypt_element(element, key_SEQ)).decode('utf-8'))
        SEQ_2c = []
        for element in SEQ_2:
            SEQ_2c.append(binascii.hexlify(TSSA.encrypt_element(element, key_SEQ)).decode('utf-8'))
        SEQ_3c = []
        for element in SEQ_3:
            SEQ_3c.append(binascii.hexlify(TSSA.encrypt_element(element, key_SEQ)).decode('utf-8'))

        plaintext = mixed + '$//$' + TSSA.chip_massive(SEQ_1c) + '$//$' + TSSA.chip_massive(SEQ_2c) + '$//$' + TSSA.chip_massive(SEQ_3c)

        # Encrypting the mixed message
        ciphertext = TSSA.encrypt_AES(plaintext.encode('utf-8'), PIN_2, receiver_id)

        # Generate a random nonce
        nonce = os.urandom(16)

        # Generate HMAC key
        hmac_key = TSSA.generate_key_from_password_and_salt(PIN_3, receiver_id)

        # Compute HMAC
        hmac_digest = hmac.new(hmac_key, ciphertext + nonce, hashlib.sha256).digest()

        return binascii.hexlify(ciphertext), binascii.hexlify(nonce), binascii.hexlify(hmac_digest)

    @staticmethod
    def decrypt(hex_ciphertext, hex_nonce, hex_hmac, password, receiver_id):
        PIN_1 = password[:int(len(password)/2)]
        PIN_2 = password[int(len(password)/2):]
        PIN_3 = password
        key = TSSA.generate_key_from_password_and_salt(password, receiver_id)
        ciphertext = binascii.unhexlify(hex_ciphertext)
        nonce = binascii.unhexlify(hex_nonce)
        hmac_digest = binascii.unhexlify(hex_hmac)

        # Generate HMAC key
        hmac_key = TSSA.generate_key_from_password_and_salt(PIN_3, receiver_id)

        # Verify HMAC
        hmac_new = hmac.new(hmac_key, ciphertext + nonce, hashlib.sha256).digest()
        if hmac.compare_digest(hmac_new, hmac_digest):
            decrypted = TSSA.decrypt_AES(ciphertext, PIN_2, receiver_id)
            mixed_cd, SEQ_1cd, SEQ_2cd, SEQ_3cd = decrypted.decode('utf-8').split('$//$')
            SEQ_1cde = []
            key_SEQ = TSSA.generate_key_from_password_and_salt(PIN_1, receiver_id)
            for element in TSSA.dechip_massive(SEQ_1cd):
                SEQ_1cde.append(TSSA.decrypt_element(binascii.unhexlify(element), key_SEQ))
            SEQ_2cde = []
            for element in TSSA.dechip_massive(SEQ_2cd):
                SEQ_2cde.append(TSSA.decrypt_element(binascii.unhexlify(element), key_SEQ))
            SEQ_3cde = []
            for element in TSSA.dechip_massive(SEQ_3cd):
                SEQ_3cde.append(TSSA.decrypt_element(binascii.unhexlify(element), key_SEQ))
            message_salt = TSSA.dechip_SEQ(mixed_cd, SEQ_3cde)
            message = message_salt[:len(SEQ_1cde)]
            decrypted = TSSA.dechip_SEQ(message, SEQ_1cde)
            return decrypted
        else:
            raise ValueError("HMAC verification failed")

# Example usage:

message = input("Enter message to encrypt: ")
receiver_id = input("Enter receiver_id: ").encode('utf-8')
password = input("Enter password: ")

encrypted_message, nonce, hmac_digest = TSSA.encrypt(message, password, receiver_id)
print("Encrypted message:", encrypted_message.decode())
print("Nonce:", nonce.decode())
print("HMAC:", hmac_digest.decode())

# Decrypting the message
hex_ciphertext = input("Enter the hex representation of the ciphertext: ")
hex_nonce = input("Enter the hex representation of the nonce: ")
hex_hmac = input("Enter the hex representation of the HMAC: ")
password = input('Enter password: ')
receiver_id = input('Enter Your id: ').encode('utf-8')

decrypted_message = TSSA.decrypt(hex_ciphertext, hex_nonce, hex_hmac, password, receiver_id)
print("Decrypted message:", decrypted_message)
