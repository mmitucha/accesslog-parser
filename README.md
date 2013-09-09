accesslog-parser
=================

Set of simple utilities created for reading and parsing **nginx** `access.log` file.

### Components: ###
* `reader` - python like `tail` implementation. It allows continuous reading by storing file's inode and last reading end position.
* `parse` - per line parsing, inspired by [this article](http://www.seehuhn.de/blog/52)


### Data Format ###
Log format for parsing must be in [Common Log Format](https://en.wikipedia.org/wiki/Common_Log_Format).

For **nginx** web server, it is [this](http://wiki.nginx.org/HttpLogModule) configuration option:

    log_format main '$remote_addr - $remote_user [$time_local] '
                '"$request" $status $body_bytes_sent "$http_referer" '
                '"$http_user_agent" "$http_x_forwarded_for"' ;  


Example
=======

    from parse import parse
    from reader import Read

    r = Read(follow="/var/www/nginx/access.log")

    # read to the end of file
    #  'status_save=True' means it will remember position of last reading
    lines = r.read(status_save=True)    

    # per line parsing
    parsed_data = []
    [parsed_data.append(parse(line)) for line in lines]
