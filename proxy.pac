function FindProxyForURL(url, host) {
    // Direct connection for localhost and local network
    if (isPlainHostName(host) ||
        shExpMatch(host, "127.0.0.1") ||
        shExpMatch(host, "localhost") ||
        isInNet(dnsResolve(host), "192.168.0.0", "255.255.0.0") ||
        isInNet(dnsResolve(host), "172.16.0.0",  "255.240.0.0") ||
        isInNet(dnsResolve(host), "10.0.0.0",    "255.0.0.0")) {
        return "DIRECT";
    }

    // For all other traffic, use the Tor SOCKS proxy
    return "SOCKS 127.0.0.1:9050";
}
