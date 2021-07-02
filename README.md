# Application

## How to Use

```console
$ docker-compose up -d app
$ docker-compose exec app bash
$ python view/client.py
```

## 構成

modelディレクトリには対話システムの中核となるもの（例えばロジックなど）を書いていく。  
viewディレクトリにはclient.pyがあり、これを実行することで対話システムが起動する。

```
/app
├── README.md
├── model
└── view
    └── client.py
```