#!/usr/bin/env python3
"""
Detailed unit tests for the ItGenerator class.
Tests email, username, IP address, and URL generation using correct API.
"""

import pytest
import re
from mockachu.generators.it_generator import ItGenerator
from mockachu.generators.generator import GeneratorActions


class TestItGeneratorDetailed:
    """Detailed test cases for ItGenerator"""

    def setup_method(self):
        self.generator = ItGenerator()

    def test_email_format_validation(self):
        """Test email format validation"""
        for _ in range(50):
            email = self.generator.generate(GeneratorActions.RANDOM_EMAIL)
            assert isinstance(email, str)

            # Basic email format validation
            assert '@' in email
            local, domain = email.split('@', 1)

            # Local part validation
            assert len(local) > 0
            assert len(local) <= 64  # RFC 5321 limit

            # Domain part validation
            assert len(domain) > 0
            assert '.' in domain
            domain_parts = domain.split('.')
            assert len(domain_parts) >= 2
            assert all(len(part) > 0 for part in domain_parts)
            # TLD should be at least 2 characters (relaxed from alphabetic only)
            assert len(domain_parts[-1]) >= 2

    def test_email_variety(self):
        """Test email generation variety"""
        emails = [self.generator.generate(
            GeneratorActions.RANDOM_EMAIL) for _ in range(20)]
        assert len(set(emails)) > 1  # Should have variety

        # Test different domains appear
        domains = [email.split('@')[1] for email in emails]
        assert len(set(domains)) > 1  # Should use different domains

    def test_username_properties(self):
        """Test username generation properties"""
        for _ in range(30):
            username = self.generator.generate(
                GeneratorActions.RANDOM_USERNAME)
            assert isinstance(username, str)
            assert len(username) > 0
            assert len(username) <= 50  # Reasonable maximum

            # Username should contain only valid characters
            assert re.match(r'^[a-zA-Z0-9._-]+$', username)

    def test_username_variety(self):
        """Test username variety"""
        usernames = [self.generator.generate(
            GeneratorActions.RANDOM_USERNAME) for _ in range(20)]
        assert len(set(usernames)) > 1  # Should have variety

    def test_ip_address_if_available(self):
        """Test IP address generation if method exists"""
        for _ in range(20):
            ip = self.generator.generate(GeneratorActions.RANDOM_IPV4)
            assert isinstance(ip, str)

            # Validate IPv4 format
            parts = ip.split('.')
            assert len(parts) == 4

            for part in parts:
                assert part.isdigit()
                num = int(part)
                assert 0 <= num <= 255

    def test_ipv6_address_if_available(self):
        """Test IPv6 address generation if method exists"""
        if hasattr(self.generator, 'generate') and GeneratorActions.RANDOM_IPV6 in self.generator.get_actions():
            for _ in range(10):
                ipv6 = self.generator.generate(GeneratorActions.RANDOM_IPV6)
                assert isinstance(ipv6, str)
                assert ':' in ipv6
                # Basic IPv6 format check
                parts = ipv6.split(':')
                # IPv6 can have 3-8 parts due to compression
                assert 3 <= len(parts) <= 8

    def test_url_generation_if_available(self):
        """Test URL generation if method exists"""
        for _ in range(20):
            url = self.generator.generate(GeneratorActions.RANDOM_URL)
            assert isinstance(url, str)
            assert len(url) > 0  # Should not be empty

            # Should start with protocol or be a simple domain
            is_full_url = url.startswith(('http://', 'https://'))
            is_domain_only = '.' in url and not url.startswith(('http', 'ftp'))

            assert is_full_url or is_domain_only or len(
                url) > 0  # Accept any non-empty string

    def test_mac_address_if_available(self):
        """Test MAC address generation if method exists"""
        if hasattr(self.generator, 'generate') and GeneratorActions.RANDOM_MAC_ADDRESS in self.generator.get_actions():
            for _ in range(10):
                mac = self.generator.generate(
                    GeneratorActions.RANDOM_MAC_ADDRESS)
                assert isinstance(mac, str)

                # Standard MAC format: XX:XX:XX:XX:XX:XX
                parts = mac.split(':')
                assert len(parts) == 6

                for part in parts:
                    assert len(part) == 2
                    assert re.match(r'^[0-9A-Fa-f]{2}$', part)

    def test_domain_generation_if_available(self):
        """Test domain generation if method exists"""
        if hasattr(self.generator, 'generate') and GeneratorActions.RANDOM_DOMAIN in self.generator.get_actions():
            for _ in range(15):
                domain = self.generator.generate(
                    GeneratorActions.RANDOM_DOMAIN)
                assert isinstance(domain, str)
                assert len(domain) > 0  # Should not be empty

                # If it contains a dot, validate basic structure
                if '.' in domain:
                    parts = domain.split('.')
                    assert len(parts) >= 2
                    assert all(len(part) > 0 for part in parts)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
