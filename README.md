cymruwhoisbulk
==============

Description
-----------
A simple script to perform bulk requests to the Cymru WHOIS service  

Usage
-----
```
$ pip install cymruwhoisbulk
$ cymruwhoisbulk -h
usage: cymruwhoisbulk [-h] -i INPUT_FILE [-o OUTPUT_FILE]

version: 1.0

options:
  -h, --help            show this help message and exit

Raw or CSV input parameters:
  -i, --input-file INPUT_FILE
                        Input file as a list of newline-separated IP or FQDN

CSV output parameters:
  -o, --output-file OUTPUT_FILE
                        CSV output file (default: ./resolve_output.csv)


$ cat input.txt
8.8.8.8
1.1.1.1
limpreur.info
bücher.example
belgië.icom.museum

$ cymruwhoisbulk -i input.txt

$ cat resolve_output.csv
"netloc_idna_decoded";"netloc";"ipv4";"ipv4_asn";"ipv4_prefix";"ipv4_owner";"ipv4_cc";"ipv6";"ipv6_asn";"ipv6_prefix";"ipv6_owner";"ipv6_cc"
"1.1.1.1";"1.1.1.1";"1.1.1.1";"13335";"1.1.1.0/24";"CLOUDFLARENET - Cloudflare, Inc., US";"AU";"";"";"";"";""
"8.8.8.8";"8.8.8.8";"8.8.8.8";"15169";"8.8.8.0/24";"GOOGLE - Google LLC, US";"US";"";"";"";"";""
"limpreur.info";"limpreur.info";"";"";"";"";"";"2001:470:1f11:110:fe3d:a4c3:e12b:5d9e";"6939";"2001:470::/32";"HURRICANE - Hurricane Electric LLC, US";"US"
"xn--bcher-kva.example";"bücher.example";"";"";"";"";"";"";"";"";"";""
"xn--belgi-rsa.icom.museum";"belgië.icom.museum";"81.201.190.55";"NA";"NA";"NA";"FR";"";"";"";"";""
```

Changelog
---------
* version 1.0 - 2026-10-20: First commit


Copyright and license
---------------------

All trademarks, service marks, trade names and product names appearing on this repository are the property of their respective owners

cymruwhoisbulk is free software: you can redistribute it and/or modify it under the terms of the MIT licence.  
cymruwhoisbulk is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
  

Contact
-------
* Thomas Debize < tdebize at mail d0t com >