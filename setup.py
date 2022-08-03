from setuptools import setup, find_packages
setup(
    name='ms_rrp',
    version='0.11',
    packages=find_packages(),
    install_requires=[
        'rpc @ git+https://github.com/vphpersson/rpc.git#egg=rpc',
        'msdsalgs @ git+https://github.com/vphpersson/msdsalgs.git#egg=msdsalgs',
        'ndr @ git+https://github.com/vphpersson/ndr.git#egg=ndr',
        'smb @ git+https://github.com/vphpersson/smb.git#egg=smb'
    ]
)
