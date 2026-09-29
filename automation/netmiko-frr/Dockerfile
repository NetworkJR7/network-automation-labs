FROM frrouting/frr:latest

RUN apk add --no-cache openssh \
    && ssh-keygen -A \
    && adduser -D netops \
    && echo 'netops:netops123' | chpasswd \
    && addgroup netops frrvty \
    && echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config

CMD ["/bin/sh", "-c", "/usr/sbin/sshd && /usr/lib/frr/docker-start"]
