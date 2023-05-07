"""
https://blog.detectify.com/2020/11/10/common-nginx-misconfigurations/

daemon off;
worker_processes 1;
error_log /dev/null;
pid {os.path.join(ng.temp_path, 'nginx.pid')};
events {
  worker_connections 8;
  accept_mutex off;
}
http {
  charset utf-8;
  vhost_traffic_status_zone;
  upstream backend {
    server unix:scgi.sock fail_timeout=0;
  }
  server {
    access_log off;
    listen {port} backlog=1;
    location /nginx {
      add_header Content-Type text/plain;
      return 200 '';
    }
    location /nginx/status {
      stub_status on;
      access_log off;
    }
    {ng.temp_subdirs_config_block}
    location /nginx/vts {
      vhost_traffic_status_display;
      vhost_traffic_status_display_format html;
    }
    location / {
      scgi_param REQUEST_METHOD $request_method;
      scgi_param REQUEST_URI $request_uri;
      scgi_param QUERY_STRING $query_string;
      scgi_param CONTENT_TYPE $content_type;
      scgi_param DOCUMENT_URI $document_uri;
      scgi_param DOCUMENT_ROOT $document_root;
      scgi_param SCGI 1;
      scgi_param SERVER_PROTOCOL $server_protocol;
      scgi_param REQUEST_SCHEME $scheme;
      scgi_param HTTPS $https if_not_empty;
      scgi_param REMOTE_ADDR $remote_addr;
      scgi_param REMOTE_PORT $remote_port;
      scgi_param SERVER_PORT $server_port;
      scgi_param SERVER_NAME $server_name;
      scgi_pass backend;
    }
  }
}

daemon off;
worker_processes 1;
% if config.log_level:
error_log /dev/stderr ${config.log_level};
% else:
error_log /dev/null;
% endif
pid ${os.path.join(temp_path, 'nginx.pid')};
events {
  worker_connections 1024;
  accept_mutex off;
  % if LINUX:
  use epoll;
  % elif DARWIN:
  use kqueue;
  % endif
}
http {
  charset utf-8;
  sendfile on;
  tcp_nopush off;
  tcp_nodelay on;
  gzip off;
  gzip_vary off;
  vhost_traffic_status_zone;
  upstream backend {
    % for _ in range(min(config.num_retries, 0) + 1):
    server unix:${socket_file} fail_timeout=0;
    % endfor
  }
  map $status $normal {
    ~^2 1;
    default 0;
  }
  map $status $abnormal {
    ~^2 0;
    default 1;
  }
  log_format access_error
    '$time_iso8601 access_error $remote_addr $remote_user $connection $connection_requests '
    '"$request" $status $body_bytes_sent "$http_referer" "$http_user_agent"'
  ;
  server {
    listen
      ${config.port}
      backlog=${config.listen_backlog}
      % if LINUX:
      deferred
      % endif
    ;
    % if config.log_access_errors:
    access_log /dev/stderr access_error if=$abnormal;
    % else:
    access_log off;
    % endif
    client_max_body_size 1M;
    client_body_buffer_size 64k;
    % for temp_subdir in temp_subdirs:
    ${temp_subdir}_temp_path ${os.path.join(temp_path, temp_subdir)};
    % endfor
    % if config.keepalive_timeout:
    keepalive_timeout ${config.keepalive_timeout};
    % endif
    % if config.keepalive_requests:
    keepalive_requests ${config.keepalive_requests};
    % endif
    location / {
      proxy_set_header Host $host:$server_port;
      proxy_set_header X-Forwarded-Host $server_name;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_redirect off;
      %if config.connect_timeout:
      proxy_connect_timeout ${config.connect_timeout};
      %endif
      %if config.send_timeout:
      proxy_send_timeout ${config.send_timeout};
      %endif
      %if config.read_timeout:
      proxy_read_timeout ${config.read_timeout};
      %endif
      proxy_pass http://backend;
    }
  }
}
"""
import typing as ta

from ... import check
from ... import code
from ... import collections as col
from ... import dataclasses as dc


class ConfigItem(dc.Pure):
    value: str = dc.field(check_type=str)
    block: ta.Optional['ConfigItems'] = dc.field(None, coerce=lambda o: check.isinstance(o, (None, ConfigItems)))

    @classmethod
    def of(cls, *args) -> 'ConfigItem':
        if len(args) == 1:
            [arg] = args
            if isinstance(arg, cls):
                return arg
            elif isinstance(arg, tuple):
                [args] = args
            elif isinstance(arg, str):
                return cls(arg)
        if len(args) == 2:
            arg0, arg1 = args
            if isinstance(arg0, str):
                return cls(arg0, ConfigItems.of(arg1))
        raise TypeError(args)

    def render(self, out: ta.Optional[code.IndentWriter] = None) -> code.IndentWriter:
        out = out or code.IndentWriter()
        if self.block is None:
            out.write(self.value)
        else:
            out.write(self.value + ' {\n')
            with out.indent():
                self.block.render(out)
            out.write('}')
        out.write('\n')
        return out


class ConfigItems(dc.Pure):
    items: ta.Sequence[ConfigItem] = dc.field(coerce=col.seq_of(check.of_isinstance(ConfigItem)))

    def __iter__(self) -> ta.Iterator[ConfigItem]:
        return iter(self.items)

    @classmethod
    def of(cls, arg) -> 'ConfigItems':
        if isinstance(arg, cls):
            return arg
        elif isinstance(arg, ta.Iterable):
            return cls(list(map(ConfigItem.of, arg)))
        else:
            raise TypeError(arg)

    def render(self, out: ta.Optional[code.IndentWriter] = None) -> code.IndentWriter:
        out = out or code.IndentWriter()
        for item in self.items:
            item.render(out)
        return out
