import datetime
import os
import struct
import sys
from simpledbf import Dbf5

class Dbf3(Dbf5):
   def __init__(self, dbf, codec='utf-8'):
       super().__init__(dbf, codec)

   def _get_recs(self, chunk=None):
        '''Generator that returns individual records.

        Parameters
        ----------
        chunk : int, optional
            Number of records to return as a single chunk. Default 'None',
            which uses all records.
        '''
        if chunk == None:
            chunk = self.numrec

        for i in range(chunk):
            # Extract a single record
            record = struct.unpack(self.fmt, self.f.read(self.fmtsiz))
            # If delete byte is not a space, record was deleted so skip
            if record[0] != b' ':
                continue

            # Save the column types for later
            self._dtypes = {}
            result = []
            for idx, value in enumerate(record):
                name, typ, size = self.fields[idx]
                if name == 'DeletionFlag':
                    continue

                # String (character) types, remove excess white space
                if typ == "C":
                    if name not in self._dtypes:
                        self._dtypes[name] = "str"
                    value = value.strip()
                    # Convert empty strings to NaN
                    if value == b'':
                        value = self._na
                    else:
                        value = value.decode(self._enc)
                        # Escape quoted characters
                        if self._esc:
                            value = value.replace('"', self._esc + '"')

                # Numeric type. Stored as string
                elif typ == "N":
                    # A decimal should indicate a float
                    if b'.' in value:
                        if name not in self._dtypes:
                            self._dtypes[name] = "float"
                        value = float(value)
                    # No decimal, probably an integer, but if that fails,
                    # probably NaN
                    else:
                        try:
                            value = int(value)
                            if name not in self._dtypes:
                                self._dtypes[name] = "int"
                        except:
                            # I changed this for SQL->Pandas conversion
                            # Otherwise floats were not showing up correctly
                            value = float('nan')

                # Date stores as string "YYYYMMDD", convert to datetime
                elif typ == 'D':
                    try:
                        y, m, d = int(value[:4]), int(value[4:6]), \
                                  int(value[6:8])
                        if name not in self._dtypes:
                            self._dtypes[name] = "date"
                    except:
                        value = self._na
                    else:
                        value = datetime.date(y, m, d)

                # Booleans can have multiple entry values
                elif typ == 'L':
                    if name not in self._dtypes:
                        self._dtypes[name] = "bool"
                    if value in b'TyTt':
                        value = True
                    elif value in b'NnFf':
                        value = False
                    # '?' indicates an empty value, convert this to NaN
                    else:
                        value = self._na

                # Floating points are also stored as strings.
                elif typ == 'F':
                    if name not in self._dtypes:
                        self._dtypes[name] = "float"
                    try:
                        value = float(value)
                    except:
                        value = float('nan')

                elif typ == 'M':
                   value = self._na

                else:
                    err = 'Column type "{}" not yet supported.'
                    raise ValueError(err.format(value))

                result.append(value)
            yield result

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python dbf3_convert_to_csv.py <input.dbf>")
        sys.exit(1)

    input_name = sys.argv[1]
    output_name = os.path.splitext(input_name)[0] + ".csv"

    dbf = Dbf3(input_name)
    dbf.to_csv(output_name)
    print(f"Conversion complete: {output_name}")