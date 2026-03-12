# Vigenere cipher implementation

def decrypt(ciphertext: str, key: str) -> str:
    """
    Decrypt a Vigenere cipher text using the given key.
    
    Args:
        ciphertext: The encrypted text to decrypt
        key: The key to use for decryption
    
    Returns:
        The decrypted plaintext in lowercase (to match test expectations)
    """
    key = key.upper()
    result = []
    key_index = 0
    
    for char in ciphertext:
        if char.isalpha():
            char_upper = char.upper()
            
            # Convert to 0-25 range
            char_num = ord(char_upper) - ord('A')
            key_num = ord(key[key_index % len(key)]) - ord('A')
            
            # Vigenere decryption: (char_num - key_num) mod 26
            decrypted_num = (char_num - key_num) % 26
            
            # Convert back to character
            decrypted_char = chr(decrypted_num + ord('A'))
            result.append(decrypted_char)
            key_index += 1
        else:
            # Keep non-alphabetic characters as is
            result.append(char)
    
    # Return everything in lowercase to match test expectations
    return ''.join(result).lower()