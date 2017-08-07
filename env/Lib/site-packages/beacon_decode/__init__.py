
class beacon(object):
    def __init__(self, hexdata):
        """Return a new beacon object."""
        scale = 16
        num_of_bits = 4*len(hexdata)
        self.format_flag = None
        self.protocol_flag = None
        self.country_code = None
        self.protocol_code = None
        self.protocol = None
        self.serial = None
        self.lat = None
        self.lon = None
        binary1 = bin(int(hexdata, scale))[2:].zfill(num_of_bits)
    


        if len(hexdata) == 30:
            self.format_flag = binary1[0]
            self.protocol_flag = binary1[1]
            self.country_code = binary1[2:12]
            self.bcnID15 = hex(int(binary1[1:61],2))[2:-1]
            if self.format_flag == '1': #long format_flag
                if self.protocol_flag == '0': # location protocol
                    self.protocol_code = binary1[12:16]
                    if self.protocol_code == '0010':
                        self.protocol = 'EPIRB - MMSI/Location Protocol'
                        beacon.standard_location_protocol(self,binary1)
                    if self.protocol_code == '0011':
                        self.protocol = 'ELT - 24-bit Address/Location Protocol'
                        beacon.standard_location_protocol(self,binary1)
                    if self.protocol_code == '0100':
                        self.protocol = 'ELT - serial'
                        beacon.standard_location_protocol(self,binary1)
                    if self.protocol_code == '0101':
                        self.protocol = 'ELT - aircraft operator designator'
                        beacon.standard_location_protocol(self,binary1)
                    if self.protocol_code == '0110':
                        self.protocol = 'EPIRB-serial'
                        beacon.standard_location_protocol(self,binary1)
                    if self.protocol_code == '0111':
                        self.protocol = 'PLB-serial'
                        beacon.standard_location_protocol(self,binary1)
                    if self.protocol_code == '1100':
                        self.protocol = 'Ship Security'
                        beacon.standard_location_protocol(self,binary1)
                    if self.protocol_code == '1000':
                        self.protocol = 'ELT - National Location Protocol'
                        beacon.national_location_protocol(self,binary1)
                    if self.protocol_code == '1010':
                        self.protocol = 'EPIRB - National Location Protocol'
                        beacon.national_location_protocol(self,binary1)
                    if self.protocol_code == '1011':
                        self.protocol = 'PLB - National Location Protocol'
                        beacon.national_location_protocol(self,binary1)
                    if self.protocol_code == '1110':
                        self.protocol = 'Standard Test Location Protocol'
                        beacon.standard_location_protocol(self,binary1)
                    if self.protocol_code == '1111':
                        self.protocol = 'National Test Location Protocol'
                        beacon.national_location_protocol(self,binary1)
                    if self.protocol_code == '1101':
                        self.protocol = 'RLS Location Protocol'
                    if self.protocol_code == '0000':
                        self.protocol = 'Orbitography'
                    if self.protocol_code == '0001':
                        self.protocol = 'Orbitography'
                    if self.protocol_code == '1001':
                        self.protocol = 'Spare'

                if self.protocol_flag == '1': # User Protocols
                    self.protocol_code = binary1[12:15]
                    if self.protocol_code == '010':
                        self.protocol = 'EPIRB - Maritime User'
                        beacon.user_location_protocol(self,binary1)
                    if self.protocol_code == '110':
                        self.protocol = 'EPIRB - Radio Call Sign'
                        beacon.user_location_protocol(self,binary1)
                    if self.protocol_code == '001':
                        self.protocol = 'ELT - Aviation User Protocol'
                        self.aircraft_id_bin = binary1[15:57]
                        self.radio_locating_bin = binary1[59:61]
                        beacon.user_location_protocol(self,binary1)
                    if self.protocol_code == '111':
                        self.protocol = 'Test User Protocol'
                        beacon.user_location_protocol(self,binary1)
                    if self.protocol_code == '011':
                        self.protocol = 'Serial User Protocol'
                        self.protocol_2_code = binary1[15:18]
                        beacon.user_location_protocol(self,binary1)
                        if self.protocol_2_code == '000':
                            self.protocol = 'ELT - serial'
                        if self.protocol_2_code == '001':
                            self.protocol = 'ELT - aircraft operator designator & serial number'
                        if self.protocol_2_code == '010':
                            self.protocol = 'float free EPIRB with serial identification number'
                        if self.protocol_2_code == '100':
                            self.protocol = 'non float free EPIRB with serial identification number'                        
                        if self.protocol_2_code == '110':
                            self.protocol = 'PLBs with serial identification number'    
                        if self.protocol_2_code == '011':
                            self.protocol = 'ELT with aircraft 24-bit address' 
                        if self.protocol_2_code == '101':
                            self.protocol = 'Spare'   
                        if self.protocol_2_code == '111':
                            self.protocol = 'Spare'   
                        
                        if binary1[18] == '0':
                            self.serial = 'Nationally assigned'      
                        if binary1[18] == '1':
                            self.serial = 'ID includes TAC'
                    if self.protocol_code == '111':
                        self.protocol = 'Test User Protocol'   
                        beacon.user_location_protocol(self,binary1)
                    if self.protocol_code == '000': 
                        self.protocol = 'Orbitography Protocol'      
                    if self.protocol_code == '100':
                        self.protocol = 'National User Protocol'   
                    if self.protocol_code == '101':
                        self.protocol = 'Spare'      

    def standard_location_protocol(self, binary1):
        self.lat_NS = binary1[40]
        self.lat_deg_bin = binary1[41:50]
        if self.lat_deg_bin == '111111111':
            self.lat = None
        else:
            self.lat_deg  = int(binary1[41:48],2)+float(int(binary1[48:50],2))/4
            self.lat_fine_sign = binary1[88]
            self.lat_fine_delta_min = int(binary1[89:94],2)
            self.lat_fine_delta_sec = int(binary1[94:98],2)*4
            self.lat_delta = float(self.lat_fine_delta_min*60 + self.lat_fine_delta_sec)/3600
            self.lat = (self.lat_deg - self.lat_delta) if self.lat_fine_sign == '0' else (self.lat_deg + self.lat_delta)
            if self.lat_NS == '1': self.lat = -self.lat 

        self.lon_EW = binary1[50]
        self.lon_deg_bin = binary1[51:61]
        if self.lon_deg_bin == '1111111111':
            self.lon_deg = None
        else:
            self.lon_deg = int(binary1[51:59],2)+float(int(binary1[59:61],2))/4
            self.lon_fine_sign = binary1[98]
            self.lon_fine_delta_min = int(binary1[99:104],2)
            self.lon_fine_delta_sec = int(binary1[104:108],2)*4
            self.lon_delta = float(self.lon_fine_delta_min*60 + self.lon_fine_delta_sec)/3600
            self.lon = (self.lon_deg - self.lon_delta) if self.lon_fine_sign == '0' else (self.lon_deg + self.lon_delta)
            if self.lon_EW == '1': self.lon = -self.lon

    def national_location_protocol(self, binary1):
        self.lat_NS = binary1[34]
        self.lat_deg_bin = binary1[35:42] 
        self.lat_min_bin = binary1[42:47] 
        if (self.lat_NS + self.lat_deg_bin + self.lat_min_bin) == '0111111100000':
            self.lat_deg = None
        else:
            self.lat_deg  = int(binary1[35:42],2)+float(int(binary1[42:47],2))/30
            if binary1[85] == '1': # if bit 110 = 0, bits 113 - 119 are national use
                if binary1[88:95] == '1001111':
                    self.lat_delta = 0
                    self.lat = self.lat_deg 
                else:
                    self.lat_fine_sign = binary1[88] # 0 = minus, 1 = plus
                    self.lat_fine_delta_min = int(binary1[89:91],2)  
                    self.lat_fine_delta_sec = int(binary1[91:95],2)*4
                    self.lat_delta = float(self.lat_fine_delta_min*60 + self.lat_fine_delta_sec)/3600
                    self.lat = (self.lat_deg - self.lat_delta) if self.lat_fine_sign == '0' else (self.lat_deg + self.lat_delta)
        if self.lat_NS == '1': self.lat = -self.lat 

        self.lon_EW = binary1[47]
        self.lon_deg_bin = binary1[48:56]
        self.lon_min_bin = binary1[56:61]
        if (self.lon_EW + self.lon_deg_bin + self.lon_min_bin) == '01111111100000':
            self.lon_deg = None
        else:
            self.lon_deg  = int(binary1[48:56],2)+float(int(binary1[56:61],2))/30
            if binary1[85] == '1': # if bit 110 = 0, bits 113 - 119 are national use
                if binary1[95:102] == '1001111':
                    self.lon_delta = 0
                    self.lon = self.lon_deg
                else:
                    self.lon_fine_sign = binary1[95] # 0 = minus, 1 = plus
                    self.lon_fine_delta_min = int(binary1[96:98],2)
                    self.lon_fine_delta_sec = int(binary1[98:102],2)*4
                    self.lon_delta = float(self.lon_fine_delta_min*60 + self.lon_fine_delta_sec)/3600
                    self.lon = (self.lon_deg - self.lon_delta) if self.lon_fine_sign == '0' else (self.lon_deg + self.lon_delta)
        if self.lon_EW == '1': self.lon = -self.lon

    def user_location_protocol(self, binary1):
        self.enc_location_source = binary1[82] # 0 = external, 1 = internal
        self.lat_NS = binary1[83]
        self.lat_deg_bin = binary1[84:91] 
        self.lat_min_bin = binary1[91:95] 
        if (self.lat_NS + self.lat_deg_bin + self.lat_min_bin) == '011111110000':
            self.lat = None
        else:
            self.lat  = int(self.lat_deg_bin,2)+float(int(self.lat_min_bin,2))/15
        if self.lat_NS == '1': self.lat = -self.lat 

        self.lon_EW = binary1[95]
        self.lon_deg_bin = binary1[96:104]
        self.lon_min_bin = binary1[104:108]
        if (self.lon_EW + self.lon_deg_bin + self.lon_min_bin) == '0111111110000':
            self.lon = None
        else:
            self.lon  = int(self.lon_deg_bin,2)+float(int(self.lon_min_bin,2))/15
        if self.lon_EW == '1': self.lon = -self.lon