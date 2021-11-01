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
            ip_address: IPv4Address | IPv6Address = check_ip(ip)
            if ip_address not in self.ip_list:
                self.ip_list.append(ip_address)
        except ValueError:
            print(f'{ip} does not appear to be an IPv4 or IPv6 address.')

    def __str__(self) -> str:
        out = [f'{self.username:16}\t{self.uuid.__str__()}\t[']
        for i in range(len(self.ip_list)):
            out.append(f'{self.ip_list[i].__str__():15}')
            if i is not len(self.ip_list) - 1:
                out.append('\t')
        string = ''.join(out).strip() + ']'
        return string

    def __eq__(self, other) -> bool:
        return isinstance(other, User) and self.uuid == other.uuid

    def __hash__(self) -> int:
        return hash(self.uuid.__str__())

    def __lt__(self, other) -> bool:
        return self.username.casefold() < other.username.casefold()


def analyze(content: str, users_list: list[User]) -> None:
    lines_iter: Iterator[str] = iter(content.splitlines())
    for line in lines_iter:
        if 'User Authenticator' in line:
            user: User = User(line.split(' ')[7], UUID(line.split(' ')[9]))

            if user not in users_list:
                users_list.append(user)

            curr_user: User = users_list[users_list.index(user)]
            ip_iter: Iterator[str] = copy(lines_iter)

            for ip_line in ip_iter:
                if curr_user.username + '[' in ip_line:
                    print(ip_line)
                    curr_user.add_ip(ip_line.split('/')[2].split(':')[0])
                    break


def main() -> None:
    folders: list[str] = []
    users_list: list[User] = []
    if len(argv) > 1:
        folders.extend(argv[1:])
    else:
        folders.append('logs')
    for folder in folders:
        for file in listdir(folder):
            if file.endswith('.gz'):
                with gopen(f'{folder}\\{file}', 'rb') as gf:
                    analyze(gf.read().decode(), users_list)
            else:
                with open(f'{folder}\\{file}', 'r') as f:
                    analyze(f.read(), users_list)
    users_list.sort()
    for users in users_list:
        print(users)


if __name__ == '__main__':
    main()
