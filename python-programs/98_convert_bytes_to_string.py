"""Program 98: Convert Bytes to a String

Demonstrates encoding strings to bytes and decoding bytes back to strings.

Reference: https://www.programiz.com/python-programming/examples/bytes-to-string
"""


def main() -> None:
    """Demonstrate conversion between bytes and strings."""
    original_string = "Hello, Python! 🐍"
    
    print(f"Original String: {original_string}")
    print(f"Type: {type(original_string)}\n")
    
    # 1. Convert String to Bytes (Encoding)
    # Using UTF-8 which supports emojis and special characters
    byte_data = original_string.encode('utf-8')
    print(f"Bytes (UTF-8 encode): {byte_data}")
    print(f"Type: {type(byte_data)}\n")
    
    # 2. Convert Bytes back to String (Decoding)
    decoded_string = byte_data.decode('utf-8')
    print(f"Decoded String: {decoded_string}")
    print(f"Type: {type(decoded_string)}\n")
    
    assert original_string == decoded_string
    
    # Example with invalid encoding
    print("--- Decoding Error Example ---")
    bad_bytes = b'\xff\xfeH\x00e\x00l\x00l\x00o\x00' # UTF-16 encoded
    try:
        # Trying to decode UTF-16 bytes as UTF-8 will fail
        bad_bytes.decode('utf-8')
    except UnicodeDecodeError as e:
        print(f"Failed to decode with UTF-8: {e}")
        
    # Correct decoding
    correct_decode = bad_bytes.decode('utf-16')
    print(f"Correctly decoded with UTF-16: '{correct_decode}'")


if __name__ == "__main__":
    main()
