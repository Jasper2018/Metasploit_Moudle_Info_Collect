# Metasploit Moudle Info Collect
![logo](https://github.com/Jasper2018/metasploit_moudle_info_collect/blob/main/logo.png)

> [!IMPORTANT]\
> A repository collecting Metasploit module information, primarily used to gather description text/html data of modules, capable of supporting applications like large language models (LLMs) by providing data support.

### Configuration

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
> To enhance the accuracy of information collection, Three verification mechanisms were implemented:
> 1. **Empty File Check**: Detects and excludes empty files to prevent data loss caused by untimely responses.
> 2. **Duplicate Collection Check**: Identifies repeated data captures within the same document to reduce redundant processing.
> 3. **Mitigate connection overload**:
>  - `Collections are processed in batches of 30 entries`
>  - `A connection reset pause is triggered between batches.`
