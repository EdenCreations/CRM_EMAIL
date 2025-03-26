import re
import socket
import dns.resolver

class EmailVerifier:
    """Basic email verification functionality."""
    
    def __init__(self):
        self.email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    def verify_syntax(self, email):
        """Verify that the email has valid syntax."""
        return bool(self.email_regex.match(email))
    
    def verify_domain(self, domain):
        """Verify that the domain has valid MX records."""
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            return len(mx_records) > 0
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.Timeout):
            return False
        except Exception:
            return False
    
    def rank_candidates(self, candidates, domain, storage):
        """Rank email candidates based on domain patterns and basic verification."""
        # Get domain patterns from storage
        domain_patterns = storage.get_domain_patterns(domain)
        pattern_weights = {pattern: count for pattern, count in domain_patterns}
        
        # If we have no patterns for this domain, all candidates have equal weight
        if not pattern_weights:
            pattern_weights = {pattern: 1 for pattern in [
                "{first}.{last}@{domain}",
                "{first}{last}@{domain}",
                "{first}_{last}@{domain}",
                "{f}.{last}@{domain}",
                "{flast}@{domain}",
                "{first}.{l}@{domain}",
                "{firstl}@{domain}",
                "{first}@{domain}",
                "{last}@{domain}"
            ]}
        
        # Check domain validity once
        domain_valid = self.verify_domain(domain)
        
        # Rank candidates
        ranked_candidates = []
        for email in candidates:
            # Skip invalid syntax
            if not self.verify_syntax(email):
                continue
                
            # Extract pattern from email
            local_part = email.split('@')[0]
            first_name = email.split('@')[0].split('.')[0] if '.' in local_part else local_part
            
            # Find matching pattern
            matching_pattern = None
            for pattern in pattern_weights:
                if pattern.startswith("{first}.{last}") and '.' in local_part:
                    matching_pattern = "{first}.{last}@{domain}"
                elif pattern.startswith("{first}{last}") and not '.' in local_part and not '_' in local_part:
                    matching_pattern = "{first}{last}@{domain}"
                # Add more pattern matching logic here
            
            # Calculate confidence score
            confidence = 0.0
            if matching_pattern:
                # Base confidence on pattern frequency
                pattern_count = pattern_weights.get(matching_pattern, 0)
                total_count = sum(pattern_weights.values())
                confidence = pattern_count / total_count if total_count > 0 else 0.5
            else:
                confidence = 0.3  # Default confidence for unknown patterns
                
            # Adjust confidence based on domain validity
            if domain_valid:
                confidence *= 1.2
            else:
                confidence *= 0.5
                
            # Cap confidence at 0.95
            confidence = min(confidence, 0.95)
            
            ranked_candidates.append((email, confidence))
        
        # Sort by confidence score
        ranked_candidates.sort(key=lambda x: x[1], reverse=True)
        return ranked_candidates 