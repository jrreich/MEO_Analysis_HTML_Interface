
class beacon(object):
    def __init__(self, hexdata):
        """Return a new beacon object."""
        scale = 16
        num_of_bits = 4*len(hexdata)
        self.format = None
        self.protocol_1 = None
        self.country_code = None
        self.protocol_2 = None
        self.protocol = None
        self.serial = None
        self.lat = None
        self.lon = None
        binary1 = bin(int(hexdata, scale))[2:].zfill(num_of_bits)
        self.bcnID15 = hex(int(binary1[1:61],2))[2:-1]
        if len(hexdata) == 30:
            self.format = binary1[0]
            self.protocol_1 = binary1[1]
            self.country_code = binary1[2:12]
            if self.format == '1': #long format

                if self.protocol_1 == '0': # location protocol
                    self.lat_NS = binary1[40]
                    self.lat_deg_bin = binary1[41:48] + binary1[48:50]
                    if self.lat_deg_bin == '111111111':
                        self.lat_deg = None
                    else:
                        self.lat_deg  = int(binary1[41:48],2)+float(int(binary1[48:50],2))/4
                        self.lat_fine_sign = binary1[88]
                        self.lat_fine_delta_min = int(binary1[89:94],2)
                        self.lat_fine_delta_sec = int(binary1[94:98],2)*4
                        self.lat_delta = float(self.lat_fine_delta_min*60 + self.lat_fine_delta_sec)/3600
                        self.lat = (self.lat_deg - self.lat_delta) if self.lat_fine_sign == '0' else (self.lat_deg + self.lat_delta)
                        if self.lat_NS == '1': self.lat = -self.lat 

                    self.lon_EW = binary1[50]
                    self.lon_deg_bin = binary1[51:59] + binary1[59:61]
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

                    self.protocol_2 = binary1[12:16]

                    if self.protocol_2 == '0010':
                        self.protocol = 'EPIRB - MMSI/Location Protocol'
                    if self.protocol_2 == '0011':
                        self.protocol = 'ELT - 24-bit Address/Location Protocol'
                    if self.protocol_2 == '0100':
                        self.protocol = 'ELT - serial'
                    if self.protocol_2 == '0101':
                        self.protocol = 'ELT - aircraft operator designator'
                    if self.protocol_2 == '0110':
                        self.protocol = 'EPIRB-serial'
                    if self.protocol_2 == '0111':
                        self.protocol = 'PLB-serial'
                    if self.protocol_2 == '1100':
                        self.protocol = 'Ship Security'
                    if self.protocol_2 == '1000':
                        self.protocol = 'ELT - National Location Protocol'
                    if self.protocol_2 == '1010':
                        self.protocol = 'EPIRB - National Location Protocol'
                    if self.protocol_2 == '1011':
                        self.protocol = 'PLB - National Location Protocol'
                    if self.protocol_2 == '1110':
                        self.protocol = 'Standard Test Location Protocol'
                    if self.protocol_2 == '1111':
                        self.protocol = 'National Test Location Protocol'
                    if self.protocol_2 == '1101':
                        self.protocol = 'RLS Location Protocol'
                    if self.protocol_2 == '0000':
                        self.protocol = 'Orbitography'
                    if self.protocol_2 == '0001':
                        self.protocol = 'Orbitography'
                    if self.protocol_2 == '1001':
                        self.protocol = 'Spare'

                if self.protocol_1 == '1': # User Protocols
                    self.lat_NS = binary1[83]
                    self.lat_deg = binary1[84:91]
                    self.lat_min = binary1[91:95]
                    self.lon_EW = binary1[95]
                    self.lon_deg = binary1[96:104]
                    self.lon_min = binary1[104:109]

                    self.protocol_2 = binary1[12:15]

                    if self.protocol_2 == '010':
                        self.protocol = 'EPIRB - Maritime User'
                    if self.protocol_2 == '110':
                        self.protocol = 'EPIRB - Radio Call Sign'
                    if self.protocol_2 == '001':
                        self.protocol = 'ELT - Aviation User Protocol'
                    if self.protocol_2 == '011':
                        self.protocol = 'Serial User Protocol'
                        if binary1[15:18] == '000':
                            self.protocol = 'ELT - serial'
                        if binary1[15:18] == '001':
                            self.protocol = 'ELT - aircraft operator designator & serial number'
                        if binary1[15:18] == '010':
                            self.protocol = 'float free EPIRB with serial identification number'
                        if binary1[15:18] == '100':
                            self.protocol = 'non float free EPIRB with serial identification number'                        
                        if binary1[15:18] == '110':
                            self.protocol = 'PLBs with serial identification number'    
                        if binary1[15:18] == '011':
                            self.protocol = 'ELT with aircraft 24-bit address' 
                        if binary1[15:18] == '101':
                            self.protocol = 'Spare'   
                        if binary1[15:18] == '111':
                            self.protocol = 'Spare'   
                        if binary1[18] == '0':
                            self.serial = 'Nationally assigned'      
                        if binary1[18] == '1':
                            self.serial = 'ID includes TAC'
                    if self.protocol_2 == '111':
                        self.protocol = 'Test User Protocol'      
                    if self.protocol_2 == '000':
                        self.protocol = 'Orbitography Protocol'      
                    if self.protocol_2 == '100':
                        self.protocol = 'National User Protocol'   
                    if self.protocol_2 == '101':
                        self.protocol = 'Spare'      