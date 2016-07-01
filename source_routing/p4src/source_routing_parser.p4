#define PORT_DEPTH 700

header easy_route_t easy_route;
header port_t ports[PORT_DEPTH];
metadata easy_route_metadata_t ingress_meta;

parser parse_easy_route {
    extract(easy_route);
    set_metadata(ingress_meta.num_port, easy_route.num_port);
    return select(latest.num_port) {
        0 : ingress;
        default : parse_port;
    }
}

parser parse_port {
    extract(ports[next]);
    set_metadata(ingress_meta.num_port, ingress_meta.num_port - 1);
    return select(ingress_meta.num_port) {
        0 : ingress;
        default : parse_port;
    }
}