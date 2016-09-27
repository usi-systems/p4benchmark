header tcp_t tcp;

parser parse_tcp {
    extract(tcp);
    return ingress;
}
