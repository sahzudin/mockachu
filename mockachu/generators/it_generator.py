from random import choice, randint, getrandbits, choices
from .generator import Generator, GeneratorActionParameters, GeneratorActions
from .string_generator import StringNumberGenerator
import ipaddress
import hashlib
import string
import socket
import struct
import uuid
import time
import ulid
from ..services.file_reader import read_resource_file_lines


class ItGenerator(Generator):
    """Generator for IT and technology-related mock data.
    
    Provides generation of various IT-related data including IP addresses,
    MAC addresses, domain names, URLs, UUIDs, hash values, email addresses,
    phone numbers, and usernames. Supports both IPv4 and IPv6 addresses,
    various hash algorithms, and different identifier formats.
    """
    
    def get_actions(self):
        """Get the list of supported generator actions.
        
        Returns:
            list: List of GeneratorActions for IT data generation
        """
        return [
            GeneratorActions.RANDOM_IPV4,
            GeneratorActions.RANDOM_PRIVATE_IPV4,
            GeneratorActions.RANDOM_PUBLIC_IPV4,
            GeneratorActions.RANDOM_IPV6,
            GeneratorActions.RANDOM_MAC_ADDRESS,
            GeneratorActions.RANDOM_DOMAIN,
            GeneratorActions.RANDOM_URL,
            GeneratorActions.RANDOM_KNOWN_URL,
            GeneratorActions.RANDOM_UUID_UPPERCASE,
            GeneratorActions.RANDOM_UUID_LOWERCASE,
            GeneratorActions.RANDOM_ULID,
            GeneratorActions.RANDOM_MD5,
            GeneratorActions.RANDOM_SHA1,
            GeneratorActions.RANDOM_SHA256,
            GeneratorActions.RANDOM_SHA512,
            GeneratorActions.RANDOM_MONGODB_OBJECT_ID,
            GeneratorActions.RANDOM_EMAIL,
            GeneratorActions.RANDOM_PHONE_NUMBER,
            GeneratorActions.RANDOM_USERNAME,
        ]

    def get_parameters(self, action):
        match action:
            case GeneratorActions.RANDOM_PHONE_NUMBER:
                return [GeneratorActionParameters.PATTERN.name]
        return []

    def get_keys(self):
        """Get the data keys that this generator can produce.
        
        Returns:
            list: List of data keys from parent class
        """
        return super().get_keys()

    def generate(self, action, *args):
        """Generate IT and technology data based on the specified action.
        
        Args:
            action (GeneratorActions): The type of IT data to generate
            *args: Additional arguments (not used by most IT actions)
            
        Returns:
            str: Generated IT data (IP address, UUID, hash, email, etc.)
        """
        match action:
            case GeneratorActions.RANDOM_IPV4:
                return self.__generate_random_ipv4()
            case GeneratorActions.RANDOM_PRIVATE_IPV4:
                return self.__generate_random_private_ipv4()
            case GeneratorActions.RANDOM_PUBLIC_IPV4:
                return self.__generate_random_public_ipv4()
            case GeneratorActions.RANDOM_IPV6:
                return self.__generate_random_ipv6()
            case GeneratorActions.RANDOM_MAC_ADDRESS:
                return self.__generate_random_mac_address()
            case GeneratorActions.RANDOM_DOMAIN:
                return self.__generate_random_domain()
            case GeneratorActions.RANDOM_URL:
                return self.__generate_random_url()
            case GeneratorActions.RANDOM_KNOWN_URL:
                return self.__generate_random_known_url()
            case GeneratorActions.RANDOM_UUID_UPPERCASE:
                return self.__generate_random_uuid_uppercase()
            case GeneratorActions.RANDOM_UUID_LOWERCASE:
                return self.__generate_random_uuid_lowercase()
            case GeneratorActions.RANDOM_ULID:
                return self.__generate_random_ulid()
            case GeneratorActions.RANDOM_MD5:
                return self.__generate_random_md5()
            case GeneratorActions.RANDOM_SHA1:
                return self.__generate_random_sha1()
            case GeneratorActions.RANDOM_SHA256:
                return self.__generate_random_sha256()
            case GeneratorActions.RANDOM_SHA512:
                return self.__generate_random_sha512()
            case GeneratorActions.RANDOM_MONGODB_OBJECT_ID:
                return self.__generate_random_mongodb_objectid()
            case GeneratorActions.RANDOM_EMAIL:
                return self.__generate_random_email()
            case GeneratorActions.RANDOM_PHONE_NUMBER:
                return self.__generate_random_phone_number() if super().args_empty(args) else self.__generate_random_phone_number(args[0])
            case GeneratorActions.RANDOM_USERNAME:
                return self.__generate_random_username()

    __random_string_generator = None
    __usernames = []
    __most_visited_websites = []

    def __init__(self):
        self.__random_string_generator = StringNumberGenerator()
        self.__usernames = read_resource_file_lines("usernames.txt")
        self.__most_visited_websites = read_resource_file_lines(
            "websites.txt")
        self.__popular_email_domains = read_resource_file_lines(
            "email_domains.txt")
        self.__top_level_domains = ["com", "org", "net", "gov", "edu", "mil"]

    def __generate_random_ipv4(self):
        return socket.inet_ntoa(struct.pack('>I', randint(1, 0xFFFFFFFF)))

    def __generate_random_private_ipv4(self):
        return f"10.{randint(0, 255)}.{randint(0, 255)}.{randint(0, 255)}"

    def __generate_random_public_ipv4(self):
        return f"203.0.113.{randint(0, 255)}"

    def __generate_random_ipv6(self):
        return str(ipaddress.IPv6Address(getrandbits(128)))

    def __generate_random_mac_address(self):
        mac_bytes = [randint(0x00, 0xff) for _ in range(6)]
        mac_address = ':'.join(f'{byte:02x}' for byte in mac_bytes)
        return mac_address

    def __generate_random_domain(self):
        return choice(self.__top_level_domains)

    def __generate_random_url(self):
        protocols = ["http", "https"]
        protocol = choice(protocols)
        domain = ''.join(choices(
            string.ascii_lowercase, k=randint(5, 10)))
        path = '/'.join(''.join(choices(string.ascii_lowercase + string.digits,
                        k=randint(2, 5))) for _ in range(randint(1, 3)))
        query_params = '&'.join(
            f'{"".join(choices(string.ascii_lowercase, k=randint(2, 5)))}={"".join(choices(string.ascii_lowercase + string.digits, k=randint(2, 5)))}' for _ in range(randint(0, 3)))
        fragment = ''.join(choices(
            string.ascii_lowercase + string.digits, k=randint(2, 5)))

        url = f"{protocol}://{domain}/{path}?{query_params}#{fragment}"
        return url

    def __generate_random_known_url(self):
        return choice(self.__most_visited_websites)

    def __generate_random_uuid_uppercase(self):
        return str(uuid.uuid4()).upper()

    def __generate_random_uuid_lowercase(self):
        return str(uuid.uuid4()).lower()

    def __generate_random_ulid(self):
        return str(ulid.ulid())

    def __generate_random_md5(self):
        hash = hashlib.md5()
        hash.update(
            self.__random_string_generator.generate(GeneratorActions.RANDOM_ALPHABETICAL_LOWERCASE_STRING, 20).encode('utf-8'))
        return hash.hexdigest()

    def __generate_random_sha1(self):
        hash = hashlib.sha1()
        hash.update(
            self.__random_string_generator.generate(GeneratorActions.RANDOM_ALPHABETICAL_LOWERCASE_STRING, 20).encode('utf-8'))
        return hash.hexdigest()

    def __generate_random_sha256(self):
        hash = hashlib.sha256()
        hash.update(
            self.__random_string_generator.generate(GeneratorActions.RANDOM_ALPHABETICAL_LOWERCASE_STRING, 20).encode('utf-8'))
        return hash.hexdigest()

    def __generate_random_sha512(self):
        hash = hashlib.sha512()
        hash.update(
            self.__random_string_generator.generate(GeneratorActions.RANDOM_ALPHABETICAL_LOWERCASE_STRING, 20).encode('utf-8'))
        return hash.hexdigest()

    def __generate_random_mongodb_objectid(self):
        # Generate a MongoDB-like ObjectId without requiring bson library
        # ObjectId format: 4-byte timestamp + 5-byte random + 3-byte counter
        timestamp = int(time.time()).to_bytes(4, 'big')
        random_bytes = getrandbits(5 * 8).to_bytes(5, 'big')
        counter = randint(0, 16777215).to_bytes(3, 'big')  # 3 bytes = 24 bits = 16777215 max
        object_id = timestamp + random_bytes + counter
        return object_id.hex()

    def __generate_random_email(self):
        return choice(self.__usernames) + "." + choice(self.__usernames) + "@" + choice(self.__popular_email_domains)

    def __generate_random_phone_number(self, pattern):
        if pattern is None:
            pattern = '+1-___-___-____'
        return ''.join(choice('0123456789') if ch == '_' else ch for ch in pattern)

    def __generate_random_username(self):
        return choice(self.__usernames) + "." + choice(self.__usernames)

    def get_pattern_example(self, action):

        if action == GeneratorActions.RANDOM_PHONE_NUMBER:
            return "+1-___-___-____"
        return "Enter pattern..."
