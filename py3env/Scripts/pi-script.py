#!c:\users\jrrei\source\repos\meo_analysis_html_interface\py3env\scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'pi==0.1.2','console_scripts','pi'
__requires__ = 'pi==0.1.2'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('pi==0.1.2', 'console_scripts', 'pi')()
    )
