#!/usr/bin/python3
# download glibc rpm packages
import re
import os
import requests
import subprocess
from urllib.parse import urlparse

cookie = 'AMCV_945D02BE532957400A490D4C%40AdobeOrg=870038026%7CMCIDTS%7C18487%7CMCMID%7C85113905737299982536015712044188554884%7CMCOPTOUT-1597338271s%7CNONE%7CvVersion%7C5.0.0%7CMCAID%7CNONE; rh_omni_tc=701f2000001Css5AAC; intercom-id-jeuow7ss=963ad8bb-7a2f-4cf5-bac9-5bd605237df3; intercom-session-jeuow7ss=; _redhat_downloads_session=mpX7l6hqkuEL7MPsNDj%2BLypgykGgPZeowtknAVFEf0uvCRB5ecA38CFLihTADPAPvgaXSmDSTp8SMlkXs4bDLLwyYvZOP2Rd%2Bxn3vWlr2EmgwMhunO3FrLKjDBtNoM5PgYqHsLa5AW27aIKJ5zhUp67M7mMD2gfGIeuvfZMsYGTcA9xmj7kZQrZi7RyeoNhKxdjHcuKUfrIMBbJQvw%3D%3D--lRb%2BNJuU%2FRSlU5vX--M4IaWJXnIFE2bLUb2CW3zA%3D%3D; 687975abb031448267d67b8718cb78ea=58781960edc61c72206340fe02d30454; test=cookie; at_check=true; AMCVS_945D02BE532957400A490D4C%40AdobeOrg=1; rh_user=thotypous|Thotypous|P|; rh_locale=en_US; rh_user_id=53640706; rh_sso_session=1; BIGipServer~prod~kcs-webapp-http=259720458.20480.0000; BIGipServer~prod~staticweb-webapp-http=795084042.20480.0000; rh_jwt=eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICItNGVsY19WZE5fV3NPVVlmMkc0UXhyOEdjd0l4X0t0WFVDaXRhdExLbEx3In0.eyJqdGkiOiJjMzc2MmYxZS0xZTZkLTQ5MTYtYTUwOC03ZmE3MTg3NWUyYTciLCJleHAiOjE1OTczMzYxOTQsIm5iZiI6MCwiaWF0IjoxNTk3MzM1Mjk0LCJpc3MiOiJodHRwczovL3Nzby5yZWRoYXQuY29tL2F1dGgvcmVhbG1zL3JlZGhhdC1leHRlcm5hbCIsImF1ZCI6ImN1c3RvbWVyLXBvcnRhbCIsInN1YiI6ImY6NTI4ZDc2ZmYtZjcwOC00M2VkLThjZDUtZmUxNmY0ZmUwY2U2OnRob3R5cG91cyIsInR5cCI6IkJlYXJlciIsImF6cCI6ImN1c3RvbWVyLXBvcnRhbCIsIm5vbmNlIjoiNTlkZDIyYjEtMjliOS00YzIzLWI5ZGEtM2I0NDZhY2M2ODlhIiwiYXV0aF90aW1lIjoxNTk3MzMxMDc0LCJzZXNzaW9uX3N0YXRlIjoiNDcxOTU2MmMtYmM2Ni00NjY4LThjODEtNzQ2YmE0YjAzNGNhIiwiYWNyIjoiMCIsImFsbG93ZWQtb3JpZ2lucyI6WyJodHRwczovL3Byb2QuZm9vLnJlZGhhdC5jb206MTMzNyIsImh0dHBzOi8vd3d3LnJlZGhhdC5jb20iLCJodHRwczovL2FjY2Vzcy5yZWRoYXQuY29tIl0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJhdXRoZW50aWNhdGVkIiwiaWRwX2F1dGhlbnRpY2F0ZWQiLCJwb3J0YWxfbWFuYWdlX3N1YnNjcmlwdGlvbnMiLCJjYW5kbGVwaW5fc3lzdGVtX2FjY2Vzc192aWV3X2VkaXRfYWxsIiwiZXJyYXRhOm5vdGlmaWNhdGlvbl9zdGF0dXNfZW5hYmxlZCIsImVycmF0YTpub3RpZmljYXRpb246ZW5oYW5jZW1lbnQiLCJwb3J0YWxfbWFuYWdlX2Nhc2VzIiwiZXJyYXRhOm5vdGlmaWNhdGlvbjpzZWN1cml0eSIsImVycmF0YTpub3RpZmljYXRpb25fbGV2ZWxfc3lzdGVtLXZpc2libGUiLCJlcnJhdGE6bm90aWZpY2F0aW9uOmJ1Z2ZpeCIsImFkbWluOm9yZzphbGwiLCJ1bWFfYXV0aG9yaXphdGlvbiIsInBvcnRhbF9zeXN0ZW1fbWFuYWdlbWVudCIsImVycmF0YTpub3RpZmljYXRpb25fZGVsaXZlcnlfaW5zdGFudCIsInBvcnRhbF9kb3dubG9hZCJdfSwicmVzb3VyY2VfYWNjZXNzIjp7InJoZC1kbSI6eyJyb2xlcyI6WyJyaHVzZXIiXX0sImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sIlJFREhBVF9MT0dJTiI6InRob3R5cG91cyIsImxhc3ROYW1lIjoiVGhvdHlwb3VzIiwiY291bnRyeSI6IkJSIiwiYWNjb3VudF9udW1iZXIiOiI2ODczNzI5IiwicHJlZmVycmVkX3VzZXJuYW1lIjoidGhvdHlwb3VzIiwiZmlyc3ROYW1lIjoiVGhvdHlwb3VzIiwiYWNjb3VudF9pZCI6IjEzNTY4NzE1IiwidXNlcl9pZCI6IjUzNjQwNzA2Iiwib3JnYW5pemF0aW9uX2lkIjoiMDBEbTAwMDAwMDAxMTZDIiwic2l0ZUlkIjoicmVkaGF0Iiwic2l0ZUlEIjoicmVkaGF0IiwicG9ydGFsX2lkIjoiMDYwNjAwMDAwMDBEMGFmIiwibGFuZyI6ImVuX1VTIiwicmVnaW9uIjoiQlIiLCJlbWFpbCI6InRob3R5cG91c0BnbWFpbC5jb20iLCJSSEFUX0xPR0lOIjoidGhvdHlwb3VzIiwidXNlcm5hbWUiOiJ0aG90eXBvdXMifQ.FwfiPZLhRLixt5QkACRjN7oOQ60uBk3TID9aq1tQjZnY7fsI0BzvQnwtUf15hTG4ZwsS9rxiiMEyMg39SD9pjwHzTM4dCcTlHCBwGwMFcXpQxWBhW7ni5e3Wd8y9nsxU_FdaiPb0W8zbxuIekgIb6dp_yXXOy84H0tUjysK44nhmjHYjbT8aKn99KsTIbLTIgY5wDYlwNcxkke6OXM2Zn8APHzrc-zaNYr3uwxM-XkjByRzgL-3xkQbDrnfbKxgeXcZlSPIGBtABQyH8_lyzd5RT_mRb05Yuge8JRC0Ws_U0Mx_Y_8sNTcL3dBjmevgrhRkz8ZvKPuhnsqLVGw988e8it-S3EYUxIMFZsuY2RFeG6d_zHeDpiKOq3_O5IGKeuxswVMxOz3gF5w1vgg2tZHe54Ykh8WQRAUIVohIUUyhJA2YnSrxl_emfwXPeabduPT46u0jOJwNGDN5nR9PEfY9pTsZPIE8S5Ty2eWw23DLFg-UNBsEjwZTUV1J4BY57m3uuDfAtSaFI1AY0eSxke00bhHP-RR8DbPO5M25nwJkd0RswJULGSKCQFmdxLliTuGz1_T366Umz1xkMhWiCIaTVWVk9Q2LK2ycmzYiACIi9qp_waD_brQeCY7hK0KGayHdpqOFrEZfM_eG20S2vsAxafdFeysOVQSWo7lWu_2A; chrome_session_id=264682|1597331086254'

