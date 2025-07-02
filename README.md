# metasploit_moudle_info_collect

### 🚀 About
> [!IMPORTANT]\
> A repository collecting Metasploit module information

### Metasploit

#### 1.Install Required Packages
```bash
# Validated Versions: pymetasploit3-1.0.6
pip install pymetasploit3 
```

#### 2.Load msgrpc
```
$ msfconsole
msf> load msgrpc [Pass=yourpassword]
[*] MSGRPC Service:  127.0.0.1:55552 
[*] MSGRPC Username: msf
[*] MSGRPC Password: glycNshR
[*] Successfully loaded plugin: msgrpc
```

#### 3.Key Design
> [!NOTE]\
> To enhance the accuracy of information collection, two verification mechanisms were implemented:
    Empty File Check
        Detects and excludes empty files to prevent data loss caused by untimely responses.
    Duplicate Collection Check
        Identifies repeated data captures within the same document to reduce redundant processing.
Additionally, to mitigate connection overload:
    Collections are processed in batches of 30 entries
    A connection reset pause is triggered between batches.
