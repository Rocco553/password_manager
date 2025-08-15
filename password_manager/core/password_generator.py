import random
import string


class PasswordGenerator:
    def __init__(self):
        pass
    
    def generate_secure_password(self, length=16, use_uppercase=True, use_lowercase=True, 
                                use_numbers=True, use_symbols=True, exclude_ambiguous=True):
        characters = ""
        
        if use_lowercase:
            chars = string.ascii_lowercase
            if exclude_ambiguous:
                chars = chars.replace('l', '').replace('o', '')
            characters += chars
        
        if use_uppercase:
            chars = string.ascii_uppercase
            if exclude_ambiguous:
                chars = chars.replace('I', '').replace('O', '')
            characters += chars
        
        if use_numbers:
            chars = string.digits
            if exclude_ambiguous:
                chars = chars.replace('0', '').replace('1', '')
            characters += chars
        
        if use_symbols:
            safe_symbols = "!@#$%^&*-_=+[]{}|;:,.<>?"
            characters += safe_symbols
        
        if not characters:
            return "Fehler: Keine Zeichen ausgewählt!"
        
        password = ''.join(random.choice(characters) for _ in range(length))
        
        required_chars = []
        if use_lowercase:
            required_chars.append(random.choice(string.ascii_lowercase))
        if use_uppercase:
            required_chars.append(random.choice(string.ascii_uppercase))
        if use_numbers:
            required_chars.append(random.choice(string.digits))
        if use_symbols:
            required_chars.append(random.choice("!@#$%^&*-_=+"))
        
        password_list = list(password)
        for i, req_char in enumerate(required_chars[:len(password_list)]):
            password_list[i] = req_char
        
        random.shuffle(password_list)
        return ''.join(password_list)
    
    def calculate_password_strength(self, password):
        if not password:
            return "Sehr schwach", 0
        
        score = 0
        
        if len(password) >= 12:
            score += 25
        elif len(password) >= 8:
            score += 15
        
        if any(c.islower() for c in password):
            score += 15
        if any(c.isupper() for c in password):
            score += 15
        if any(c.isdigit() for c in password):
            score += 15
        if any(c in "!@#$%^&*-_=+[]{}|;:,.<>?" for c in password):
            score += 20
        
        if len(set(password)) / len(password) > 0.7:
            score += 10
        
        if score >= 85:
            return "Sehr stark", score
        elif score >= 70:
            return "Stark", score
        elif score >= 50:
            return "Mittel", score
        elif score >= 30:
            return "Schwach", score
        else:
            return "Sehr schwach", score