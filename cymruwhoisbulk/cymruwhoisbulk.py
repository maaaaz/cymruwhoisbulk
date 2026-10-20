#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
import csv
import functools
import concurrent.futures
import urllib.parse

import cymruwhois
import pandas as pd
import validators
import dns.resolver
from w3lib.url import safe_url_string

# Script version
VERSION = '1.0'

# Options definition
parser = argparse.ArgumentParser(description="version: " + VERSION)

input_group = parser.add_argument_group('Raw or CSV input parameters')
input_group.add_argument('-i', '--input-file', help='Input file as a list of newline-separated IP or FQDN', default = None, required = True)

output_group = parser.add_argument_group('CSV output parameters')
output_group.add_argument('-o', '--output-file', help='CSV output file (default: ./resolve_output.csv)', default = os.path.abspath(os.path.join(os.getcwd(), 'resolve_output.csv')))

def decode_idna(entry):
    if validators.url(entry):
        return urllib.parse.urlparse(safe_url_string(entry)).hostname
    
    elif validators.domain(entry):
        return urllib.parse.urlparse(safe_url_string('http://'+entry)).hostname

def dns_resolve_entry(netloc):
    ipv4 = None
    ipv6 = None
    
    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = ['9.9.9.9', '149.112.112.112', '1.1.1.1', '8.8.8.8', '1.0.0.1']
    resolver.timeout = 0.3
    resolver.lifetime = 2.0
    
    # IPv4 resolve
    try:
        ipv4_response = resolver.resolve(netloc, 'A')
        if ipv4_response:
            ipv4 = ipv4_response[0].to_text()
    except:
        pass
    
    # IPv6 resolve
    try:
        ipv6_response = resolver.resolve(netloc, 'AAAA')
        if ipv6_response:
            ipv6 = ipv6_response[0].to_text()
    except:
        pass
    
    finally:
        return ipv4, ipv6

def check_entry_type(entry):
    #print("[+] resolving '%s'" % entry)
    entry = entry.strip()
    
    netloc = None
    netloc_idna_decoded = None
    netloc_ipv4 = None
    netloc_ipv6 = None
    
    if validators.url(entry) or validators.domain(entry):
        if validators.url(entry):
            netloc = urllib.parse.urlparse(entry).netloc
            netloc_idna_decoded = decode_idna(entry)
        
        elif validators.domain(entry):
            netloc = entry
            netloc_idna_decoded = decode_idna(entry)
            
        netloc_ipv4, netloc_ipv6 = dns_resolve_entry(netloc_idna_decoded)
        
    elif validators.ip_address.ipv4(entry):
        netloc = netloc_idna_decoded = entry
        netloc_ipv4 = entry
        
    elif validators.ip_address.ipv6(entry):
        netloc = netloc_idna_decoded = entry
        netloc_ipv6 = entry
    
    #print(netloc_idna_decoded, netloc, netloc_ipv4, netloc_ipv6)
    return netloc_idna_decoded, netloc, netloc_ipv4, netloc_ipv6

    
def cymru_resolve(results):
    results_ipv4 = list(set([ x['ipv4'] for x in results.values() if x.get('ipv4')]))
    results_ipv6 = list(set([ x['ipv6'] for x in results.values() if x.get('ipv6')]))
    
    ips_to_resolve = results_ipv4 + results_ipv6
    if not(ips_to_resolve):
        return {}
    
    cymru_resolver = cymruwhois.Client()
    try:
        cymru_lookup = cymru_resolver.lookupmany_dict(ips_to_resolve)
    finally:
        cymru_resolver.disconnect()
    
    return cymru_lookup

def process_input(options):
    
    results = {}
    df_columns = ['netloc_idna_decoded', 'netloc', 'ipv4', 'ipv4_asn', 'ipv4_prefix', 'ipv4_owner', 'ipv4_cc', 'ipv6', 'ipv6_asn', 'ipv6_prefix', 'ipv6_owner', 'ipv6_cc']
    
    with open(options.input_file, mode='r', encoding='utf-8') as fd_input:
        data = [l.strip() for l in fd_input.readlines()]
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
            futs = [ (netloc, executor.submit(functools.partial(check_entry_type, netloc.strip())))
                for netloc in data if netloc ]
    
    for netloc, entry_resolved in futs:
        if entry_resolved.result():
            elem = {}
            
            netloc_idna_decoded, netloc_in, netloc_ipv4, netloc_ipv6 = entry_resolved.result()
            elem['netloc_idna_decoded'] = netloc_idna_decoded
            elem['netloc'] = netloc_in
            elem['ipv4'] = netloc_ipv4
            elem['ipv6'] = netloc_ipv6
            
            if not(netloc in results):
                results[netloc] = elem
    
    try:
        cymru_results = cymru_resolve(results)
    except Exception as exc:
        print(f"[!] Team Cymru lookup failed: {exc}")
        cymru_results = {}
    
    
    for netloc, elem in results.items():
        netloc_ipv4 = elem['ipv4']
        if netloc_ipv4 and (netloc_ipv4 in cymru_results):
            cymru_elem = vars(cymru_results[netloc_ipv4])
            
            elem['ipv4_asn'] = cymru_elem['asn']
            elem['ipv4_prefix'] = cymru_elem['prefix']
            elem['ipv4_owner'] = cymru_elem['owner']
            elem['ipv4_cc'] = cymru_elem['cc']
            
        netloc_ipv6 = elem['ipv6']
        if netloc_ipv6 and (netloc_ipv6 in cymru_results):
            cymru_elem = vars(cymru_results[netloc_ipv6])
            
            elem['ipv6_asn'] = cymru_elem['asn']
            elem['ipv6_prefix'] = cymru_elem['prefix']
            elem['ipv6_owner'] = cymru_elem['owner']
            elem['ipv6_cc'] = cymru_elem['cc']
            
            
        results[netloc] = elem
    
    
    df_results = pd.DataFrame.from_dict(results, orient='index').reindex(columns=df_columns)
    
    df_results = df_results.sort_values(by='netloc_idna_decoded', na_position='last').reset_index(drop=True)
    df_results.to_csv(options.output_file, sep=';', index=False, quoting=csv.QUOTE_ALL, lineterminator='\n', encoding='utf-8-sig')
    
    return
    

def main():
    global parser
    options = parser.parse_args()
    
    if options.input_file:
        process_input(options)
    
    return
    
if __name__ == "__main__" :
    main()