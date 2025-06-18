class SemVer:
    def __init__(self, major, minor, patch, pre_release=None):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.pre_release = pre_release

    @classmethod
    def from_string(cls, version_str):
        version_parts = version_str.split(".")
        major = int(version_parts[0])
        minor = int(version_parts[1])
        patch_and_pre_release = version_parts[2]
        
        pre_release = None
        if "-" in patch_and_pre_release:
            patch, pre_release = patch_and_pre_release.split("-")
            # Split pre-release into parts if it contains dots
            pre_release = pre_release.split(".")
        else:
            patch = patch_and_pre_release
        patch = int(patch)
        return cls(major, minor, patch, pre_release)
    
    def __str__(self):
        version_str = f"{self.major}.{self.minor}.{self.patch}"
        if self.pre_release:
            version_str += "-" + ".".join(self.pre_release)
        return version_str

    def __repr__(self):
        return f"SemVer({self.major}, {self.minor}, {self.patch}, {self.pre_release})"

    def __eq__(self, other):
        if isinstance(other, SemVer):
            return (self.major, self.minor, self.patch, self.pre_release) == (
                other.major,
                other.minor,
                other.patch,
                other.pre_release,
            )
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, SemVer):
            # Compare version numbers first
            if (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch):
                return True
            elif (self.major, self.minor, self.patch) > (other.major, other.minor, other.patch):
                return False
            # If version numbers are equal, consider pre-release
            else:
                if self.pre_release and not other.pre_release:
                    return True  # Pre-release is less than release
                elif not self.pre_release and other.pre_release:
                    return False  # Release is greater than pre-release
                elif self.pre_release and other.pre_release:
                    return self.pre_release < other.pre_release
                else:  # Both are releases or both are None
                    return False  # Equal versions
        return NotImplemented
      
    def __gt__(self, other):
        if isinstance(other, SemVer):
            # Compare version numbers first
            if (self.major, self.minor, self.patch) > (other.major, other.minor, other.patch):
                return True
            elif (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch):
                return False
            # If version numbers are equal, consider pre-release
            else:
                if self.pre_release and not other.pre_release:
                    return False  # Pre-release is less than release
                elif not self.pre_release and other.pre_release:
                    return True  # Release is greater than pre-release
                elif self.pre_release and other.pre_release:
                    return self.pre_release > other.pre_release
                else:  # Both are releases or both are None
                    return False  # Equal versions
        return NotImplemented
    
    # Add these for complete comparison operations
    def __le__(self, other):
        return self < other or self == other
        
    def __ge__(self, other):
        return self > other or self == other

    def increment_major(self):
        self.major += 1
        self.minor = 0
        self.patch = 0
        self.pre_release = None

    def increment_minor(self):
        self.minor += 1
        self.patch = 0
        self.pre_release = None

    def increment_patch(self):
        self.patch += 1
        self.pre_release = None

    def set_pre_release(self, pre_release):
        self.pre_release = pre_release

if __name__ == "__main__":
    # Test cases
    cv = SemVer.from_string('0.7.0')
    nv = SemVer.from_string('0.7.0')
    print(f"cv: {cv}, nv: {nv}")
    print(f"cv < nv: {cv < nv}")  # Should be False
    print(f"cv > nv: {cv > nv}")  # Should be False
    print(f"cv == nv: {cv == nv}")  # Should be True
    
    # Additional test cases
    v1 = SemVer.from_string('1.0.0')
    v2 = SemVer.from_string('1.1.0')
    v3 = SemVer.from_string('1.0.1')
    v4 = SemVer.from_string('1.0.0-alpha')
    v5 = SemVer.from_string('1.0.0-beta')
    
    print("\nAdditional test cases:")
    print(f"1.0.0 < 1.1.0: {v1 < v2}")  # Should be True
    print(f"1.0.0 < 1.0.1: {v1 < v3}")  # Should be True
    print(f"1.0.0-alpha < 1.0.0: {v4 < v1}")  # Should be True
    print(f"1.0.0-alpha < 1.0.0-beta: {v4 < v5}")  # Should be True