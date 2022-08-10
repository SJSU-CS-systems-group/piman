import click
import piman
from dhcp import test_dhcp
from tftp import test_tftp


@click.group()
def cli():
    pass


@cli.command()
def server():
    piman.server()

# adding monitoring command
@cli.command()
def monitoring():
    piman.monitoring()

@cli.command()
@click.argument('switch_address')
@click.argument('interface')
@click.argument('ports', nargs=-1)
def restart(switch_address, interface, ports):
    piman.restart(switch_address, interface, ports)


@cli.command()
@click.argument('switch_address')
@click.argument('interface')
@click.argument('port')
def reinstall(switch_address, interface, port):
    piman.reinstall(switch_address, interface, port)
    
@cli.command()
@click.argument('switch_address')
@click.argument('interface')
@click.argument('port', nargs = -1)
@click.option('--file', default = None)
def mapper(switch_address, interface, port, file):
    piman.mapper(switch_address,interface, port, file)

@cli.command()
@click.argument('name')
@click.argument('configpath')
@click.argument('hostcsvpath')
def config(name, configpath, hostcsvpath):
    piman.config_ui(name, configpath, hostcsvpath)


@cli.command()
def run_dhcp_test():
    test_dhcp.run_test()

@cli.command()
def run_tftp_test():
    test_tftp.run_test()

if __name__ == "__main__":
    cli()
