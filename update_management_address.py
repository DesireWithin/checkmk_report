#!/usr/bin/python
# coding=utf-8
"""
README
This file is to bulk replace "management ip address" with "host ip address",
as there is no batch import function on checkmk.
Please pay attention to below variables, which need to be updated if you are using for a new environment.
e.g.
CHECKMK_API_URL = 'http://192.168.19.8/mysite/check_mk/webapi.py'
AUTOMATION_USER = 'automation'
PASSWORD = 'd5435d51-cfa7-4c18-ae8b-7a924b7eb228'
MASTER_SITE = 'mysite'
"""

import check_mk_web_api

CHECKMK_API_URL = 'http://checkmk.uat.homecreditcfc.cn/checkmk/check_mk/webapi.py'
AUTOMATION_USER = 'automation'
PASSWORD = '23f5e208-bbf5-4aaa-a421-d3f88b8c2d50'
MASTER_SITE = 'checkmk'


class CheckmkAPI(check_mk_web_api.WebApi):
    def __init__(self, check_mk_url, username, secret):
        super(CheckmkAPI, self).__init__(check_mk_url, username, secret)

    def cmk_get_folder_list(self):
        # Print Folder List and save them to a temp dict with numbers.
        # Require input for folder selection.
        all_folders = self.get_all_folders()
        n = 0
        folder_dict = {}
        print('\n# Here is the folder list:')
        for folder_key, folder_value in all_folders.items():
            if folder_key:
                n += 1
                print(n, ".", folder_key)
                folder_dict[n] = folder_key
            else:
                pass
        return folder_dict

    def cmk_select_folder(self):
        # Present folder list to users and return folder name
        while True:
            folders = self.cmk_get_folder_list()
            try:
                path_number = int(input("# Please select your fold number:"))
                folder = folders.get(path_number)
            except Exception:
                print('\n# What the fuck! Number!Digit! Fool!')
                continue
            return folder

    def cmk_print_hosts_info(self, hosts):
        # Print host info in a readable way
        print("\n# Here is the list of hosts in the target folder.")
        for host, attr in hosts.items():
            folder = self.get_folder(attr.get('path'))
            host_site = attr.get('attributes').get('site')
            folder_site = folder.get('attributes').get('site')
            ip = str(attr.get('attributes').get('ipaddress'))
            mgt_ip = str(attr.get('attributes').get('management_address'))
            if host_site:
                # If the option for "monitored on site" is enabled on host configuration
                print('hostname: %s|' % attr.get('hostname').ljust(20),
                      'ip: %s|' % ip.ljust(16),
                      'managementIP: %s|' % mgt_ip.ljust(16),
                      'monitored on site(host):    %s|' % host_site.ljust(10),
                      'folder: %s' % attr.get('path').ljust(20))
            elif folder_site:
                # If the option for "monitored on site" is enabled on folder configuration
                print('hostname: %s|' % attr.get('hostname').ljust(20),
                      'ip: %s|' % ip.ljust(16),
                      'managementIP: %s|' % mgt_ip.ljust(16),
                      'monitored on site(folder):  %s|' % folder_site.ljust(10),
                      'folder: %s' % attr.get('path').ljust(20))
            else:
                # If host is added in default way
                print('hostname: %s|' % attr.get('hostname').ljust(20),
                      'ip: %s|' % ip.ljust(16),
                      'managementIP: %s|' % mgt_ip.ljust(16),
                      'monitored on site(default): %s|' % MASTER_SITE.ljust(10),
                      'folder: %s' % attr.get('path').ljust(20))

    def cmk_get_hosts_info(self):
        # Print out host list information for users to verify the targets for edit.
        while True:
            path = self.cmk_select_folder()
            hosts = self.get_hosts_by_folder(path)
            if hosts.keys():
                self.cmk_print_hosts_info(hosts)
                print('\n# Would you like to edit the hosts attribute in this folder:', path)
                confirm = input('\n# yes/no/quit:')
                if confirm.lower() == 'yes':
                    return hosts
                elif confirm.lower() == 'no':
                    continue
                elif confirm.lower() == 'quit':
                    print('\n# Byebye...')
                    return
                else:
                    print('\n# wrong input!')
            else:
                print('\n# NOTE: No hosts are found in this folder, please double check.')
                continue

    def cmk_update_ip_to_mgtip(self):
        # Update management IP address field with host ip address and clear host ip afterwards
        while True:
            hosts = self.cmk_get_hosts_info()
            if hosts:
                print('\n# WARNING!!!'
                      '# This is to replace management IP address with Host IP address, and clear IP address afterwards.')
                signal = input("\n# 'yes' to continue, 'no' to cancel:'")
                if signal.lower() == 'yes':
                    for host, attr in hosts.items():
                        hostname = str(attr.get('hostname'))
                        try:
                            ip = attr['attributes']['ipaddress']
                            # Update management_address with ip address
                            self.edit_host(hostname, management_address=ip)
                            # Uncheck IP Address Field
                            self.edit_host(hostname, unset_attributes=['ipaddress'])
                        except KeyError as e:
                            print('# INFO: Attribute Key %s is not found in %s; skipping..' % (e, hostname))
                            continue

                    try:
                        # Activate changes in checkmk.
                        print('# Activating changes...')
                        self.activate_changes()
                    except Exception as e:
                        print('\n# Exception %s' % e)

                    print('\n# Job is done.')
                    print('\n# NOTE: Please go to WEB UI to verify the completed changes.')
                    print('# Or you may restart this python script again and select the same folder to view the results.')
                    return

                elif signal.lower() == 'no':
                    print('\n# Exiting...Byebye')
                    break
                else:
                    print('\n# Wrong Input!')
                    continue
            else:
                print('\n# Exiting...')
                return


if __name__ == '__main__':
    try:
        CHECKMK = CheckmkAPI(CHECKMK_API_URL, username=AUTOMATION_USER, secret=PASSWORD)
        CHECKMK.cmk_update_ip_to_mgtip()
    except KeyboardInterrupt:
        print('\n\n# See you...')
