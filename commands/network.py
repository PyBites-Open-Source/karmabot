from ipaddress import ip_network


def how_many_ips(**kwargs: dict) -> str:
    """Print the number of individual ip addresses that are within the 
    provided network.

    The provided network can be given using either CIDR notation 
    as in '192.168.0.0/24', 
    using a netmask as in '192.168.0.0/255.255.255.0', 
    or using a wildcard mask as in '192.168.0.0/0.0.0.255'.

    EXAMPLE USAGE: '@karmabot howmanyipsin 192.168.0.0/23'

    **If any host bits are set in the network you provide, they will 
    automatically be coerced to zero(s) in order to form a valid network.
    """
    user = kwargs.get('user')
    msg_text = kwargs.get('text') # msg_text should just be the ip network,
                                  # for example, '192.168.0.0/23'

    num_of_ips = ip_network(msg_text, strict=False).num_addresses
    return ('Hello {}!\nThe IP network {} '
            'contains {} IP addresses.'.format(user, msg_text, num_of_ips))


if __name__ == '__main__':
    # standalone test
    user, text = 'bob', '192.168.0.0/23'
    kwargs = dict(user=user,
                  text=text)
    output = how_many_ips(**kwargs)
    print(output)
