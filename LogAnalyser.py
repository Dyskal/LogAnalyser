from uuid import UUID
from typing import Iterator
from ipaddress import ip_address as check_ip, IPv4Address, IPv6Address
from copy import copy
from sys import argv
from gzip import open as gopen
from os import listdir


class User:
    def __init__(self, username: str, uuid: UUID) -> None:
        self.username: str = username
        self.uuid: UUID = uuid
        self.ip_list: list[IPv4Address | IPv6Address] = []

    def add_ip(self, ip: str) -> None:
        try:
            ip_address: [IPv4Address | IPv6Address] = check_ip(ip)
            if ip_address not in self.ip_list:
                self.ip_list.append(ip_address)
        except ValueError:
            print(f'{ip} does not appear to be an IPv4 or IPv6 address.')

    def __str__(self) -> str:
        out: str = f'{self.username}    {self.uuid.__str__()}    ['
        for i in range(len(self.ip_list)):
            out += self.ip_list[i].__str__()
            if i is not len(self.ip_list) - 1:
                out += '    '
            else:
                pass
        out += ']'
        return out

    def __eq__(self, other) -> bool:
        return isinstance(other, User) and self.uuid == other.uuid

    def __hash__(self) -> int:
        return hash(self.uuid.__str__())


def analyze(content: str) -> None:
    lines_iter: Iterator[str] = iter(content.splitlines())
    for line in lines_iter:
        if 'User Authenticator' in line:
            user: User = User(line.split(' ')[7], UUID(line.split(' ')[9]))
            if user not in users_list:
                users_list.append(user)
            ip_iter: Iterator[str] = copy(lines_iter)

            curr_user: User = users_list[users_list.index(user)]
            for ip_line in ip_iter:
                if curr_user.username + '[' in ip_line:
                    curr_user.add_ip(ip_line.split('/')[2].split(':')[0])
                    break


if __name__ == '__main__':
    dirs_list: list[str] = []
    users_list: list[User] = []
    if len(argv) > 1:
        dirs_list.extend(argv[1::])
    else:
        dirs_list.append('logs')
    for dir in dirs_list:
        for file in listdir(dir):
            if file.endswith('.gz'):
                with gopen(f'{dir}\\{file}', 'rb') as gf:
                    analyze(gf.read().decode())
            else:
                with open(f'{dir}\\{file}', 'r') as f:
                    analyze(f.read())
    for users in users_list:
        print(users)
