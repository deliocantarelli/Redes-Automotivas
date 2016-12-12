#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

key = b'z\xDC\x18\x90\xA2\x81\x86\xA9'
iv = b'\x91i\xA9<\x98\x9El\xB6'

def crypt_byte(size, bytes):

	to_fill = 7- size
	rand_bytes = b''
	if to_fill > 0:
		rand_bytes = os.urandom(to_fill)
	message = bytes[2:] + rand_bytes

	#key = os.urandom(8)
	#print(key)
	backend = default_backend()
	#iv = os.urandom(8)
	#print(iv)

	cipher = Cipher(algorithms.CAST5(key), modes.OFB(iv), backend=backend)

	encryptor = cipher.encryptor()

	ct = encryptor.update(message) + encryptor.finalize()

	return bytes[:2] + ct

def decrypt_byte(bytes):

	backend = default_backend()

	cipher = Cipher(algorithms.CAST5(key), modes.OFB(iv), backend=backend)

	decryptor = cipher.decryptor()
	message = decryptor.update(bytes) + decryptor.finalize()
	
	return message

