from setuptools import setup, find_packages
setup(
    name='ms_rrp',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'rpc @ git+ssh://git@github.com/vphpersson/rpc.git#egg=rpc',
        'msdsalgs @ git+ssh://git@github.com/vphpersson/msdsalgs.git#egg=msdsalgs',
        'ndr @ git+ssh://git@github.com/vphpersson/ndr.git#egg=ndr',
        'smb @ git+ssh://git@github.com/vphpersson/smb.git#egg=smb'
    ]
)
