**exploit_payload_mapping_info_collect.py**: Create mappings between Metasploit exploits and payloads.

Overall approach:
    - `Retrieve all exploits`
    - Get payloads for each exploit
    - Process in loop and aggregate results
    - Output real-time progress information
2. **Duplicate Collection Check**: Identifies repeated data captures within the same document to reduce redundant processing.
3. **Mitigate connection overload**:
- `Collections are processed in batches of 30 entries`
- `A connection reset pause is triggered between batches.`