base_url = "https://access.redhat.com"

pkg_urls = [
    # rhel7
    "https://access.redhat.com/downloads/content/rhel---7/x86_64/2456/glibc/2.17-307.el7.1/x86_64/fd431d51/package",
    "https://access.redhat.com/downloads/content/rhel---7/x86_64/2463/glibc-static/2.17-307.el7.1/x86_64/fd431d51/package",
    # rhel6
    "https://access.redhat.com/downloads/content/rhel---6/x86_64/168/glibc/2.12-1.212.el6_10.3/x86_64/fd431d51/package",
    "https://access.redhat.com/downloads/content/rhel---6/x86_64/166/glibc-static/2.12-1.212.el6_10.3/x86_64/fd431d51/package",
    # rhel5
    "https://access.redhat.com/downloads/content/rhel---5/x86_64/867/glibc/2.5-123.el5_11.3/x86_64/37017186/package",
    "https://access.redhat.com/downloads/content/rhel---5/x86_64/867/glibc-devel/2.5-123.el5_11.3/x86_64/37017186/package",
    # rhel4
    "https://access.redhat.com/downloads/content/rhel---4/x86_64/2013/glibc/2.3.4-2.57/x86_64/db42a60e/package",
    "https://access.redhat.com/downloads/content/rhel---4/x86_64/2013/glibc-devel/2.3.4-2.57/x86_64/db42a60e/package",
]

headers = {'Cookie': cookie}

for pkg_url in pkg_urls:
    r = requests.get(pkg_url, headers=headers)
    r.raise_for_status()
    archs_html, = re.search(r'<label for="arch">Architecture:</label>(.+?)</select>', r.text, re.DOTALL).groups()
    vers_html, = re.search(r'<label for="evr">Version:</label>(.+?)</select>', r.text, re.DOTALL).groups()
    archs = [m.group(1) for m in re.finditer(r'<option[^>]*>\s*(.+?)\s*</option>', archs_html, re.DOTALL)]
    ver_links = [m.group(1) for m in re.finditer(r'<option\s+value="(.+?)"', vers_html, re.DOTALL)]
    for i, ver_link in enumerate(ver_links):
        arr = ver_link.split('/')
        rhel_rel = int(re.match(r'rhel---(\d+)', arr[3]).group(1))
        for arch in archs:
            print("=> RHEL%d (%d/%d) %s" % (rhel_rel, i + 1, len(ver_links), arch))

            arr[8] = arch
            ver_link = '/'.join(arr)

            r = requests.get(base_url + ver_link, headers=headers)
            r.raise_for_status()
            rpm_url = re.search(r'href="(https://access.cdn.redhat.com/.+?)"', r.text).group(1).replace('&amp;', '&')

            print(rpm_url)

            filename = os.path.basename(urlparse(rpm_url).path)

            cwd = 'el%d' % rhel_rel
            os.makedirs(cwd, exist_ok=True)
            subprocess.call(['wget',
                             '-O', os.path.join(cwd, filename),
                             '-c', rpm_url])
