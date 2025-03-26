class PatternGenerator:
    """Generate email address patterns based on first name, last name and domain."""
    
    def __init__(self):
        self.patterns = [
            "{first}.{last}@{domain}",
            "{first}{last}@{domain}",
            "{first}_{last}@{domain}",
            "{f}.{last}@{domain}",
            "{flast}@{domain}",
            "{first}.{l}@{domain}",
            "{firstl}@{domain}",
            "{first}@{domain}",
            "{last}@{domain}"
        ]
    
    def generate_candidates(self, first_name, last_name, domain):
        """Generate all possible email patterns for the given inputs."""
        first_name = first_name.lower()
        last_name = last_name.lower()
        domain = domain.lower()
        
        candidates = []
        
        for pattern in self.patterns:
            email = pattern.format(
                first=first_name,
                last=last_name,
                domain=domain,
                f=first_name[0] if first_name else "",
                l=last_name[0] if last_name else "",
                flast=first_name[0] + last_name if first_name and last_name else "",
                firstl=first_name + last_name[0] if first_name and last_name else ""
            )
            candidates.append(email)
            
        return candidates 