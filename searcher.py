import subprocess
import requests
import tempfile
import os

def do(keywords):
    k = tempfile.NamedTemporaryFile(suffix=".txt")
    r = tempfile.NamedTemporaryFile(suffix=".txt")
    p = tempfile.NamedTemporaryFile(suffix=".txt")

    with open(k.name, 'w') as kw:
        kw.write("\n".join(x.strip() for x in keywords))
    kw.close()

    cmd = f'python3 opensquat.py -o {r.name} -k {k.name}'
    subprocess.call(cmd, shell=True)

    matches = [line.decode("utf-8").strip() for line in r.readlines()]

    if (len(matches) == 0):
        return

    cmd = f'python3 opensquat.py -o {p.name} -k {k.name} --portcheck'
    subprocess.call(cmd, shell=True)

    ports = [line.decode("utf-8").strip() for line in p.readlines()]

    lines = []

    print(matches)
    print(ports)
    for x in matches:
        if x in ports:
            domain = str(x).replace(os.linesep, '')
        else:
            domain = str(x).replace(os.linesep, '') + ' ❌'

        x = str(x).replace(os.linesep, '')

        registrar = ''
        abuse = ''
        try:
            rdap = requests.get(f"http://rdap.org/domain/{x}").json()
            for entity in rdap["entities"]:
                if "registrar" in entity["roles"]:
                    registrar = '\t' + entity["vcardArray"][1][1][3]
                    for subEntities in entity["entities"]:
                        if "abuse" in subEntities["roles"]:
                            for vcard in subEntities["vcardArray"][1]:
                                if "tel" in vcard[0] and vcard[3] and vcard[3] != 'tel:':
                                    abuse += '\t' + vcard[3]
                                if "email" in vcard[0] and vcard[3]:
                                    abuse += '\t' + vcard[3]
        except Exception as e:
            print(e)

        # nameservers = ''
        # try:
        #     data = requests.get(
        #                 f"https://www.whoisxmlapi.com/whoisserver/DNSService?apiKey={os.getenv('WHO_IS_API_KEY')}&domainName={x}&type=_all&outputFormat=json"
        #             ).json()
        #     records = data["DNSData"]["dnsRecords"]
        #     nameservers = []
        #     for record in records:
        #         if record["dnsType"] == "NS":
        #             nameservers.append(record["target"])
        #     nameservers = "\t".join(nameservers)
        # except Exception as e:
        #     print(e)

        # lines.append(f"{domain}\t{nameservers}\n")

        lines.append(f"- {domain}{registrar}{abuse}\n")

    r.close()
    k.close()
    p.close()

    return lines