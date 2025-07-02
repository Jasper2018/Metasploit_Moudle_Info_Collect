**exploit_payload_map_info_collect**: Create mappings between Metasploit exploits and payloads.

**auxiliary_scanner_info_collect**: Collects information for auxiliary/scanner modules.

**payload_info_collect**:Gathers payload module information(.txt).

**payload_html_info_collect**:Gathers payload module information(.html).

Overall approach:
- `Retrieve all single name from moudle`
- `Get info / info -d for each moudle`
- `Process in loop and aggregate results`
- `Output real-time progress information`
