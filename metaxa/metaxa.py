import struct
import xml.etree.ElementTree as ET

class WAVMetadata:
    def __init__(self, filename):
        self.filename = filename
        self.metadata = {}

    def extract(self):
        with open(self.filename, 'rb') as f:
            self._parse_file(f)
        return self.metadata

    def _parse_file(self, f):
        riff = f.read(12)
        if riff[0:4] != b'RIFF' or riff[8:12] != b'WAVE':
            raise ValueError("Not a valid RIFF/WAVE file")

        while True:
            chunk = f.read(8)
            if len(chunk) < 8:
                break  # EOF

            chunk_id, chunk_size = struct.unpack('<4sI', chunk)
            chunk_data = f.read(chunk_size)

            # Handle padding (word alignment)
            if chunk_size % 2 == 1:
                f.read(1)

            handler = getattr(self, f"_handle_{chunk_id.decode('ascii').strip()}", self._handle_unknown)
            handler(chunk_data, chunk_id.decode('ascii').strip())

    def _handle_LIST(self, data, chunk_id):
        list_type = data[0:4].decode('ascii')
        if list_type == 'INFO':
            self.metadata['INFO'] = {}
            offset = 0
            data_without_type = data[4:]
            while offset + 8 <= len(data_without_type):
                sub_id = data_without_type[offset:offset + 4].decode('ascii')
                sub_size = struct.unpack('<I', data_without_type[offset + 4:offset + 8])[0]
                sub_data = data_without_type[offset + 8:offset + 8 + sub_size].decode('utf-8', errors='ignore').rstrip('\x00')
                self.metadata['INFO'][sub_id] = sub_data
                offset += 8 + sub_size
                if sub_size % 2 == 1:
                    offset += 1
        else:
            self.metadata[f'LIST:{list_type}'] = 'Unknown LIST type'

    def _handle_bext(self, data, chunk_id):
        if len(data) < 602:
            self.metadata['bext'] = 'Incomplete bext chunk'
            return
        self.metadata['bext'] = {}
        self.metadata['bext']['description'] = data[0:256].decode('utf-8', errors='ignore').rstrip('\x00')
        self.metadata['bext']['originator'] = data[256:256 + 32].decode('utf-8', errors='ignore').rstrip('\x00')
        self.metadata['bext']['originator_reference'] = data[288:288 + 32].decode('utf-8', errors='ignore').rstrip('\x00')
        self.metadata['bext']['origination_date'] = data[320:320 + 10].decode('ascii', errors='ignore').rstrip('\x00')
        self.metadata['bext']['origination_time'] = data[330:330 + 8].decode('ascii', errors='ignore').rstrip('\x00')

        time_reference_low = struct.unpack('<I', data[338:342])[0]
        time_reference_high = struct.unpack('<I', data[342:346])[0]
        time_reference = (time_reference_high << 32) | time_reference_low
        self.metadata['bext']['time_reference'] = time_reference

        version = struct.unpack('<H', data[346:348])[0]
        self.metadata['bext']['version'] = version

        umid = data[348:348 + 64]
        self.metadata['bext']['umid'] = umid.hex()

        # Reserved (348+64=412), skip 190 reserved bytes (total 602 bytes up to coding history)
        coding_history = data[602:].decode('utf-8', errors='ignore').rstrip('\x00')
        self.metadata['bext']['coding_history'] = coding_history

    def _handle_iXML(self, data, chunk_id):
        try:
            xml_str = data.decode('utf-8', errors='ignore').rstrip('\x00')
            root = ET.fromstring(xml_str)
            self.metadata['iXML'] = self._xml_to_dict(root)

        except Exception as e:
            self.metadata['iXML'] = f"Invalid iXML: {e}"

    def _xml_to_dict(self, element):
        """
        Recursively convert XML tree into nested Python dict.
        """
        node = {}
        # If element has children, recurse
        if len(element):
            for child in element:
                child_dict = self._xml_to_dict(child)
                # Handle multiple children with the same tag as list
                if child.tag in node:
                    if not isinstance(node[child.tag], list):
                        node[child.tag] = [node[child.tag]]
                    node[child.tag].append(child_dict[child.tag])
                else:
                    node.update(child_dict)
        else:
            node[element.tag] = element.text.strip() if element.text else ""
        return {element.tag: node[element.tag] if len(node) == 1 else node}

    def _handle_fmt(self, data, chunk_id):
        # Parse minimum 16 bytes (PCM format)
        if len(data) < 16:
            self.metadata['fmt'] = 'Invalid fmt chunk (too short)'
            return

        fmt_fields = struct.unpack('<HHIIHH', data[:16])
        (
            audio_format,  # 1 = PCM, 3 = IEEE float, 6 = A-law, 7 = μ-law, etc.
            num_channels,
            sample_rate,
            byte_rate,
            block_align,
            bits_per_sample
        ) = fmt_fields

        fmt_info = {
            'audio_format': audio_format,
            'num_channels': num_channels,
            'sample_rate': sample_rate,
            'byte_rate': byte_rate,
            'block_align': block_align,
            'bits_per_sample': bits_per_sample
        }

        # Check for extended fmt chunk (non-PCM)
        if len(data) > 16:
            cb_size = struct.unpack('<H', data[16:18])[0] if len(data) >= 18 else 0
            fmt_info['cb_size'] = cb_size

            if cb_size > 0 and len(data) >= 18 + cb_size:
                ext_data = data[18:18 + cb_size]
                fmt_info['extension'] = ext_data.hex()

        self.metadata['fmt'] = fmt_info

    def _handle_unknown(self, data, chunk_id):
        # If you want to store unknown chunks:
        self.metadata[f'{chunk_id}'] = {}
        self.metadata[f'{chunk_id}']['size'] = f'{len(data)} bytes'
        self.metadata[f'{chunk_id}']['type'] = 'Unknown'

    # Not tested methods

    # def _handle_axml(self, data, chunk_id):
    #     self.metadata['axml'] = data.decode('utf-8', errors='ignore').rstrip('\x00')
    #
    # def _handle_cue(self, data, chunk_id):
    #     num_cue_points = struct.unpack('<I', data[0:4])[0]
    #     cue_points = []
    #     offset = 4
    #     for _ in range(num_cue_points):
    #         fields = struct.unpack('<IIIIIII', data[offset:offset+24])
    #         cue_points.append({
    #             'ID': fields[0],
    #             'position': fields[1],
    #             'data_chunk_id': fields[2],
    #             'chunk_start': fields[3],
    #             'block_start': fields[4],
    #             'sample_offset': fields[5],
    #         })
    #         offset += 24
    #     self.metadata['cue_points'] = cue_points

    # def _handle_smpl(self, data, chunk_id):
    #     # Sample Loop Metadata (simplified)
    #     num_loops = struct.unpack('<I', data[28:32])[0]
    #     loops = []
    #     offset = 36
    #     for _ in range(num_loops):
    #         loop_data = struct.unpack('<IIIIII', data[offset:offset+24])
    #         loops.append({
    #             'identifier': loop_data[0],
    #             'type': loop_data[1],
    #             'start': loop_data[2],
    #             'end': loop_data[3],
    #             'fraction': loop_data[4],
    #             'play_count': loop_data[5],
    #         })
    #         offset += 24
    #     self.metadata['sample_loops'] = loops