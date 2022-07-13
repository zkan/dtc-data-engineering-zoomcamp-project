# Playground

Credit: https://github.com/openraildata/td-example-python3

## Getting Started

```sh
python -m venv ENV
source ENV/bin/activate
pip install -r requirements.txt
```

For Mac users, see [this
issue](https://github.com/jasonrbriggs/stomp.py/issues/391) if you found this
error below.

```
try_setsockopt() missing 1 required positional argument: 'val'
```

#### Work Around to Fix the Issue Above on Mac

1. Edit the file `ENV/lib/python3.8/site-packages/stomp/transport.py`
1. Search for `def try_setsockopt`.
1. Change the code from
    ```py
    def try_setsockopt(sock, name, fam, opt, val)
    ```

    to

    ```py
    def try_setsockopt(sock, name, fam, opt, val=None)
    ```

## References

* [Quick Start for Confluent
  Platform](https://docs.confluent.io/platform/current/quickstart/ce-docker-quickstart.html)